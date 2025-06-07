from rest_framework import serializers
from .models import CoinTransaction, CoinHolding, Coin

class BaseCoinSerializer(serializers.ModelSerializer):
    name = serializers.CharField(read_only=True)
    symbol = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Coin
        fields = ['name', 'symbol', 'slug']

class CoinTransactionSerializer(serializers.ModelSerializer):
    coin = BaseCoinSerializer(read_only=True)

    class Meta:
        model = CoinTransaction
        fields = ['id', 'coin', 'transaction_type', 'amount', 'price_per_coin', 'created_at']

class CoinHoldingSerializer(serializers.ModelSerializer):
    coin = BaseCoinSerializer(read_only=True)

    class Meta:
        model = CoinHolding
        fields = ['id', 'coin', 'amount', 'average_buy_price']