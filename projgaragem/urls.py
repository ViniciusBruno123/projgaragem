"""
URL configuration for projgaragem project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from tenants.views import termos_uso

urlpatterns = [
    path('admin/', admin.site.urls),
    path('termos/', termos_uso, name='termos_uso'),
    path('painel/', include('dashboard.urls')),
    path('billing/', include('billing.urls')),
    path('g/<slug:garagem_slug>/', include('storefront.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
