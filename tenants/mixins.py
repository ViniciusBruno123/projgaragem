from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Garagem


class GaragemRequiredMixin(LoginRequiredMixin):
    """Exige login e resolve a garagem do usuário logado em self.garagem.

    Views do painel devem sempre buscar objetos a partir de self.garagem
    (ex: self.garagem.veiculos.all()), nunca do manager global do model —
    isso é o que impede um dono acessar dados de outra garagem trocando
    o pk/slug na URL.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            self.garagem = request.user.garagem
        except Garagem.DoesNotExist:
            raise PermissionDenied("Usuário sem garagem vinculada.")
        return super().dispatch(request, *args, **kwargs)


class BloqueiaEdicaoSeInadimplenteMixin:
    """Bloqueia criar/editar/excluir quando a garagem está atrasada ou suspensa.

    Usar SÓ nas views de escrita (create/update/delete) — a listagem/leitura
    do painel continua acessível mesmo com pagamento atrasado; só a vitrine
    pública some quando suspensa (ver tenants.services.get_garagem_ativa_ou_404).
    Deve vir DEPOIS de GaragemRequiredMixin no MRO, já que depende de self.garagem.
    """

    def dispatch(self, request, *args, **kwargs):
        if self.garagem.status in (Garagem.Status.ATRASADO, Garagem.Status.SUSPENSO):
            messages.warning(request, "Pagamento em atraso. Regularize para editar seu estoque.")
            return redirect('dashboard:assinatura')
        return super().dispatch(request, *args, **kwargs)
