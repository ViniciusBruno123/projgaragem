// Carrossel dos destaques: setas com rolagem suave e avanço automático.
(function () {
  'use strict';

  var reduzMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function iniciar(carrossel) {
    var trilho = carrossel.querySelector('.carrossel-trilho');
    var anterior = carrossel.querySelector('[data-carrossel-anterior]');
    var proximo = carrossel.querySelector('[data-carrossel-proximo]');
    var intervalo = parseInt(carrossel.dataset.intervalo, 10) || 10000;
    var timer = null;
    var pausado = false;

    function cabeTudo() {
      return trilho.scrollWidth <= trilho.clientWidth + 1;
    }

    function passo() {
      var item = trilho.querySelector('.carrossel-item');
      var espaco = parseFloat(getComputedStyle(trilho).columnGap) || 0;
      return item.getBoundingClientRect().width + espaco;
    }

    function ir(direcao) {
      var comportamento = reduzMovimento ? 'auto' : 'smooth';
      var noFim = trilho.scrollLeft + trilho.clientWidth >= trilho.scrollWidth - 2;
      var noInicio = trilho.scrollLeft <= 2;

      if (direcao > 0 && noFim) {
        trilho.scrollTo({ left: 0, behavior: comportamento });
      } else if (direcao < 0 && noInicio) {
        trilho.scrollTo({ left: trilho.scrollWidth, behavior: comportamento });
      } else {
        trilho.scrollBy({ left: direcao * passo(), behavior: comportamento });
      }
    }

    function parar() {
      clearInterval(timer);
      timer = null;
    }

    function agendar() {
      parar();
      if (reduzMovimento || cabeTudo()) return;
      timer = setInterval(function () {
        if (!pausado && !document.hidden) ir(1);
      }, intervalo);
    }

    function atualizar() {
      var curto = cabeTudo();
      carrossel.classList.toggle('carrossel--curto', curto);
      if (curto) parar();
      else if (!timer) agendar();
    }

    anterior.addEventListener('click', function () { ir(-1); agendar(); });
    proximo.addEventListener('click', function () { ir(1); agendar(); });

    carrossel.addEventListener('pointerenter', function () { pausado = true; });
    carrossel.addEventListener('pointerleave', function () { pausado = false; agendar(); });
    carrossel.addEventListener('focusin', function () { pausado = true; });
    carrossel.addEventListener('focusout', function () { pausado = false; agendar(); });

    window.addEventListener('resize', atualizar);
    atualizar();
  }

  document.querySelectorAll('[data-carrossel]').forEach(iniciar);

  // No celular o filtro começa recolhido (se não houver filtro ativo), para os
  // destaques aparecerem na primeira tela; no desktop fica sempre aberto.
  var celular = window.matchMedia('(max-width: 767.98px)');
  document.querySelectorAll('details[data-fechar-no-mobile]').forEach(function (detalhes) {
    function ajustar() { detalhes.open = !celular.matches; }
    ajustar();
    celular.addEventListener('change', ajustar);
  });

  // Prévia das próximas fotos ao passar o mouse no card. As URLs já vêm na página
  // (texto, quase sem peso); a imagem em si só é baixada se alguém passar o mouse de
  // verdade — numa vitrine com dezenas de veículos, ninguém paira sobre todos ao mesmo
  // tempo, então isso não vira "carregar tudo de uma vez".
  var INTERVALO_PREVIA_MS = 2200; // tempo que cada foto fica na tela
  var DURACAO_FADE_MS = 280; // duração do esmaecer entre uma foto e outra
  document.querySelectorAll('.photo-link[data-fotos-extra]').forEach(function (link) {
    if (reduzMovimento) return;
    var urls = link.dataset.fotosExtra.split('|').filter(Boolean);
    var img = link.querySelector('.photo');
    if (!urls.length || !img) return;

    var original = img.dataset.fotoPrincipal || img.src;
    var indice = 0;
    var timer = null;

    // Pré-carrega a próxima foto antes de esmaecer a atual, pra não trocar pra uma
    // imagem em branco enquanto ela ainda está baixando (rede lenta).
    function trocarComFade(novaUrl) {
      var pronta = new Image();
      pronta.onload = function () {
        img.style.opacity = '0';
        setTimeout(function () {
          img.src = novaUrl;
          img.style.opacity = '1';
        }, DURACAO_FADE_MS);
      };
      pronta.src = novaUrl;
    }

    function mostrar(i) {
      indice = i;
      trocarComFade(indice === 0 ? original : urls[indice - 1]);
    }

    function comecar(evento) {
      if (evento.pointerType === 'touch') return; // celular não tem "passar o mouse"
      timer = setInterval(function () { mostrar((indice + 1) % (urls.length + 1)); }, INTERVALO_PREVIA_MS);
    }

    function parar() {
      clearInterval(timer);
      mostrar(0);
    }

    link.addEventListener('pointerenter', comecar);
    link.addEventListener('pointerleave', parar);
    link.addEventListener('focusout', parar);
  });
})();
