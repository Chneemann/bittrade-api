from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import PasswordResetConfirmSerializer, UserLoginSerializer, UserRegisterSerializer, UserUpdateSerializer, PasswordResetRequestSerializer
from .utils import create_token_response, get_transaction_sum, ratelimit_response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from coins.models import CoinTransaction, CoinHolding
from rest_framework import status
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework import generics

from decimal import Decimal
from wallets.models import Wallet

User = get_user_model()

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(ratelimit_response(rate='10/m', method='GET'))
    def get(self, request, *args, **kwargs):
        user = request.user

        purchase_count = CoinTransaction.objects.filter(
            user=user, transaction_type='buy'
        ).count()
        sale_count = CoinTransaction.objects.filter(
            user=user, transaction_type='sell'
        ).count()
        held_coins_count = CoinHolding.objects.filter(
            user=user, amount__gt=0
        ).count()

        wallet = Wallet.objects.filter(user=user).first()

        if wallet:
            deposits_fiat = get_transaction_sum(wallet, 'deposit', 'fiat')
            withdrawals_fiat = get_transaction_sum(wallet, 'withdrawal', 'fiat')
            deposits_total = get_transaction_sum(wallet, 'deposit')
            withdrawals_total = get_transaction_sum(wallet, 'withdrawal')
            balance = deposits_total - withdrawals_total
        else:
            deposits_fiat = withdrawals_fiat = balance = Decimal('0')

        return Response({
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "verified": user.verified,
            "coin_purchases": purchase_count,
            "coin_sales": sale_count,
            "held_coins": held_coins_count,
            "wallet_deposits": float(deposits_fiat),
            "wallet_withdrawals": float(withdrawals_fiat),
            "wallet_balance": float(balance),
        })

class MeUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            email_changed = serializer.is_email_changed()
            user = serializer.save()

            return Response({
                "username": user.username,
                "email": user.email,
                "unconfirmed_email": user.unconfirmed_email,
                "verified": user.verified,
                "email_verification_required": email_changed
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        return create_token_response(user)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(status=200)
        response.delete_cookie('auth_token', path='/', domain=None)
        return response

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit_response(rate='5/m', method='POST'))
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "If an account with that email exists, a password reset link has been sent."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Password has been reset."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        uidb64 = request.query_params.get("uid")
        token = request.query_params.get("token")

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.email = user.unconfirmed_email
            user.unconfirmed_email = None
            user.verified = True
            user.save()
            return Response({"detail": "Email successfully confirmed."})
        else:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
         