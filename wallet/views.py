from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import Wallet

class WalletMixin:
    def get_wallet(self, request):
        try:
            return Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return None

    def wallet_not_found_response(self):
        return Response({'detail': 'Wallet not found.'}, status=status.HTTP_404_NOT_FOUND)

    def parse_amount(self, request):
        try:
            amount = Decimal(request.data['amount'])
            if amount <= 0:
                raise ValueError("Amount must be positive.")
            return amount, None
        except (KeyError, TypeError, ValueError):
            return None, Response(
                {'detail': 'Invalid or missing amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class MyWalletView(WalletMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        wallet = self.get_wallet(request)
        if wallet is None:
            return self.wallet_not_found_response()

        data = {'id': str(wallet.id), 'balance': float(wallet.balance)}
        return Response(data, status=status.HTTP_200_OK)

class DepositWalletView(WalletMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        wallet = self.get_wallet(request)
        if wallet is None:
            return self.wallet_not_found_response()

        amount, error_response = self.parse_amount(request)
        if error_response:
            return error_response

        wallet.balance += amount
        wallet.save()
        return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)

class WithdrawWalletView(WalletMixin, APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        wallet = self.get_wallet(request)
        if wallet is None:
            return self.wallet_not_found_response()

        amount, error_response = self.parse_amount(request)
        if error_response:
            return error_response

        if wallet.balance < amount:
            return Response(
                {'detail': 'Insufficient funds.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        wallet.balance -= amount
        wallet.save()
        return Response({'balance': wallet.balance}, status=status.HTTP_200_OK)