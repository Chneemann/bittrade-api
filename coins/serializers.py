from rest_framework import serializers
from .models import CoinTransaction

class CoinTransactionSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(source='coin.slug', read_only=True)

    class Meta:
        model = CoinTransaction
        fields = ['id', 'slug', 'transaction_type', 'amount', 'price_per_coin', 'created_at']