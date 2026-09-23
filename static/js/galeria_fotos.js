// Galeria de miniaturas da página do veículo: clicar numa miniatura troca a foto em
// destaque (o Bootstrap já faz isso sozinho, via data-bs-slide-to) — este script só
// cuida de destacar a miniatura correspondente conforme a foto muda, inclusive pelas
// setas do carrossel ou passando o dedo no celular, não só pelo clique na miniatura.
(function () {
  'use strict';

  document.querySelectorAll('.galeria-miniaturas').forEach(function (galeria) {
    var carrosselEl = document.getElementById('carouselFotos');
    if (!carrosselEl) return;
    var miniaturas = galeria.querySelectorAll('.galeria-miniatura');

    carrosselEl.addEventListener('slide.bs.carousel', function (evento) {
      miniaturas.forEach(function (miniatura, indice) {
        miniatura.classList.toggle('active', indice === evento.to);
      });
      var atual = miniaturas[evento.to];
      if (atual) atual.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    });
  });
})();
