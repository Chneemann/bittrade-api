from rest_framework import serializers
from .models import CoinTransaction, CoinHolding, Coin
from django.core.exceptions import ValidationError

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

    def validate(self, data):
        user = self.context['request'].user
        coin = self.context.get('coin')
        try:
            instance = CoinTransaction(
                user=user,
                coin=coin,
                transaction_type=data['transaction_type'],
                amount=data['amount'],
                price_per_coin=data['price_per_coin']
            )
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        coin = self.context['coin']
        transaction = CoinTransaction.objects.create(user=user, coin=coin, **validated_data)
        return transaction
    
class CoinHoldingSerializer(serializers.ModelSerializer):
    coin = BaseCoinSerializer(read_only=True)
    not_holding = serializers.SerializerMethodField()

    class Meta:
        model = CoinHolding
        fields = ['id', 'coin', 'amount', 'average_buy_price', 'not_holding']
    
    def get_not_holding(self, obj):
        return getattr(obj, 'not_holding', False)