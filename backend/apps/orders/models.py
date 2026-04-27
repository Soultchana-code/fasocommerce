from django.db import models
from django.utils import timezone
from apps.users.models import User
from apps.products.models import Product


class GroupBuySession(models.Model):
    """
    Achat Groupé — Fonctionnalité clé Burkina-Centric.
    Permet aux utilisateurs de se regrouper pour déclencher
    le tarif de gros et lutter contre l'inflation.
    """
    class Status(models.TextChoices):
        OPEN = 'open', 'Ouvert'
        THRESHOLD_REACHED = 'threshold_reached', 'Seuil atteint'
        CONFIRMED = 'confirmed', 'Confirmé'
        CANCELLED = 'cancelled', 'Annulé'
        COMPLETED = 'completed', 'Complété'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='group_buy_sessions')
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_groups')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    target_quantity = models.PositiveIntegerField(verbose_name="Quantité cible (seuil de gros)")
    current_quantity = models.PositiveIntegerField(default=0, verbose_name="Quantité actuelle")
    unit_price_at_bulk = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name="Prix unitaire de gros (FCFA)"
    )
    expires_at = models.DateTimeField(
        verbose_name="Date d'expiration",
        default=lambda: timezone.now() + timezone.timedelta(days=7),
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'group_buy_sessions'
        verbose_name = 'Session d\'achat groupé'
        verbose_name_plural = 'Sessions d\'achat groupé'
        ordering = ['-created_at']

    def __str__(self):
        return f"Achat groupé [{self.product.name}] — {self.current_quantity}/{self.target_quantity}"

    @property
    def is_open(self):
        return self.status == self.Status.OPEN and timezone.now() < self.expires_at

    @property
    def progress_percent(self):
        if self.target_quantity == 0:
            return 0
        return min(100, int((self.current_quantity / self.target_quantity) * 100))

    def check_threshold(self):
        """Met à jour le statut si le seuil est atteint."""
        if self.current_quantity >= self.target_quantity and self.status == self.Status.OPEN:
            self.status = self.Status.THRESHOLD_REACHED
            self.save(update_fields=['status'])
            return True
        return False


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        PAID = 'paid', 'Payée'
        CONFIRMED = 'confirmed', 'Confirmée'
        PREPARING = 'preparing', 'En préparation'
        SHIPPED = 'shipped', 'Expédiée'
        DELIVERED = 'delivered', 'Livrée'
        CANCELLED = 'cancelled', 'Annulée'
        REFUNDED = 'refunded', 'Remboursée'

    class OrderType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individuel'
        GROUP = 'group', 'Achat groupé'

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.INDIVIDUAL)
    group_buy_session = models.ForeignKey(
        GroupBuySession, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='orders'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="Montant total (FCFA)")
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Commission (FCFA)")

    # Livraison — adressage burkinabè
    delivery_city = models.CharField(max_length=100, verbose_name="Ville de livraison")
    delivery_district = models.CharField(max_length=100, blank=True, verbose_name="Quartier")
    delivery_landmark = models.CharField(max_length=255, blank=True, verbose_name="Repère géographique")
    delivery_phone = models.CharField(max_length=20, verbose_name="Téléphone de livraison")
    delivery_notes = models.TextField(blank=True, verbose_name="Instructions de livraison")

    # Traçabilité
    reference = models.CharField(max_length=30, unique=True, verbose_name="Référence commande")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'orders'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['client', 'status']),
            models.Index(fields=['reference']),
        ]

    def __str__(self):
        return f"Commande {self.reference} — {self.client.phone_number}"

    def save(self, *args, **kwargs):
        if not self.reference:
            import uuid
            self.reference = f"FC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire (FCFA)")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Sous-total (FCFA)")

    class Meta:
        db_table = 'order_items'
        verbose_name = 'Article de commande'

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} ({self.order.reference})"


class GroupBuyParticipation(models.Model):
    """Participation d'un utilisateur à une session d'achat groupé."""
    session = models.ForeignKey(GroupBuySession, on_delete=models.CASCADE, related_name='participations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_participations')
    quantity = models.PositiveIntegerField(default=1)
    order = models.OneToOneField(Order, null=True, blank=True, on_delete=models.SET_NULL)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_buy_participations'
        unique_together = [['session', 'user']]
        verbose_name = 'Participation achat groupé'

    def __str__(self):
        return f"{self.user.phone_number} → {self.session}"
