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
        results = []

        for coin in Coin.objects.filter(is_active=True):
            try:
                task = app.send_task('caches.tasks.cache_coin_data', args=[coin.slug])
                task.get(timeout=30)
                results.append(f"{coin.slug} cached successfully")
            except Exception as e:
                results.append(f"{coin.slug} failed: {str(e)}")

        return Response({"results": results}, status=status.HTTP_200_OK)