from rest_framework import serializers
from .models import WalletTransaction

class WalletTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = WalletTransaction
        fields = ['id', 'transaction_type', 'transaction_source', 'amount', 'created_at']