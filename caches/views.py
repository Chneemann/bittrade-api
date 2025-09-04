from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils.timezone import now

from config.celery import app
from coins.models import Coin

TASKS = {
    "data": "caches.tasks.cache_coin_data",
    "chart": "caches.tasks.cache_coin_chart",
}

class CoinCacheBase(APIView):
    """
    Helper function: Start task and return result
    """
    permission_classes = [IsAuthenticated]

    def run_task(self, slug: str, kind: str, args: list):
        """
        Run a Celery task and store timestamp in Redis.
        If `days` is given (for chart), the timestamp key follows the same pattern:
        "chart:<slug>:<days>:timestamp"
        """
        try:
            task_name = TASKS[kind]
            task = app.send_task(task_name, args=args)
            task.get(timeout=30)

            timestamp = int(now().timestamp() * 1000)

            if kind == "chart" and len(args) > 1:
                days = args[1]
                cache.set(f"chart:{slug}:{days}:timestamp", timestamp, None)
            else:
                cache.set(f"coin:{slug}:timestamp", timestamp, None)

            return f"{slug} {kind} cached successfully"
        except Exception as e:
            return f"{slug} {kind} failed: {str(e)}"

class CoinCacheView(CoinCacheBase):
    """
    GET: return cached coin data for all active coins
    POST: refresh all active coins (data + chart 1d)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coins = Coin.objects.filter(is_active=True)
        results = {}

        chart_days = [1, 7, 30, 180, 365]

        for coin in coins:
            redis_key = f"coin:{coin.slug}"
            cached_data = cache.get(redis_key)
            if cached_data:
                timestamp = cache.get(f"coin:{coin.slug}:timestamp")

                cached_charts = {}
                for days in chart_days:
                    chart_key = f"chart:{coin.slug}:{days}"
                    chart_data = cache.get(chart_key)
                    if chart_data:
                        chart_timestamp = cache.get(f"chart:{coin.slug}:{days}:timestamp")
                        cached_charts[str(days)] = {
                            "data": chart_data,
                            "timestamp": chart_timestamp,
                        }

                results[coin.slug] = {
                    "data": cached_data,
                    "charts": cached_charts,
                    "timestamp": timestamp,
                }

        return Response(results, status=status.HTTP_200_OK)

    def post(self, request):
        coins = Coin.objects.filter(is_active=True)
        results = []
        for coin in coins:
            results.append(self.run_task(coin.slug, "data", [coin.slug]))
            results.append(self.run_task(coin.slug, "chart", [coin.slug, "1"]))
        return Response({"results": results}, status=status.HTTP_200_OK)

class SingleCoinCacheView(CoinCacheBase):
    """
    Cache a single coin's chart.
    URL: /api/coins/cache/chart/<slug>
    Optional query param: ?days=7
    Allowed: 1, 7, 30, 180, 365
    """
    ALLOWED_DAYS = [1, 7, 30, 180, 365]
    DEFAULT_DAYS = 1

    def post(self, request, *args, **kwargs):
        kind = kwargs.get("kind")
        slug = kwargs.get("slug")

        if kind not in TASKS:
            return Response(
                {"error": "Invalid kind. Use 'data' or 'chart'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        args_list = [slug]
        if kind == "chart":
            days = request.query_params.get("days", str(self.DEFAULT_DAYS))
            try:
                days = int(days)
            except ValueError:
                return Response({"error": "Invalid 'days' parameter"}, status=400)

            if days not in self.ALLOWED_DAYS:
                return Response(
                    {"error": f"Invalid 'days'. Allowed: {self.ALLOWED_DAYS}"},
                    status=400,
                )
            args_list.append(str(days))

        result = self.run_task(slug, kind, args_list)
        return Response({"result": result}, status=200)