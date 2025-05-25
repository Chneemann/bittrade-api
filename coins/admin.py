from django.contrib import admin
from .models import Coin, CoinHolding, CoinTransaction

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol']


@admin.register(CoinHolding)
class CoinHoldingAdmin(admin.ModelAdmin):
    list_display = ['user', 'coin', 'amount', 'average_buy_price']
    readonly_fields = ['user', 'coin', 'amount', 'average_buy_price']


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'coin', 'transaction_type', 'amount', 'price_per_coin', 'created_at']