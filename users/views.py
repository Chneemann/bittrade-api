from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import LoginSerializer
from .utils import create_token_response, ratelimit_response
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from coins.models import Coin, CoinTransaction, CoinHolding
from coins.serializers import CoinTransactionSerializer, CoinHoldingSerializer
from rest_framework import status

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit_response(rate='10/m', method='GET'))
    def get(self, request, *args, **kwargs):
        user = request.user

        purchase_count = CoinTransaction.objects.filter(user=user, transaction_type='buy').count()
        sale_count = CoinTransaction.objects.filter(user=user, transaction_type='sell').count()
        held_coins_count = CoinHolding.objects.filter(user=user, amount__gt=0).count()

        return Response({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "coin_purchases": purchase_count,
            "coin_sales": sale_count,
            "held_coins": held_coins_count,
        })
    
class MyHoldingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        holdings = CoinHolding.objects.filter(user=request.user)
        serializer = CoinHoldingSerializer(holdings, many=True)
        return Response(serializer.data)
    
class MyCoinHoldingsView(APIView):
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
    
class MyTransactionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        transactions = CoinTransaction.objects.filter(user=request.user).order_by('-created_at')
        serializer = CoinTransactionSerializer(transactions, many=True)
        return Response(serializer.data)

class MyCoinTransactionsView(APIView):
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

class LoginView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @method_decorator(ratelimit_response(rate='5/m', method='POST'))
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({
                'error': 'validation_error',
                'message': 'Invalid input data.'
            }, status=400)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)

        if not user:
            return Response({
                'error': 'authentication_failed',
                'message': 'Email or password is incorrect.'
            }, status=401)

        if not user.is_active:
            return Response({
                'error': 'account_inactive',
                'message': 'Account inactive. Please check your email.'
            }, status=403)

        return create_token_response(user)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(status=200)
        response.delete_cookie('auth_token', path='/', domain=None)
        return response