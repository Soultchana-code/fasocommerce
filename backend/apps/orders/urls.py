from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    GroupBuySessionListView,
    GroupBuyJoinView,
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<str:reference>/', OrderDetailView.as_view(), name='order-detail'),
    # Achat groupé — Fonctionnalité Burkina-Centric
    path('group-buy/', GroupBuySessionListView.as_view(), name='groupbuy-list-create'),
    path('group-buy/<int:pk>/join/', GroupBuyJoinView.as_view(), name='groupbuy-join'),
]
