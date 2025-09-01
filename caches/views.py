from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from config.celery import app  
from coins.models import Coin

class CoinCacheView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        coins = Coin.objects.filter(is_active=True)
        results = {}

        for coin in coins:
            redis_key = f"coin:{coin.slug}"
            cached = cache.get(redis_key)
            if cached:
                results[coin.slug] = cached 
                
        return Response(results, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        coins = Coin.objects.filter(is_active=True)
        tasks = [
            (coin.slug, kind, app.send_task(task, args=args))
            for coin in coins
            for kind, task, args in [
                ("data", "caches.tasks.cache_coin_data", [coin.slug]),
                ("chart", "caches.tasks.cache_coin_chart", [coin.slug, "30"]),
            ]
        ]

        results = []
        for slug, kind, task in tasks:
            try:
                task.get(timeout=30)
                results.append(f"{slug} {kind} cached successfully")
            except Exception as e:
                results.append(f"{slug} {kind} failed: {str(e)}")

        return Response({"results": results}, status=status.HTTP_200_OK)