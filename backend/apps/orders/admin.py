from django.contrib import admin
from .models import Order, OrderItem, GroupBuySession, GroupBuyParticipation


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['reference', 'client', 'order_type', 'status', 'total_amount', 'delivery_city', 'created_at']
    list_filter = ['status', 'order_type', 'delivery_city']
    search_fields = ['reference', 'client__phone_number', 'delivery_phone']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    inlines = [OrderItemInline]


class GroupBuyParticipationInline(admin.TabularInline):
    model = GroupBuyParticipation
    extra = 0
    readonly_fields = ['joined_at']


@admin.register(GroupBuySession)
class GroupBuySessionAdmin(admin.ModelAdmin):
    list_display = ['product', 'organizer', 'status', 'current_quantity', 'target_quantity', 'progress_percent', 'expires_at']
    list_filter = ['status']
    readonly_fields = ['current_quantity', 'created_at', 'confirmed_at']
    inlines = [GroupBuyParticipationInline]
