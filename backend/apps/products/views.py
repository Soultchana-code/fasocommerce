from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils.text import slugify

from .models import Category, Product, ProductReview
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer, ProductReviewSerializer
from apps.users.models import User


class IsVendorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in [User.Role.VENDOR, User.Role.ADMIN]

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.vendor == request.user or request.user.role == User.Role.ADMIN


class CategoryListView(generics.ListCreateAPIView):
    """Liste et création des catégories."""
    queryset = Category.objects.filter(is_active=True, parent=None).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [IsVendorOrAdmin]

    @extend_schema(tags=['Products'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProductListView(generics.ListCreateAPIView):
    """
    Liste des produits — Supporte le mode basse consommation.
    En retournant uniquement les miniatures pour les zones à faible connectivité.
    """
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_essential', 'status', 'vendor']
    search_fields = ['name', 'description']
    ordering_fields = ['unit_price', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.select_related('category', 'vendor').filter(status=Product.Status.ACTIVE)
        if self.request.user.is_authenticated and self.request.user.role == User.Role.VENDOR:
            # Les vendeurs voient leurs propres produits peu importe le statut
            qs = Product.objects.filter(vendor=self.request.user).select_related('category', 'vendor')
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductDetailSerializer
        # Mode basse consommation : paramètre ?low_bandwidth=true → miniature uniquement
        return ProductListSerializer

    @extend_schema(
        tags=['Products'],
        parameters=[
            OpenApiParameter('low_bandwidth', bool, description='Mode basse consommation — images miniatures seulement'),
            OpenApiParameter('is_essential', bool, description='Filtrer les produits de première nécessité'),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Products'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class VendorProductListView(generics.ListAPIView):
    """Liste des produits appartenant au vendeur connecté — Dashboard."""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOrAdmin]

    @extend_schema(tags=['Products (Vendor)'])
    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user).order_by('-created_at')


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Détail, mise à jour et suppression d'un produit."""
    queryset = Product.objects.select_related('category', 'vendor').prefetch_related('images', 'reviews__user')
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    @extend_schema(tags=['Products'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Products'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(tags=['Products'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ProductReviewCreateView(generics.CreateAPIView):
    """Soumettre un avis sur un produit."""
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Products'])
    def perform_create(self, serializer):
        product_slug = self.kwargs['slug']
        from django.db import IntegrityError
        from rest_framework.exceptions import ValidationError
        
        product = Product.objects.get(slug=product_slug)
        
        # Vérifie si l'utilisateur a commandé ce produit
        from apps.orders.models import OrderItem
        is_verified = OrderItem.objects.filter(
            order__client=self.request.user,
            product=product,
            order__status='delivered'
        ).exists()
        
        try:
            serializer.save(user=self.request.user, product=product, is_verified_purchase=is_verified)
        except IntegrityError:
            raise ValidationError({"detail": "Vous avez déjà laissé un avis sur ce produit."})
