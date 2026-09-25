// Landing page: seletor "O cliente vê" / "Ele simula" / "Você recebe". Troca o celular (vitrine ao
// vivo, na home ou na página de um veículo, ou o painel de demonstração), a lista de texto e a
// legenda. Sem JS a página continua legível: fica só o lado do cliente.
(function () {
    var palco = document.querySelector('.lp-palco');
    if (palco) {
        var abas = Array.prototype.slice.call(palco.querySelectorAll('[role="tab"]'));
        var telaPainel = palco.querySelector('.lp-tela--painel');
        var iframe = document.getElementById('lp-iframe');
        var legenda = document.getElementById('lp-legenda');

        var mostrar = function (lado, focar) {
            palco.setAttribute('data-lado-ativo', lado);
            var noPainel = lado === 'dono';
            if (telaPainel) telaPainel.setAttribute('aria-hidden', noPainel ? 'false' : 'true');
            if (iframe) {
                // Atrás do painel, o iframe não pode receber foco por teclado.
                if (noPainel) iframe.setAttribute('inert', ''); else iframe.removeAttribute('inert');
                var destino = iframe.getAttribute('data-src-' + lado);
                if (destino && iframe.getAttribute('src') !== destino) iframe.setAttribute('src', destino);
            }

            abas.forEach(function (aba) {
                var ativa = aba.getAttribute('data-lado') === lado;
                aba.setAttribute('aria-selected', ativa ? 'true' : 'false');
                aba.tabIndex = ativa ? 0 : -1;
                var lista = document.getElementById(aba.getAttribute('aria-controls'));
                if (lista) {
                    lista.hidden = !ativa;
                    lista.classList.add('is-troca');
                }
                if (ativa && legenda) legenda.textContent = aba.getAttribute('data-legenda');
                if (ativa && focar) aba.focus();
            });
        };

        abas.forEach(function (aba, indice) {
            aba.addEventListener('click', function () {
                mostrar(aba.getAttribute('data-lado'), false);
            });
            aba.addEventListener('keydown', function (evento) {
                var passo = { ArrowRight: 1, ArrowLeft: -1 }[evento.key];
                if (!passo) return;
                evento.preventDefault();
                var proxima = abas[(indice + passo + abas.length) % abas.length];
                mostrar(proxima.getAttribute('data-lado'), true);
            });
        });
    }

    // Vitrines em miniatura: o iframe tem a largura de um celular (360px) e é reduzido para
    // caber na moldura, mantendo o layout de celular da vitrine.
    var minis = Array.prototype.slice.call(document.querySelectorAll('.lp-mini'));
    var ajustarMinis = function () {
        minis.forEach(function (mini) {
            var quadro = mini.querySelector('iframe');
            if (quadro) quadro.style.transform = 'scale(' + (mini.clientWidth / 360) + ')';
        });
    };
    if (minis.length) {
        ajustarMinis();
        window.addEventListener('resize', ajustarMinis);
    }

    // Reenvio com erro de validação: leva direto ao formulário, que fica abaixo da dobra.
    if (document.querySelector('[data-form-erros]')) {
        var contato = document.getElementById('contato');
        if (contato) contato.scrollIntoView();
    }
})();
