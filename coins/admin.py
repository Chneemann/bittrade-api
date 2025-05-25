from django.contrib import admin
from .models import Coin, CoinHolding, CoinTransaction

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_active']
    readonly_fields = ['name', 'symbol']

    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(CoinHolding)
class CoinHoldingAdmin(admin.ModelAdmin):
    list_display = ['user', 'coin', 'amount', 'average_buy_price']
    readonly_fields = ['user', 'coin', 'amount', 'average_buy_price']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'coin', 'transaction_type', 'amount', 'price_per_coin', 'created_at']
    readonly_fields = ['created_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['user', 'coin']
        return self.readonly_fields 