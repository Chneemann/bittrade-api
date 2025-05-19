from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group

class UserAdmin(admin.ModelAdmin):
    exclude = ('uId',)
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'is_online', 'is_active')
    list_filter = ('is_online', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')

    fieldsets = (
        (None, {
            'fields': ['first_name', 'last_name', 'email', 'password']
        }),
        ('Additional Info', {
            'fields': ['is_online', 'last_login', 'joined_at']
        }),
        ('Permissions', {
            'fields': ['is_active', 'is_staff', 'is_superuser',] 
        }),
    )

    readonly_fields = ('last_login', 'joined_at')

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)