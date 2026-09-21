import json
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django.conf import settings

from .models import TaxaReferencia

# Banco Central, SGS 25471: taxa média mensal de juros das operações de crédito com
# recursos livres, pessoas físicas, aquisição de veículos (% ao mês).
FONTE_BCB = 'bcb-sgs-25471'
URL_BCB = 'https://api.bcb.gov.br/dados/serie/bcdata.sgs.25471/dados/ultimos/1?formato=json'


def calcular_parcela_price(valor_financiado: Decimal, taxa_mensal_pct: Decimal, numero_parcelas: int) -> Decimal:
    """Valor da parcela mensal pela Tabela Price (juros compostos)."""
    if taxa_mensal_pct == 0:
        return (valor_financiado / numero_parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    i = taxa_mensal_pct / Decimal(100)
    fator = (1 + i) ** numero_parcelas
    pmt = valor_financiado * (i * fator) / (fator - 1)
    return pmt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class TaxaIndisponivel(Exception):
    pass


@dataclass(frozen=True)
class TaxaAplicada:
    valor: Decimal
    origem: str  # 'garagem', 'mercado' ou 'estimada'
    referencia: date | None = None


def buscar_taxa_bcb(timeout=15):
    """Consulta a última taxa média publicada pelo Banco Central: (mês de referência, taxa)."""
    try:
        with urllib.request.urlopen(URL_BCB, timeout=timeout) as resposta:
            ultimo = json.load(resposta)[-1]
        referencia = datetime.strptime(ultimo['data'], '%d/%m/%Y').date()
        return referencia, Decimal(ultimo['valor'])
    except (OSError, ValueError, KeyError, IndexError, TypeError, InvalidOperation) as exc:
        raise TaxaIndisponivel(f'Não foi possível obter a taxa do Banco Central: {exc}') from exc


def atualizar_taxa_bcb():
    """Guarda a última taxa do Banco Central. Devolve (TaxaReferencia, criada)."""
    referencia, taxa = buscar_taxa_bcb()
    return TaxaReferencia.objects.update_or_create(
        fonte=FONTE_BCB, referencia=referencia, defaults={'taxa_mensal': taxa},
    )


def taxa_media_de_mercado():
    return TaxaReferencia.objects.filter(fonte=FONTE_BCB).first()


def taxa_para(garagem):
    """Taxa que o simulador usa: a da garagem, se ela informou; senão a média de mercado."""
    if garagem.taxa_juros_mensal_padrao is not None:
        return TaxaAplicada(garagem.taxa_juros_mensal_padrao, 'garagem')
    media = taxa_media_de_mercado()
    if media:
        return TaxaAplicada(media.taxa_mensal, 'mercado', media.referencia)
    return TaxaAplicada(settings.TAXA_JUROS_ESTIMADA, 'estimada')
