from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductReview


class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'parent', 'subcategories', 'is_active']

    def get_subcategories(self, obj):
        children = obj.subcategories.filter(is_active=True)
        return CategorySerializer(children, many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']


class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ProductReview
        fields = ['id', 'user_name', 'rating', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['is_verified_purchase', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Sérialiseur léger pour les listes — Mode basse consommation."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'unit_price', 'bulk_price', 'bulk_min_quantity',
            'thumbnail', 'stock', 'unit', 'is_essential', 'status',
            'category_name', 'vendor_name', 'is_in_stock',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur complet pour la page produit."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source='vendor.get_full_name', read_only=True)
    vendor_city = serializers.CharField(source='vendor.city', read_only=True)
    avg_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description',
            'unit_price', 'bulk_price', 'bulk_min_quantity',
            'stock', 'unit', 'weight_kg', 'is_essential', 'status',
            'commission_rate', 'thumbnail', 'image',
            'category', 'category_id',
            'vendor_name', 'vendor_city',
            'images', 'reviews', 'avg_rating',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['slug', 'vendor_name', 'vendor_city', 'created_at', 'updated_at']

    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    def create(self, validated_data):
        validated_data['vendor'] = self.context['request'].user
        import re
        from django.utils.text import slugify
        base_slug = slugify(validated_data['name'])
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        validated_data['slug'] = slug
        return super().create(validated_data)
