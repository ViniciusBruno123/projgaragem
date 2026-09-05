from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from leads.models import Proposta
from tenants.mixins import BloqueiaEdicaoSeInadimplenteMixin, GaragemRequiredMixin
from vehicles.models import Veiculo

from .forms import FotoVeiculoFormSet, GaragemForm, VeiculoForm


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
        return ctx


class VeiculoListView(GaragemRequiredMixin, ListView):
    template_name = 'dashboard/veiculo_list.html'
    context_object_name = 'veiculos'

    def get_queryset(self):
        return self.garagem.veiculos.all()


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


class VeiculoCreateView(GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, VeiculoFormsetMixin, CreateView):
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


class VeiculoDeleteView(GaragemRequiredMixin, BloqueiaEdicaoSeInadimplenteMixin, DeleteView):
    model = Veiculo
    template_name = 'dashboard/veiculo_confirm_delete.html'
    success_url = reverse_lazy('dashboard:veiculo_list')

    def get_queryset(self):
        return self.garagem.veiculos.all()

    def form_valid(self, form):
        messages.success(self.request, "Veículo excluído com sucesso.")
        return super().form_valid(form)
