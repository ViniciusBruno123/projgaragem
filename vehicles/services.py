"""Heurística de "veículos semelhantes" (página de detalhe do veículo, na vitrine).

Não é um filtro que pode ficar vazio: pega os outros veículos disponíveis da mesma
garagem, ordena por semelhança e devolve os N mais parecidos. Se a garagem tiver
menos que N outros veículos, devolve todos que houver — nunca completa com algo
de fora da garagem nem inventa um mínimo.
"""

QUANTIDADE_PADRAO = 5


def _porte_do_motor(veiculo):
    """Um número só pra comparar "tamanho do motor" entre motos e carros — não é uma
    unidade real (só multiplica a potência em litros por mil pra ficar na mesma ordem
    de grandeza da cilindrada em cc), só serve pra ordenar por semelhança."""
    if veiculo.cilindrada is not None:
        return veiculo.cilindrada
    if veiculo.potencia_motor is not None:
        return float(veiculo.potencia_motor) * 1000
    return None


def _chave_semelhanca(base, candidato):
    """Tupla usada pra ordenar os candidatos. Python compara tuplas posição a posição,
    então isso já implementa a prioridade em cascata pedida — tipo, depois preço,
    depois marca, depois ano, depois motor — sem precisar de pesos artificiais entre
    critérios de escalas tão diferentes (R$ vs. cc vs. ano)."""
    tipo_diferente = candidato.tipo != base.tipo
    diferenca_preco = abs(candidato.preco - base.preco)
    marca_diferente = candidato.marca.strip().lower() != base.marca.strip().lower()
    diferenca_ano = abs(candidato.ano_modelo - base.ano_modelo)

    motor_base = _porte_do_motor(base)
    motor_candidato = _porte_do_motor(candidato)
    # Falta o dado de motor de um lado (ou dos dois): não dá pra comparar, então nem
    # favorece nem penaliza. É o critério de menor prioridade, então o efeito é pequeno.
    diferenca_motor = abs(motor_candidato - motor_base) if None not in (motor_base, motor_candidato) else 0

    return (tipo_diferente, diferenca_preco, marca_diferente, diferenca_ano, diferenca_motor)


def veiculos_semelhantes(veiculo, quantidade=QUANTIDADE_PADRAO):
    candidatos = list(
        veiculo.garagem.veiculos.filter(disponivel=True).exclude(pk=veiculo.pk).prefetch_related('fotos')
    )
    candidatos.sort(key=lambda candidato: _chave_semelhanca(veiculo, candidato))
    return candidatos[:quantidade]
