from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from leads.models import Proposta
from tenants.mixins import BloqueiaEdicaoSeInadimplenteMixin, GaragemRequiredMixin, RespeitaLimiteDoPlanoMixin
from vehicles.models import Veiculo

from .forms import FotoVeiculoFormSet, GaragemForm, VeiculoForm, VeiculoPainelFiltroForm
from .security import bloqueado, limpar_falhas, registrar_falha


class PainelLoginView(auth_views.LoginView):
    """Login do painel com limite de tentativas (ver dashboard/security.py)."""

    def post(self, request, *args, **kwargs):
        usuario = request.POST.get('username', '').strip()
        if bloqueado(request, usuario):
            form = self.get_form()
            form.add_error(None, "Muitas tentativas de login. Aguarde alguns minutos e tente novamente.")
            return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        registrar_falha(self.request, self.request.POST.get('username', '').strip())
        return super().form_invalid(form)

    def form_valid(self, form):
        limpar_falhas(form.get_user().get_username())
        return super().form_valid(form)


class DadosGaragemView(GaragemRequiredMixin, UpdateView):
    form_class = GaragemForm
    template_name = 'dashboard/dados_garagem.html'
    success_url = reverse_lazy('dashboard:dados_garagem')

    def get_object(self, queryset=None):
        return self.garagem

    def form_valid(self, form):
        messages.success(self.request, "Dados da garagem atualizados com sucesso.")
        return super().form_valid(form)


class AssinaturaView(GaragemRequiredMixin, TemplateView):
    template_name = 'dashboard/assinatura.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['garagem'] = self.garagem
        ctx['assinatura'] = getattr(self.garagem, 'assinatura', None)
        return ctx


class HomeView(GaragemRequiredMixin, TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['garagem'] = self.garagem
        ctx['total_veiculos'] = self.garagem.veiculos.count()
        ctx['limite_veiculos'] = self.garagem.limite_veiculos
        return ctx


class VeiculoListView(GaragemRequiredMixin, ListView):
    template_name = 'dashboard/veiculo_list.html'
    context_object_name = 'veiculos'

    def get_queryset(self):
        self.filtro = VeiculoPainelFiltroForm(self.request.GET or None, garagem=self.garagem)
        queryset = self.garagem.veiculos.all().prefetch_related('fotos')
        return self.filtro.aplicar(queryset)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        ctx['filtro_ativo'] = any(self.request.GET.values())
        ctx['total_veiculos'] = self.garagem.veiculos.count()
        ctx['limite_veiculos'] = self.garagem.limite_veiculos
        ctx['no_limite'] = ctx['total_veiculos'] >= ctx['limite_veiculos']
        return ctx


class AlternarCampoVeiculoView(GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, View):
    """Liga/desliga Destaque ou Disponível direto da lista, sem abrir o formulário de edição."""

    CAMPOS_PERMITIDOS = {'destaque', 'disponivel'}

    def post(self, request, pk, campo):
        if campo not in self.CAMPOS_PERMITIDOS:
            raise Http404("Campo não pode ser alternado por aqui.")
        veiculo = get_object_or_404(self.garagem.veiculos, pk=pk)
        setattr(veiculo, campo, not getattr(veiculo, campo))
        veiculo.save(update_fields=[campo])
        return redirect(self._url_de_volta(request))

    def _url_de_volta(self, request):
        """Mantém os filtros/ordenação da lista depois de alternar (não confia cegamente
        no valor enviado, pra não virar redirecionamento aberto)."""
        proximo = request.POST.get('proximo', '')
        if proximo and url_has_allowed_host_and_scheme(proximo, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return proximo
        return reverse_lazy('dashboard:veiculo_list')


class VeiculoFormsetMixin:
    """Compartilha a lógica do formset de fotos entre criar/editar veículo."""

    def get_formset(self):
        instance = getattr(self, 'object', None)
        if self.request.method == 'POST':
            return FotoVeiculoFormSet(self.request.POST, self.request.FILES, instance=instance)
        return FotoVeiculoFormSet(instance=instance)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.setdefault('formset', self.get_formset())
        return ctx

    def form_valid(self, form):
        formset = self.get_formset()
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, formset=formset))
        form.instance.garagem = self.garagem
        self.object = form.save()
        formset.instance = self.object
        formset.save()
        messages.success(self.request, self.success_message)
        return redirect(self.get_success_url())


class VeiculoCreateView(
    GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, RespeitaLimiteDoPlanoMixin,
    VeiculoFormsetMixin, CreateView,
):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'dashboard/veiculo_form.html'
    success_url = reverse_lazy('dashboard:veiculo_list')
    success_message = "Veículo criado com sucesso."


class VeiculoUpdateView(GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, VeiculoFormsetMixin, UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    template_name = 'dashboard/veiculo_form.html'
    success_url = reverse_lazy('dashboard:veiculo_list')
    success_message = "Veículo atualizado com sucesso."

    def get_queryset(self):
        return self.garagem.veiculos.all()


class PropostaListView(GaragemRequiredMixin, ListView):
    template_name = 'dashboard/proposta_list.html'
    context_object_name = 'propostas'

    def get_queryset(self):
        return self.garagem.propostas.select_related('veiculo').all()


class AtualizarStatusPropostaView(GaragemRequiredMixin, View):
    def post(self, request, pk):
        proposta = get_object_or_404(self.garagem.propostas, pk=pk)
        novo_status = request.POST.get('status')
        if novo_status in Proposta.Status.values:
            proposta.status = novo_status
            proposta.save(update_fields=['status'])
            messages.success(request, "Status da proposta atualizado.")
        return redirect('dashboard:proposta_list')


class VeiculoDeleteView(GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, DeleteView):
    model = Veiculo
    template_name = 'dashboard/veiculo_confirm_delete.html'
    success_url = reverse_lazy('dashboard:veiculo_list')

    def get_queryset(self):
        return self.garagem.veiculos.all()

    def form_valid(self, form):
        messages.success(self.request, "Veículo excluído com sucesso.")
        return super().form_valid(form)
