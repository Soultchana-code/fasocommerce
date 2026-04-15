from rest_framework import serializers
from django.utils import timezone
from .models import Order, OrderItem, GroupBuySession, GroupBuyParticipation
from apps.products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.ImageField(source='product.thumbnail', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_thumbnail', 'quantity', 'unit_price', 'subtotal']
        read_only_fields = ['unit_price', 'subtotal']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_type', 'group_buy_session',
            'delivery_city', 'delivery_district', 'delivery_landmark',
            'delivery_phone', 'delivery_notes',
            'items',
        ]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("La commande doit contenir au moins un article.")
        return items

    def create(self, validated_data):
        from apps.products.models import Product
        items_data = validated_data.pop('items')
        validated_data['client'] = self.context['request'].user
        order = Order.objects.create(**validated_data)
        total = 0
        commission_total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            # Tarif de gros si achat groupé avec seuil atteint
            if order.order_type == Order.OrderType.GROUP and product.bulk_price:
                unit_price = product.bulk_price
            else:
                unit_price = product.unit_price
            item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
            )
            total += item.subtotal
            commission_total += item.subtotal * (product.commission_rate / 100)
            # Déduire du stock
            product.stock = max(0, product.stock - quantity)
            product.save(update_fields=['stock'])
        order.total_amount = total
        order.commission_amount = commission_total
        order.save(update_fields=['total_amount', 'commission_amount'])
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    client_phone = serializers.CharField(source='client.phone_number', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'reference', 'client_phone', 'order_type', 'status', 'status_display',
            'total_amount', 'commission_amount',
            'delivery_city', 'delivery_district', 'delivery_landmark',
            'delivery_phone', 'delivery_notes',
            'items', 'created_at', 'updated_at', 'delivered_at',
        ]
        read_only_fields = ['reference', 'total_amount', 'commission_amount', 'created_at']


class GroupBuySessionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_thumbnail = serializers.ImageField(source='product.thumbnail', read_only=True)
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = GroupBuySession
        fields = [
            'id', 'product', 'product_name', 'product_thumbnail',
            'organizer_name', 'status', 'target_quantity', 'current_quantity',
            'unit_price_at_bulk', 'expires_at', 'progress_percent', 'is_open',
            'participants_count', 'created_at',
        ]
        read_only_fields = ['organizer_name', 'current_quantity', 'status', 'created_at']

    def get_participants_count(self, obj):
        return obj.participations.count()

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        product = validated_data['product']
        if product.bulk_price:
            validated_data.setdefault('unit_price_at_bulk', product.bulk_price)
        validated_data.setdefault('target_quantity', product.bulk_min_quantity)
        return super().create(validated_data)


class GroupBuyJoinSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        session = self.context.get('session')
        if not session or not session.is_open:
            raise serializers.ValidationError("Cette session d'achat groupé est fermée ou expirée.")
        return data
