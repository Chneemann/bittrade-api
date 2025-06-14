from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet

class MyWalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            wallet = Wallet.objects.get(user=request.user)
        except Wallet.DoesNotExist:
            return Response(
                {'detail': 'Wallet not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        data = {
            'id': str(wallet.id),
            'balance': float(wallet.balance)
        }
        return Response(data, status=status.HTTP_200_OK)