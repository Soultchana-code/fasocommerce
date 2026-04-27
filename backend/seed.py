import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fasocommerce.settings')
django.setup()

from apps.users.models import User
from apps.products.models import Category, Product

# On récupère l'admin que j'ai créé tout à l'heure
admin = User.objects.filter(role=User.Role.ADMIN).first()

if not admin:
    # Au cas où l'admin aurait disparu, on en recrée un avec email
    admin = User.objects.create_superuser(
        email='admin@fasocommerce.bf', 
        password='AdminFaso2026', 
        phone_number='+22600000000'
    )

cat, _ = Category.objects.get_or_create(name='Alimentation', slug='alimentation')

products_data = [
    {
        'name': 'Sac de Riz (25kg)',
        'slug': 'sac-riz-25kg',
        'vendor': admin,
        'category': cat,
        'description': 'Riz brisé parfumé de qualité supérieure.',
        'unit_price': 12500,
        'bulk_price': 10000,
        'bulk_min_quantity': 5,
        'stock': 100,
        'unit': 'sac',
        'is_essential': True,
        'status': 'active'
    },
    {
        'name': "Bidon d'Huile (5L)",
        'slug': 'bidon-huile-5l',
        'vendor': admin,
        'category': cat,
        'description': 'Huile végétale raffinée pour cuisine.',
        'unit_price': 6000,
        'bulk_price': 5000,
        'bulk_min_quantity': 10,
        'stock': 50,
        'unit': 'bidon',
        'is_essential': True,
        'status': 'active'
    },
    {
        'name': 'Sucre en Poudre (50kg)',
        'slug': 'sucre-poudre-50kg',
        'vendor': admin,
        'category': cat,
        'description': 'Sucre blanc local granulé.',
        'unit_price': 30000,
        'bulk_price': 27000,
        'bulk_min_quantity': 3,
        'stock': 20,
        'unit': 'sac',
        'is_essential': False,
        'status': 'active'
    },
    {
        'name': 'Carton de Pâtes (10kg)',
        'slug': 'carton-pates-10kg',
        'vendor': admin,
        'category': cat,
        'description': 'Pâtes alimentaires diverses.',
        'unit_price': 8500,
        'bulk_price': 7500,
        'bulk_min_quantity': 5,
        'stock': 40,
        'unit': 'carton',
        'is_essential': True,
        'status': 'active'
    }
]

for prod in products_data:
    p, created = Product.objects.get_or_create(slug=prod['slug'], defaults=prod)
    if not created:
        for key, value in prod.items():
            setattr(p, key, value)
        p.save()

print('Catalogue rempli avec succès !')
