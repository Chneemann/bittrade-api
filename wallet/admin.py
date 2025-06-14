from django.contrib import admin
from .models import Wallet
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')
    search_fields = ('user__username',)
    list_filter = ('balance',)
    ordering = ('user__username',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=False, is_superuser=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
