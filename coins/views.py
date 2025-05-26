from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Coin

class CoinView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        coins = Coin.objects.filter(is_active=True)
        data = [{"name": coin.name, "symbol": coin.symbol} for coin in coins]
        return Response(data, status=status.HTTP_200_OK)