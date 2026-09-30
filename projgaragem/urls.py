"""
URL configuration for projgaragem project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from dashboard.security import AdminLoginComCodigoForm
from storefront.sitemaps import GaragemSitemap, VeiculoSitemap
from tenants.views import termos_uso

from .views import robots_txt

sitemaps = {
    'garagens': GaragemSitemap,
    'veiculos': VeiculoSitemap,
}

# Login do /admin/ (Django admin) com trava extra por e-mail depois de tentativas demais —
# ver dashboard/security.py.
admin.site.login_form = AdminLoginComCodigoForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('termos/', termos_uso, name='termos_uso'),
    path('painel/', include('dashboard.urls')),
    path('billing/', include('billing.urls')),
    path('g/<slug:garagem_slug>/', include('storefront.urls')),
    path('', include('landing.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
