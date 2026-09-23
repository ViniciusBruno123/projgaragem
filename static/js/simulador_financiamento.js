// Simulador de financiamento: "Calcular" busca só o resultado (fetch) e troca o miolo
// da caixa no lugar, em vez de recarregar a página inteira e jogar a rolagem pro topo.
//
// Delegação de evento em document (não no <form> direto): o innerHTML da caixa é trocado
// a cada cálculo, então o <form> de dentro é um elemento novo a cada vez — um listener
// preso nele se perderia. Sem JavaScript, o <form> continua com method="get" apontando
// pra própria página do veículo, então tudo funciona igual a antes (só recarrega a página).
(function () {
  'use strict';

  var caixa = document.getElementById('simulador-financiamento');
  if (!caixa) return;

  var urlParcial = caixa.dataset.urlParcial;

  document.addEventListener('submit', function (evento) {
    var form = evento.target;
    if (!caixa.contains(form)) return;
    evento.preventDefault();

    var parametros = new URLSearchParams(new FormData(form)).toString();
    var botao = form.querySelector('button[type="submit"]');
    if (botao) botao.disabled = true;

    fetch(urlParcial + '?' + parametros, { headers: { 'X-Requested-With': 'fetch' } })
      .then(function (resposta) {
        if (!resposta.ok) throw new Error('resposta ' + resposta.status);
        return resposta.text();
      })
      .then(function (html) {
        caixa.innerHTML = html;
        history.replaceState(null, '', window.location.pathname + '?' + parametros);
      })
      .catch(function () {
        // Rede fora do ar ou erro inesperado: cai pro comportamento normal (recarrega
        // a página), que é o que aconteceria sem este script.
        form.submit();
      });
  });
})();
