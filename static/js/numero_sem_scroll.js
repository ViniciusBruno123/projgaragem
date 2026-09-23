// Rolar o mouse sobre um <input type="number"> focado muda o valor dele em vez de rolar
// a página (comportamento nativo do Chrome/Edge) — fácil de fazer sem querer, só de passar
// o scroll por cima de um campo em que se clicou antes. No formulário de fotos do veículo
// isso fazia o valor de "Ordem" divergir do pré-preenchido, e o Django passava a exigir a
// foto naquele slot (ver dashboard.views.VeiculoFormsetMixin) mesmo sem o dono ter mexido
// ali de propósito.
//
// Correção padrão: ao rolar com um campo numérico focado, tira o foco dele. Isso não
// bloqueia a rolagem da página (não usa preventDefault) — só evita que ESSE campo receba
// o scroll como se fosse uma seta pra cima/baixo.
(function () {
  'use strict';

  document.addEventListener('wheel', function () {
    var ativo = document.activeElement;
    if (ativo && ativo.tagName === 'INPUT' && ativo.type === 'number') {
      ativo.blur();
    }
  }, { passive: true });
})();
