// Landing page: seletor "O cliente vê" / "Ele abre o anúncio" / "Ele simula" / "Ele propõe" /
// "Você recebe". Troca o celular (vitrine ao vivo, na home, no anúncio, no simulador ou no
// formulário de proposta, ou o painel de demonstração) e a lista de texto. Sem JS a página
// continua legível: fica só o lado do cliente.
(function () {
    var palco = document.querySelector('.lp-palco');
    if (palco) {
        var abas = Array.prototype.slice.call(palco.querySelectorAll('[role="tab"]'));
        var telaPainel = palco.querySelector('.lp-tela--painel');
        var iframe = document.getElementById('lp-iframe');

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

    // Celular do herói: o iframe sempre renderiza a 360x800 (20:9) e é reduzido para caber na
    // moldura — sem isso, o iframe herdava a largura da moldura (que muda com a altura da tela)
    // e a vitrine renderizava um layout mobile diferente do que aparece num celular de verdade.
    var celular = document.querySelector('.lp-celular');
    var iframeHero = document.getElementById('lp-iframe');
    var ajustarHero = function () {
        if (iframeHero) iframeHero.style.transform = 'scale(' + (celular.clientWidth / 360) + ')';
    };
    if (celular && iframeHero) {
        ajustarHero();
        window.addEventListener('resize', ajustarHero);
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
