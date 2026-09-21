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
})();
