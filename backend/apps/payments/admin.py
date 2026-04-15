from django.contrib import admin
from .models import Payment, PaymentAuditLog, VendorWallet, WithdrawalRequest


class PaymentAuditLogInline(admin.TabularInline):
    model = PaymentAuditLog
    extra = 0
    readonly_fields = ['event', 'old_status', 'new_status', 'payload', 'actor_ip', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'provider', 'amount', 'status', 'phone_number', 'created_at']
    list_filter = ['provider', 'status']
    search_fields = ['transaction_id', 'user__phone_number', 'external_reference']
    readonly_fields = ['transaction_id', 'raw_request', 'raw_response', 'webhook_payload', 'created_at', 'updated_at']
    inlines = [PaymentAuditLogInline]

    def has_add_permission(self, request):
        return False


@admin.register(PaymentAuditLog)
class PaymentAuditLogAdmin(admin.ModelAdmin):
    list_display = ['payment', 'event', 'old_status', 'new_status', 'actor_ip', 'created_at']
    list_filter = ['event']
    readonly_fields = list_display + ['payload']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False  # Journal immuable — aucune suppression autorisée


@admin.register(VendorWallet)
class VendorWalletAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'balance', 'total_earned', 'total_withdrawn', 'updated_at']
    readonly_fields = ['total_earned', 'total_withdrawn', 'updated_at']
    search_fields = ['vendor__phone_number']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'amount', 'provider', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'provider']
    readonly_fields = ['wallet', 'amount', 'phone_number', 'provider', 'created_at']
