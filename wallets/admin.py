from django.contrib import admin
from .models import Wallet, WalletTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

class WalletTransactionInline(admin.TabularInline):
    model = WalletTransaction
    readonly_fields = ['transaction_type', 'transaction_source', 'amount', 'created_at']
    can_delete = False
    extra = 0
    
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_balance']
    list_filter = []
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['current_balance']
    ordering = ['user__username']
    inlines = [WalletTransactionInline]

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet_user', 'transaction_type', 'transaction_source', 'amount', 'created_at']
    list_filter = ['transaction_type', 'transaction_source', 'created_at']
    search_fields = ['wallet__user__username', 'wallet__user__email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_select_related = ['wallet__user']

    @admin.display(description='User', ordering='wallet__user__username')
    def wallet_user(self, obj):
        return obj.wallet.user