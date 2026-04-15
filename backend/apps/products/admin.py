from django.contrib import admin
from .models import Category, Product, ProductImage, ProductReview


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'category', 'unit_price', 'bulk_price', 'stock', 'status', 'is_essential']
    list_filter = ['status', 'is_essential', 'category']
    search_fields = ['name', 'vendor__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Informations', {'fields': ('vendor', 'category', 'name', 'slug', 'description', 'unit', 'status', 'is_essential')}),
        ('Prix & Stock', {'fields': ('unit_price', 'bulk_price', 'bulk_min_quantity', 'stock', 'weight_kg')}),
        ('Commission', {'fields': ('commission_rate',)}),
        ('Médias', {'fields': ('thumbnail', 'image')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase']
    readonly_fields = ['created_at']
