from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from coins.serializers import CoinHoldingSerializer, CoinTransactionSerializer
from .models import Coin, CoinHolding, CoinTransaction

class CoinView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        coins = Coin.objects.filter(is_active=True)
        data = [{"name": coin.name, "symbol": coin.symbol} for coin in coins]
        return Response(data, status=status.HTTP_200_OK)

class MyCoinHoldingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        holdings = CoinHolding.objects.filter(user=request.user)
        serializer = CoinHoldingSerializer(holdings, many=True)
        return Response(serializer.data)
    
class MyCoinHoldingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, coin_id):
        try:
            coin = Coin.objects.get(name__iexact=coin_id)
        except Coin.DoesNotExist:
            return Response({'detail': 'Coin not found.'}, status=status.HTTP_404_NOT_FOUND)

        holding = CoinHolding.objects.filter(user=request.user, coin=coin).first()

        if not holding:
            empty_holding = CoinHolding(
                coin=coin,
                amount=0,
                average_buy_price=0
            )
            empty_holding.not_holding = True
            serializer = CoinHoldingSerializer(empty_holding)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = CoinHoldingSerializer(holding)
        return Response(serializer.data)
    
class MyCoinTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = CoinTransaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = CoinTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class MyCoinTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, coin_id):
        try:
            coin = Coin.objects.get(name__iexact=coin_id)
        except Coin.DoesNotExist:
            return Response({'detail': 'Coin not found.'}, status=status.HTTP_404_NOT_FOUND)

        transactions = CoinTransaction.objects.filter(user=request.user, coin=coin).order_by('-created_at')
        serializer = CoinTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request, coin_id):
        try:
            coin = Coin.objects.get(name__iexact=coin_id)
        except Coin.DoesNotExist:
            return Response({'detail': 'Coin not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CoinTransactionSerializer(data=request.data, context={'request': request, 'coin': coin})
        serializer.is_valid(raise_exception=True)
        transaction = serializer.save()
        response_serializer = CoinTransactionSerializer(transaction, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
