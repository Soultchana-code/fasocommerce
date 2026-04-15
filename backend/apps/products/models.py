from django.db import models
from apps.users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icône (emoji ou classe CSS)")
    parent = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='subcategories',
        verbose_name="Catégorie parente"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        ACTIVE = 'active', 'Actif'
        SUSPENDED = 'suspended', 'Suspendu'
        OUT_OF_STOCK = 'out_of_stock', 'Rupture de stock'

    vendor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='products',
        limit_choices_to={'role': 'vendor'},
        verbose_name="Vendeur"
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='products',
        verbose_name="Catégorie"
    )
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(verbose_name="Description")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire (FCFA)")
    # Tarif de gros pour l'achat groupé
    bulk_price = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name="Prix de gros (FCFA)"
    )
    bulk_min_quantity = models.PositiveIntegerField(
        default=10,
        verbose_name="Quantité min. pour le prix de gros"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    unit = models.CharField(max_length=30, default='unité', verbose_name="Unité de mesure")
    weight_kg = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, verbose_name="Poids (kg)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_essential = models.BooleanField(
        default=False,
        verbose_name="Produit de première nécessité",
        help_text="Produits prioritaires pour la stabilisation des prix"
    )
    # Mode basse consommation : image optimisée
    thumbnail = models.ImageField(upload_to='products/thumbs/', null=True, blank=True, verbose_name="Miniature")
    image = models.ImageField(upload_to='products/images/', null=True, blank=True, verbose_name="Image principale")
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00,
        verbose_name="Taux de commission (%)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_essential']),
            models.Index(fields=['vendor', 'status']),
        ]

    def __str__(self):
        return f"{self.name} — {self.unit_price} FCFA"

    @property
    def effective_price(self):
        """Prix effectif selon le stock disponible."""
        if self.stock == 0:
            return None
        return self.unit_price

    @property
    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'product_images'
        ordering = ['order']

    def __str__(self):
        return f"Image {self.order} — {self.product.name}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5)  # 1 à 5
    comment = models.TextField(blank=True)
    is_verified_purchase = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_reviews'
        unique_together = [['product', 'user']]
        verbose_name = 'Avis produit'

    def __str__(self):
        return f"{self.user.phone_number} — {self.product.name} ({self.rating}★)"
