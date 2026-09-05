from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import EstiloLoginForm

app_name = 'dashboard'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='dashboard/login.html', authentication_form=EstiloLoginForm),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.HomeView.as_view(), name='home'),
    path('veiculos/', views.VeiculoListView.as_view(), name='veiculo_list'),
    path('veiculos/novo/', views.VeiculoCreateView.as_view(), name='veiculo_create'),
    path('veiculos/<int:pk>/editar/', views.VeiculoUpdateView.as_view(), name='veiculo_update'),
    path('veiculos/<int:pk>/excluir/', views.VeiculoDeleteView.as_view(), name='veiculo_delete'),
    path('propostas/', views.PropostaListView.as_view(), name='proposta_list'),
    path('propostas/<int:pk>/status/', views.AtualizarStatusPropostaView.as_view(), name='proposta_status'),
    path('assinatura/', views.AssinaturaView.as_view(), name='assinatura'),
    path('dados/', views.DadosGaragemView.as_view(), name='dados_garagem'),
]
