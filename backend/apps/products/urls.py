from django.urls import path
from .views import (
    CategoryListView,
    ProductListView,
    VendorProductListView,
    ProductDetailView,
    ProductReviewCreateView,
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('mine/', VendorProductListView.as_view(), name='product-vendor-list'),
    path('', ProductListView.as_view(), name='product-list'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<slug:slug>/reviews/', ProductReviewCreateView.as_view(), name='product-review-create'),
]
