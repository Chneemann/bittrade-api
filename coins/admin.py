from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Coin, CoinHolding, CoinTransaction

User = get_user_model()

def format_decimal(value, max_decimals=6):
    if value is None:
        return ''
    formatted = f"{value:.{max_decimals}f}".rstrip('0').rstrip('.')
    return formatted if formatted else '0'

class DecimalFormatAdminMixin:
    def _format_decimal_field(self, value, max_decimals=6):
        return format_decimal(value, max_decimals)

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ['name', 'symbol', 'is_active']
    readonly_fields = ['name', 'symbol']

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CoinHolding)
class CoinHoldingAdmin(DecimalFormatAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'coin', 'formatted_amount', 'formatted_average_buy_price']
    list_select_related = ('user', 'coin')
    list_filter = ('coin', 'user')
    ordering = ('user', 'coin')
    readonly_fields = [field.name for field in CoinHolding._meta.fields]  # evtl. fix statt dynamisch

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description='Amount')
    def formatted_amount(self, obj):
        return self._format_decimal_field(obj.amount)

    @admin.display(description='Average buy price')
    def formatted_average_buy_price(self, obj):
        return self._format_decimal_field(obj.average_buy_price)

@admin.register(CoinTransaction)
class CoinTransactionAdmin(DecimalFormatAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'coin', 'transaction_type', 'formatted_amount', 'formatted_price_per_coin', 'created_at']
    readonly_fields = ['created_at']
    list_select_related = ('user', 'coin')
    list_filter = ('transaction_type', 'coin', 'user')
    ordering = ('-created_at',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['user', 'coin']
        return self.readonly_fields

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description='Amount')
    def formatted_amount(self, obj):
        return self._format_decimal_field(obj.amount)

    @admin.display(description='Price per coin')
    def formatted_price_per_coin(self, obj):
        return self._format_decimal_field(obj.price_per_coin)