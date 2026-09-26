// Cadastro de veículo em etapas: tipo -> identificação -> detalhes -> preço -> fotos.
// Sem este script o formulário continua funcionando como uma página só (ver veiculo_form.html).
//
// - O tipo (carro ou moto) é escolhido em dois botões grandes; os campos que só existem para o
//   outro tipo somem e ficam desativados (desativado não é enviado, então nada "sobra" no cadastro).
// - "Continuar" confere os campos da etapa antes de avançar; ao salvar, todas as etapas são conferidas.
// - Se o servidor devolver erro, a primeira etapa com problema é aberta.
(function () {
    var form = document.querySelector('[data-wizard]');
    if (!form) return;

    var etapas = Array.prototype.slice.call(form.querySelectorAll('.etapa'));
    var passos = Array.prototype.slice.call(form.querySelectorAll('[data-passo]'));
    var listaPassos = form.querySelector('[data-passos]');
    var opcoesTipo = form.querySelector('[data-tipo-opcoes]');
    var campoTipoSelect = form.querySelector('[data-tipo-select]');
    var seletorTipo = form.querySelector('select[name="tipo"]');
    var botoesTipo = Array.prototype.slice.call(form.querySelectorAll('[data-tipo]'));
    var navegacao = form.querySelector('[data-nav]');
    var botaoVoltar = form.querySelector('[data-voltar]');
    var botaoContinuar = form.querySelector('[data-continuar]');
    var rodapeFinal = form.querySelector('[data-final]');
    var edicao = form.hasAttribute('data-edicao');

    var tipo = form.hasAttribute('data-tipo-escolhido') ? seletorTipo.value : '';
    var atual = 0;
    var maiorVisitada = 0;
    var ultima = etapas.length - 1;

    // ---- tipo: mostra só os campos que pertencem ao tipo escolhido
    function aplicarTipo() {
        botoesTipo.forEach(function (botao) {
            var escolhido = botao.getAttribute('data-tipo') === tipo;
            botao.setAttribute('aria-pressed', escolhido ? 'true' : 'false');
            botao.classList.toggle('tipo-opcao--escolhida', escolhido);
        });
        Array.prototype.forEach.call(form.querySelectorAll('[data-so-tipo]'), function (campo) {
            var pertence = campo.getAttribute('data-so-tipo') === tipo;
            campo.hidden = !pertence;
            Array.prototype.forEach.call(campo.querySelectorAll('input, select, textarea'), function (entrada) {
                entrada.disabled = !pertence;
            });
        });
        if (tipo) seletorTipo.value = tipo;
    }

    // ---- título sugerido enquanto a pessoa não escreve o dela
    var titulo = form.querySelector('[name="titulo"]');
    var marca = form.querySelector('[name="marca"]');
    var modelo = form.querySelector('[name="modelo"]');
    var anoModelo = form.querySelector('[name="ano_modelo"]');
    var tituloEditado = !!(titulo && titulo.value);
    function sugerirTitulo() {
        if (!titulo || tituloEditado) return;
        titulo.value = [marca.value.trim(), modelo.value.trim(), anoModelo.value].filter(Boolean).join(' ');
    }
    if (titulo) {
        titulo.addEventListener('input', function () { tituloEditado = true; });
        [marca, modelo, anoModelo].forEach(function (entrada) { entrada.addEventListener('input', sugerirTitulo); });
    }

    // ---- navegação entre etapas
    function mostrar(indice, focar) {
        atual = indice;
        maiorVisitada = Math.max(maiorVisitada, indice);
        etapas.forEach(function (etapa, i) { etapa.hidden = i !== indice; });
        passos.forEach(function (passo, i) {
            passo.disabled = i > maiorVisitada;
            passo.classList.toggle('wizard-passo--atual', i === indice);
            passo.classList.toggle('wizard-passo--feito', i < indice);
            if (i === indice) passo.setAttribute('aria-current', 'step'); else passo.removeAttribute('aria-current');
        });
        var naTipo = indice === 0;
        var naUltima = indice === ultima;
        botaoVoltar.hidden = naTipo;
        botaoContinuar.hidden = naTipo || naUltima;
        rodapeFinal.hidden = !naUltima;
        navegacao.hidden = naTipo;
        if (focar) {
            form.scrollIntoView({ block: 'start', behavior: 'smooth' });
            var cabecalho = etapas[indice].querySelector('.etapa-titulo');
            if (cabecalho) cabecalho.focus({ preventScroll: true });
        }
    }

    // Campos que a pessoa de fato preenche na etapa: nem desativados (do outro tipo) nem dentro de
    // um bloco escondido. A própria etapa pode estar escondida (não é a atual), então só se olha
    // dos campos até ela.
    function escondido(entrada, etapa) {
        for (var no = entrada; no && no !== etapa; no = no.parentElement) { if (no.hidden) return true; }
        return false;
    }
    function entradasVisiveis(etapa) {
        return Array.prototype.slice.call(etapa.querySelectorAll('input, select, textarea')).filter(function (entrada) {
            return !entrada.disabled && entrada.type !== 'hidden' && entrada.type !== 'file' && !escondido(entrada, etapa);
        });
    }

    // Confere os campos de uma etapa; devolve false (e mostra o aviso do navegador) no primeiro inválido.
    function etapaValida(indice) {
        var invalida = entradasVisiveis(etapas[indice]).find(function (entrada) { return !entrada.checkValidity(); });
        if (!invalida) return true;
        if (indice !== atual) mostrar(indice, false);
        invalida.reportValidity();
        return false;
    }

    function continuar() {
        if (atual === 0) return;
        if (etapaValida(atual)) mostrar(Math.min(atual + 1, ultima), true);
    }

    botaoContinuar.addEventListener('click', continuar);
    botaoVoltar.addEventListener('click', function () { mostrar(Math.max(atual - 1, 0), true); });
    passos.forEach(function (passo, i) {
        passo.addEventListener('click', function () {
            // Avançar pelo indicador também confere as etapas puladas; voltar é sempre livre.
            for (var j = atual; j < i; j++) { if (j > 0 && !etapaValida(j)) return; }
            mostrar(i, true);
        });
    });

    botoesTipo.forEach(function (botao) {
        botao.addEventListener('click', function () {
            tipo = botao.getAttribute('data-tipo');
            aplicarTipo();
            mostrar(1, true);
        });
    });

    // Enter dentro de um campo avança a etapa em vez de enviar o formulário incompleto.
    form.addEventListener('keydown', function (evento) {
        var alvo = evento.target;
        if (evento.key !== 'Enter' || alvo.tagName === 'TEXTAREA' || alvo.tagName === 'BUTTON' || alvo.type === 'submit') return;
        if (atual < ultima) { evento.preventDefault(); continuar(); }
    });

    // Ao salvar, confere todas as etapas (o navegador não alcança campos de etapas escondidas).
    form.addEventListener('submit', function (evento) {
        if (!tipo) { evento.preventDefault(); mostrar(0, true); return; }
        for (var i = 1; i <= ultima; i++) {
            if (!etapaValida(i)) { evento.preventDefault(); return; }
        }
    });

    // ---- estado inicial
    form.classList.add('wizard--ativo');
    listaPassos.hidden = false;
    opcoesTipo.hidden = false;
    campoTipoSelect.hidden = true;
    aplicarTipo();

    var comErro = etapas.findIndex(function (etapa) { return etapa.hasAttribute('data-tem-erro'); });
    if (comErro > 0 || (comErro === 0 && !tipo)) {
        maiorVisitada = ultima;
        mostrar(comErro, false);
    } else if (edicao) {
        maiorVisitada = ultima;
        mostrar(1, false);
    } else if (tipo) {
        mostrar(1, false);
    } else {
        mostrar(0, false);
    }
})();
