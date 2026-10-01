// Corte de foto no upload (logo, capa e fotos de veículo) — usa o Cropper.js (CDN) para o
// dono escolher exatamente o que aparece, já na proporção real de exibição.
//
// Sem Cropper.js ou Bootstrap carregados (bloqueio de CDN, por exemplo), a função inteira
// é pulada e o campo de arquivo funciona do jeito normal: o corte é só uma etapa a mais
// antes do envio, o servidor sempre redimensiona e comprime de qualquer forma
// (vehicles/imagens.py) — então essa é uma melhoria, não uma dependência.
//
// Campo com data-cortar-par (hoje só o banner, ver dashboard/forms.py BannerForm): ao
// escolher o arquivo, a fila de corte ganha uma SEGUNDA etapa, na proporção do campo
// apontado por data-cortar-par — mesma foto, dois cortes em sequência, sem pedir um
// segundo upload. O campo-par fica escondido (não abre corte sozinho) e só recebe o
// resultado programaticamente.
(function () {
  'use strict';

  if (typeof Cropper === 'undefined' || typeof bootstrap === 'undefined') return;

  var modalEl = document.getElementById('modal-cortar-foto');
  if (!modalEl) return;

  var imagemEl = document.getElementById('cortar-foto-imagem');
  var botaoConfirmar = document.getElementById('cortar-foto-confirmar');
  var tituloEl = document.getElementById('modal-cortar-foto-titulo');
  var modal = new bootstrap.Modal(modalEl);
  var cropper = null;
  var urlObjeto = null;
  var confirmado = false;
  var etapas = [];        // fila de <input> desta sequência (1 ou 2 campos)
  var etapaAtual = 0;
  var nomeBase = null;    // nome do arquivo original, sem extensão

  // O tipo do veículo (moto/carro) decide a proporção do corte — mesma regra do
  // static/css/site.css (.foto-moto / .foto-carro). Fotos de logo não têm um "encaixe"
  // fixo (a logo aparece inteira, object-fit: contain), então o corte fica livre.
  function razaoDoInput(input) {
    var modo = input.dataset.cortar;
    if (modo === 'veiculo') {
      var tipoSelect = document.getElementById('id_tipo');
      var tipo = tipoSelect ? tipoSelect.value : 'moto';
      return tipo === 'carro' ? 4 / 3 : 3 / 4;
    }
    if (!modo || modo === 'livre') return NaN;
    var partes = modo.split('/');
    return Number(partes[0]) / Number(partes[1]);
  }

  function limparUrlObjeto() {
    if (urlObjeto) {
      URL.revokeObjectURL(urlObjeto);
      urlObjeto = null;
    }
  }

  function atualizarPreviaDoInput(input, urlImagem) {
    var previa = input.nextElementSibling;
    if (!previa || !previa.classList || !previa.classList.contains('pre-visualizacao-corte')) {
      previa = document.createElement('img');
      previa.className = 'pre-visualizacao-corte';
      input.insertAdjacentElement('afterend', previa);
    }
    previa.src = urlImagem;
  }

  function abrirEtapa(indice) {
    etapaAtual = indice;
    var input = etapas[etapaAtual];
    if (cropper) cropper.destroy();
    cropper = new Cropper(imagemEl, {
      aspectRatio: razaoDoInput(input),
      viewMode: 1,
      autoCropArea: 1,
      responsive: true,
      background: false,
    });
    var titulo = input.dataset.cortarTitulo || 'Ajustar foto';
    var ultima = etapaAtual === etapas.length - 1;
    tituloEl.textContent = etapas.length > 1 ? titulo + ' (' + (etapaAtual + 1) + '/' + etapas.length + ')' : titulo;
    botaoConfirmar.textContent = ultima ? 'Usar esse corte' : 'Usar esse corte e continuar';
  }

  // Campos-par (data-cortar-par aponta pro id deles) não abrem corte sozinhos — entram na
  // fila quando o campo principal é escolhido, abaixo.
  var idsDeCamposPar = {};
  document.querySelectorAll('input[type="file"][data-cortar-par]').forEach(function (input) {
    idsDeCamposPar[input.dataset.cortarPar] = true;
  });

  document.querySelectorAll('input[type="file"][data-cortar]').forEach(function (input) {
    if (idsDeCamposPar[input.id]) return;

    input.addEventListener('change', function () {
      var arquivo = input.files && input.files[0];
      if (!arquivo) return;

      etapas = [input];
      var idPar = input.dataset.cortarPar;
      var inputPar = idPar ? document.getElementById(idPar) : null;
      if (inputPar) etapas.push(inputPar);

      nomeBase = arquivo.name.replace(/\.[^./\\]+$/, '');
      confirmado = false;
      limparUrlObjeto();
      urlObjeto = URL.createObjectURL(arquivo);
      imagemEl.src = urlObjeto;
      modal.show();
    });
  });

  // Cropper.js precisa que a imagem já esteja com tamanho definido na tela — por isso
  // inicializa só depois do modal terminar de aparecer, não no "change" do campo.
  modalEl.addEventListener('shown.bs.modal', function () {
    abrirEtapa(0);
  });

  modalEl.addEventListener('hidden.bs.modal', function () {
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
    limparUrlObjeto();
    // Fechou sem terminar a fila (X, Cancelar, Esc): não manda nenhuma foto da sequência
    // pela metade — limpa todos os campos envolvidos, inclusive o que já tinha corte confirmado.
    if (!confirmado) {
      etapas.forEach(function (input) {
        input.value = '';
        var previa = input.nextElementSibling;
        if (previa && previa.classList && previa.classList.contains('pre-visualizacao-corte')) {
          previa.remove();
        }
      });
    }
    etapas = [];
    etapaAtual = 0;
  });

  botaoConfirmar.addEventListener('click', function () {
    if (!cropper) return;
    var input = etapas[etapaAtual];

    cropper.getCroppedCanvas({ imageSmoothingQuality: 'high' }).toBlob(function (blob) {
      if (!blob) return;

      var sufixo = etapas.length > 1 ? '-' + (etapaAtual + 1) : '';
      var arquivoCortado = new File([blob], (nomeBase || 'foto') + sufixo + '.jpg', { type: 'image/jpeg' });
      var transferencia = new DataTransfer();
      transferencia.items.add(arquivoCortado);
      input.files = transferencia.files;
      atualizarPreviaDoInput(input, URL.createObjectURL(arquivoCortado));

      if (etapaAtual < etapas.length - 1) {
        abrirEtapa(etapaAtual + 1);
      } else {
        confirmado = true;
        modal.hide();
      }
    }, 'image/jpeg', 0.92);
  });
})();
