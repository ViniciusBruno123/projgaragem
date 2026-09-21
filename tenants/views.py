from django.shortcuts import render

from .legal import contexto_plataforma


def termos_uso(request):
    return render(request, 'tenants/termos_uso.html', contexto_plataforma())
