from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .models import Order, GroupBuySession, GroupBuyParticipation
from .serializers import (
    OrderCreateSerializer, OrderDetailSerializer,
    GroupBuySessionSerializer, GroupBuyJoinSerializer
)
from apps.users.models import User


class OrderListCreateView(generics.ListCreateAPIView):
    """Liste et création de commandes."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Order.objects.select_related('client').prefetch_related('items__product').all()
        elif user.role == User.Role.VENDOR:
            return Order.objects.filter(items__product__vendor=user).distinct()
        return Order.objects.filter(client=user).prefetch_related('items__product')

    @extend_schema(tags=['Orders'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Orders'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """Détail et mise à jour du statut d'une commande."""
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'reference'

    def get_queryset(self):
        user = self.request.user
        if user.role == User.Role.ADMIN:
            return Order.objects.all()
        elif user.role == User.Role.VENDOR:
            return Order.objects.filter(items__product__vendor=user).distinct()
        return Order.objects.filter(client=user)

    @extend_schema(tags=['Orders'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Orders'])
    def patch(self, request, *args, **kwargs):
        # Seuls vendeurs/admins peuvent changer le statut
        if request.user.role == User.Role.CLIENT:
            if set(request.data.keys()) - {'delivery_notes'}:
                return Response({'error': 'Action non autorisée.'}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


class GroupBuySessionListView(generics.ListCreateAPIView):
    """Liste des sessions d'achat groupé ouvertes."""
    serializer_class = GroupBuySessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = GroupBuySession.objects.select_related('product', 'organizer').prefetch_related('participations')
        status_filter = self.request.query_params.get('status', 'open')
        return qs.filter(status=status_filter)

    @extend_schema(tags=['Orders'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(tags=['Orders'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GroupBuyJoinView(APIView):
    """Rejoindre une session d'achat groupé."""
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(tags=['Orders'], request=GroupBuyJoinSerializer)
    def post(self, request, pk):
        try:
            session = GroupBuySession.objects.get(pk=pk)
        except GroupBuySession.DoesNotExist:
            return Response({'error': 'Session introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if not session.is_open:
            return Response({'error': 'Cette session est fermée ou expirée.'}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si déjà participant
        if GroupBuyParticipation.objects.filter(session=session, user=request.user).exists():
            return Response({'error': 'Vous participez déjà à cette session.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GroupBuyJoinSerializer(data=request.data, context={'session': session})
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        participation = GroupBuyParticipation.objects.create(
            session=session,
            user=request.user,
            quantity=quantity,
        )
        session.current_quantity += quantity
        session.save(update_fields=['current_quantity'])
        session.check_threshold()  # Vérifie si le seuil est atteint

        return Response({
            'message': f'Vous avez rejoint la session ! Progression : {session.progress_percent}%',
            'progress_percent': session.progress_percent,
            'current_quantity': session.current_quantity,
            'target_quantity': session.target_quantity,
            'status': session.status,
        }, status=status.HTTP_201_CREATED)
