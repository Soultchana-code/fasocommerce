from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

API_PREFIX = 'api/v1/'

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API Routes
    path(f'{API_PREFIX}users/', include('apps.users.urls')),
    path(f'{API_PREFIX}products/', include('apps.products.urls')),
    path(f'{API_PREFIX}orders/', include('apps.orders.urls')),
    path(f'{API_PREFIX}payments/', include('apps.payments.urls')),

    # Documentation API — Swagger & ReDoc (Livrable CDC §4.2.2)
    path(f'{API_PREFIX}schema/', SpectacularAPIView.as_view(), name='schema'),
    path(f'{API_PREFIX}docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path(f'{API_PREFIX}redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
