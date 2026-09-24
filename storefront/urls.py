from django.urls import path

from leads import views as leads_views

from . import views

app_name = 'storefront'

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('veiculos/<slug:veiculo_slug>/', views.detalhe_veiculo, name='detalhe_veiculo'),
    path('veiculos/<slug:veiculo_slug>/simular/', views.simular_financiamento, name='simular_financiamento'),
    path('veiculos/<slug:veiculo_slug>/proposta/', leads_views.enviar_proposta, name='enviar_proposta'),
    path('contato/', leads_views.enviar_proposta, name='contato'),
    path('veiculos/<slug:veiculo_slug>/vender/', leads_views.enviar_avaliacao, name='enviar_avaliacao_veiculo'),
    path('vender/', leads_views.enviar_avaliacao, name='enviar_avaliacao'),
    path('privacidade/', views.politica_privacidade, name='privacidade'),
]
