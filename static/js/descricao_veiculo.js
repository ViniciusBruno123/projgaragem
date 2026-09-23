// "Leia mais" da descrição do veículo: o botão só fica visível se o texto realmente
// estourar o limite de linhas do CSS (.descricao-veiculo) — um texto curto que já cabe
// inteiro não precisa de botão nenhum.
(function () {
  'use strict';

  var caixa = document.getElementById('descricao-veiculo');
  var botao = document.getElementById('descricao-leia-mais');
  if (!caixa || !botao) return;

  if (caixa.scrollHeight <= caixa.clientHeight + 2) {
    botao.remove();
    return;
  }

  botao.addEventListener('click', function () {
    var expandida = caixa.classList.toggle('expandida');
    botao.textContent = expandida ? 'Leia menos' : 'Leia mais';
  });
})();
