from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.HomeView.as_view(), name='home'),
    path('veiculos/', views.VeiculoListView.as_view(), name='veiculo_list'),
    path('veiculos/novo/', views.VeiculoCreateView.as_view(), name='veiculo_create'),
    path('veiculos/<int:pk>/editar/', views.VeiculoUpdateView.as_view(), name='veiculo_update'),
    path('veiculos/<int:pk>/excluir/', views.VeiculoDeleteView.as_view(), name='veiculo_delete'),
    path('propostas/', views.PropostaListView.as_view(), name='proposta_list'),
    path('assinatura/', views.AssinaturaView.as_view(), name='assinatura'),
]
