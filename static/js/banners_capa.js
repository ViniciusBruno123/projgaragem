// Alterna a camada .active entre os banners da faixa superior (ver .site-header-banners em
// static/css/site.css e o header em storefront/_base_vitrine.html). Só é carregado quando a
// garagem tem mais de um banner — com um banner só não tem nada pra alternar.
(function () {
  'use strict';

  var reduzMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduzMovimento) return; // primeiro banner já nasce .active; fica parado nele.

  document.querySelectorAll('.site-header-banners').forEach(function (container) {
    var camadas = container.querySelectorAll('.site-header-banner-camada');
    if (camadas.length < 2) return;

    var intervalo = parseInt(container.dataset.intervalo, 10) || 3000;
    var atual = 0;

    setInterval(function () {
      camadas[atual].classList.remove('active');
      atual = (atual + 1) % camadas.length;
      camadas[atual].classList.add('active');
    }, intervalo);
  });
})();
