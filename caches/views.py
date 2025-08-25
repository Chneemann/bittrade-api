from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from config.celery import app  
from coins.models import Coin

class QueueCoinCacheView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        coins = Coin.objects.filter(is_active=True)
        results = []

        for coin in coins:
            try:
                app.send_task('caches.tasks.cache_coin_data', args=[coin.slug])
                results.append(f"{coin.slug} queued")
            except Exception as e:
                results.append(f"{coin.slug} failed: {str(e)}")

        return Response({"results": results}, status=status.HTTP_200_OK)