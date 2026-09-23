// Sincroniza a fonte do próprio <select> com a opção escolhida. O navegador já estiliza cada
// <option> na fonte que ela representa (ver dashboard.forms.SelectComPreviaDeFonte), mas só
// aplica isso na lista aberta — a caixa fechada do <select> sempre usa a fonte do elemento em
// si. Sem este script, a "Aa" só aparece quando a lista está aberta.
(function () {
  'use strict';

  document.querySelectorAll('select[data-previa-fonte]').forEach(function (select) {
    function sincronizar() {
      var opcaoEscolhida = select.options[select.selectedIndex];
      select.style.fontFamily = opcaoEscolhida ? opcaoEscolhida.style.fontFamily : '';
    }
    select.addEventListener('change', sincronizar);
    sincronizar();
  });
})();
