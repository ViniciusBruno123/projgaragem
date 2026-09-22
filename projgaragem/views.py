from django.conf import settings
from django.http import HttpResponse


def robots_txt(request):
    """Libera as vitrines para indexação e mantém painel/admin fora dos buscadores."""
    linhas = [
        "User-agent: *",
        "Allow: /g/",
        "Disallow: /painel/",
        "Disallow: /admin/",
        "Disallow: /billing/",
        "",
        f"Sitemap: {settings.SITE_URL}/sitemap.xml",
    ]
    return HttpResponse("\n".join(linhas), content_type="text/plain")
