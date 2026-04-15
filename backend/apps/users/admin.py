from django.contrib import admin
from .models import User, OTPLog


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'role', 'is_phone_verified', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_phone_verified', 'city']
    search_fields = ['phone_number', 'first_name', 'last_name', 'email']
    readonly_fields = ['date_joined', 'updated_at']
    fieldsets = (
        ('Identité', {'fields': ('phone_number', 'email', 'first_name', 'last_name', 'avatar')}),
        ('Rôle & Statut', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_phone_verified', 'mfa_enabled')}),
        ('Localisation (BF)', {'fields': ('city', 'district', 'landmark')}),
        ('Dates', {'fields': ('date_joined', 'updated_at')}),
    )


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'purpose', 'is_used', 'created_at', 'used_at', 'ip_address']
    list_filter = ['purpose', 'is_used']
    search_fields = ['user__phone_number']
    readonly_fields = ['user', 'purpose', 'code_hash', 'created_at', 'used_at', 'ip_address']

    def has_add_permission(self, request):
        return False  # Journal immuable

    def has_change_permission(self, request, obj=None):
        return False
