from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import EstiloLoginForm

app_name = 'dashboard'

urlpatterns = [
    path(
        'login/',
        views.PainelLoginView.as_view(template_name='dashboard/login.html', authentication_form=EstiloLoginForm),
        name='login',
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path(
        'senha/recuperar/',
        auth_views.PasswordResetView.as_view(
            template_name='dashboard/senha_recuperar.html',
            email_template_name='dashboard/email/senha_recuperar_corpo.txt',
            subject_template_name='dashboard/email/senha_recuperar_assunto.txt',
            success_url=reverse_lazy('dashboard:senha_recuperar_enviado'),
        ),
        name='senha_recuperar',
    ),
    path(
        'senha/recuperar/enviado/',
        auth_views.PasswordResetDoneView.as_view(template_name='dashboard/senha_recuperar_enviado.html'),
        name='senha_recuperar_enviado',
    ),
    path(
        'senha/redefinir/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='dashboard/senha_redefinir.html',
            success_url=reverse_lazy('dashboard:senha_redefinir_concluido'),
        ),
        name='senha_redefinir',
    ),
    path(
        'senha/redefinir/concluido/',
        auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/senha_redefinir_concluido.html'),
        name='senha_redefinir_concluido',
    ),
    path('', views.HomeView.as_view(), name='home'),
    path('veiculos/', views.VeiculoListView.as_view(), name='veiculo_list'),
    path('veiculos/novo/', views.VeiculoCreateView.as_view(), name='veiculo_create'),
    path('veiculos/<int:pk>/alternar/<str:campo>/', views.AlternarCampoVeiculoView.as_view(), name='veiculo_alternar'),
    path('veiculos/<int:pk>/editar/', views.VeiculoUpdateView.as_view(), name='veiculo_update'),
    path('veiculos/<int:pk>/excluir/', views.VeiculoDeleteView.as_view(), name='veiculo_delete'),
    path('propostas/', views.PropostaListView.as_view(), name='proposta_list'),
    path('propostas/<int:pk>/status/', views.AtualizarStatusPropostaView.as_view(), name='proposta_status'),
    path('avaliacoes/', views.AvaliacaoListView.as_view(), name='avaliacao_list'),
    path('avaliacoes/<int:pk>/status/', views.AtualizarStatusAvaliacaoView.as_view(), name='avaliacao_status'),
    path('assinatura/', views.AssinaturaView.as_view(), name='assinatura'),
    path('dados/', views.DadosGaragemView.as_view(), name='dados_garagem'),
]
