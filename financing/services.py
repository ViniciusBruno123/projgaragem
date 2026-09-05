from decimal import ROUND_HALF_UP, Decimal


def calcular_parcela_price(valor_financiado: Decimal, taxa_mensal_pct: Decimal, numero_parcelas: int) -> Decimal:
    """Valor da parcela mensal pela Tabela Price (juros compostos)."""
    if taxa_mensal_pct == 0:
        return (valor_financiado / numero_parcelas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    i = taxa_mensal_pct / Decimal(100)
    fator = (1 + i) ** numero_parcelas
    pmt = valor_financiado * (i * fator) / (fator - 1)
    return pmt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
