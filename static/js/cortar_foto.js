// Corte de foto no upload (logo, capa e fotos de veículo) — usa o Cropper.js (CDN) para o
// dono escolher exatamente o que aparece, já na proporção real de exibição.
//
// Sem Cropper.js ou Bootstrap carregados (bloqueio de CDN, por exemplo), a função inteira
// é pulada e o campo de arquivo funciona do jeito normal: o corte é só uma etapa a mais
// antes do envio, o servidor sempre redimensiona e comprime de qualquer forma
// (vehicles/imagens.py) — então essa é uma melhoria, não uma dependência.
(function () {
  'use strict';

  if (typeof Cropper === 'undefined' || typeof bootstrap === 'undefined') return;

  var modalEl = document.getElementById('modal-cortar-foto');
  if (!modalEl) return;

  var imagemEl = document.getElementById('cortar-foto-imagem');
  var botaoConfirmar = document.getElementById('cortar-foto-confirmar');
  var modal = new bootstrap.Modal(modalEl);
  var cropper = null;
  var inputAtivo = null;
  var urlObjeto = null;
  var confirmado = false;

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

  document.querySelectorAll('input[type="file"][data-cortar]').forEach(function (input) {
    input.addEventListener('change', function () {
      var arquivo = input.files && input.files[0];
      if (!arquivo) return;

      inputAtivo = input;
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
    if (cropper) cropper.destroy();
    cropper = new Cropper(imagemEl, {
      aspectRatio: razaoDoInput(inputAtivo),
      viewMode: 1,
      autoCropArea: 1,
      responsive: true,
      background: false,
    });
  });

  modalEl.addEventListener('hidden.bs.modal', function () {
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
    limparUrlObjeto();
    // Fechou sem confirmar (X, Cancelar, Esc): não manda a foto sem corte por engano.
    if (inputAtivo && !confirmado) {
      inputAtivo.value = '';
    }
    inputAtivo = null;
  });

  botaoConfirmar.addEventListener('click', function () {
    if (!cropper || !inputAtivo) return;

    cropper.getCroppedCanvas({ imageSmoothingQuality: 'high' }).toBlob(function (blob) {
      if (!blob) return;

      var nomeOriginal = inputAtivo.files[0].name.replace(/\.[^./\\]+$/, '') + '.jpg';
      var arquivoCortado = new File([blob], nomeOriginal, { type: 'image/jpeg' });
      var transferencia = new DataTransfer();
      transferencia.items.add(arquivoCortado);
      inputAtivo.files = transferencia.files;

      atualizarPreviaDoInput(inputAtivo, URL.createObjectURL(arquivoCortado));

      confirmado = true;
      modal.hide();
    }, 'image/jpeg', 0.92);
  });
})();
