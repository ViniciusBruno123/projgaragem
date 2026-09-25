// Endereço da garagem via mapa embutido (modal, ver _modal_endereco_mapa.html): busca por texto
// OU clique/arraste do marcador pra ajustar o local exato — não é só uma busca de texto, é um
// mapa de verdade que o dono usa pra fincar o pino da garagem.
//
// Usa OpenStreetMap: tiles + Leaflet (visual do mapa) e a API pública Nominatim (busca de texto
// e geocodificação reversa) — tudo gratuito, sem chave nem cadastro. A Nominatim pede uso
// moderado (no máx. ~1 requisição/segundo, sem disparar a cada tecla): por isso a busca espera
// o dono parar de digitar (debounce) antes de consultar.
document.addEventListener('DOMContentLoaded', function () {
    var campos = window.GARAGEM_MAPS_CAMPOS;
    var canvas = document.getElementById('mapa-endereco-canvas');
    var buscaEl = document.getElementById('mapa-busca-endereco');
    var resultadosEl = document.getElementById('mapa-busca-resultados');
    var modalEl = document.getElementById('modal-endereco-mapa');
    if (!campos || !canvas || !modalEl || typeof L === 'undefined') return;

    var campoLat = document.getElementById(campos.lat);
    var campoLng = document.getElementById(campos.lng);
    var campoEndereco = document.getElementById(campos.endereco);

    // Catanduva-SP como centro padrão, pra quem ainda não definiu nenhum local.
    var latAtual = parseFloat(campoLat.value);
    var lngAtual = parseFloat(campoLng.value);
    var temLocal = !isNaN(latAtual) && !isNaN(lngAtual);
    var centro = temLocal ? [latAtual, lngAtual] : [-21.1376, -48.9756];

    var mapa = L.map(canvas).setView(centro, temLocal ? 16 : 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(mapa);
    var marcador = L.marker(centro, { draggable: true }).addTo(mapa);

    function definirLocal(lat, lng, endereco) {
        campoLat.value = lat;
        campoLng.value = lng;
        campoEndereco.value = endereco || '';

        var gatilho = document.getElementById('mapa-endereco-trigger');
        if (gatilho) gatilho.textContent = endereco || (lat.toFixed(6) + ', ' + lng.toFixed(6));
    }

    function moverPara(lat, lng, enderecoConhecido) {
        marcador.setLatLng([lat, lng]);
        mapa.panTo([lat, lng]);
        if (enderecoConhecido !== undefined) {
            definirLocal(lat, lng, enderecoConhecido);
            return;
        }
        // Sem endereço de um resultado de busca (clique/arraste livre no mapa) — descobre pelo
        // geocoding reverso (coordenada -> endereço), pra continuar mostrando um texto legível
        // em vez de só números.
        fetch('https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=' + lat + '&lon=' + lng)
            .then(function (resposta) { return resposta.json(); })
            .then(function (dados) { definirLocal(lat, lng, dados && dados.display_name); })
            .catch(function () { definirLocal(lat, lng, ''); });
    }

    marcador.on('dragend', function () {
        var posicao = marcador.getLatLng();
        moverPara(posicao.lat, posicao.lng);
    });
    mapa.on('click', function (evento) {
        moverPara(evento.latlng.lat, evento.latlng.lng);
    });

    // Busca por texto (Nominatim) com debounce — evita uma requisição a cada tecla digitada.
    var temporizadorBusca = null;
    var controladorBusca = null;
    if (buscaEl && resultadosEl) {
        buscaEl.addEventListener('input', function () {
            var termo = buscaEl.value.trim();
            clearTimeout(temporizadorBusca);
            if (termo.length < 3) {
                resultadosEl.style.display = 'none';
                return;
            }
            temporizadorBusca = setTimeout(function () { buscarEndereco(termo); }, 600);
        });
        document.addEventListener('click', function (evento) {
            if (evento.target !== buscaEl) resultadosEl.style.display = 'none';
        });
    }

    function buscarEndereco(termo) {
        if (controladorBusca) controladorBusca.abort();
        controladorBusca = new AbortController();
        var url = 'https://nominatim.openstreetmap.org/search?format=jsonv2&countrycodes=br&limit=5&q=' + encodeURIComponent(termo);
        fetch(url, { signal: controladorBusca.signal })
            .then(function (resposta) { return resposta.json(); })
            .then(mostrarResultados)
            .catch(function (erro) { if (erro.name !== 'AbortError') resultadosEl.style.display = 'none'; });
    }

    function mostrarResultados(lugares) {
        resultadosEl.innerHTML = '';
        if (!lugares || !lugares.length) {
            resultadosEl.style.display = 'none';
            return;
        }
        lugares.forEach(function (lugar) {
            var item = document.createElement('button');
            item.type = 'button';
            item.className = 'list-group-item list-group-item-action';
            item.textContent = lugar.display_name;
            item.addEventListener('click', function () {
                var lat = parseFloat(lugar.lat);
                var lng = parseFloat(lugar.lon);
                mapa.setZoom(16);
                moverPara(lat, lng, lugar.display_name);
                buscaEl.value = '';
                resultadosEl.style.display = 'none';
            });
            resultadosEl.appendChild(item);
        });
        resultadosEl.style.display = 'block';
    }

    // O mapa nasce dentro de um modal escondido (display:none) — sem isso ele mede 0x0 e
    // renderiza cinza/quebrado. Toda vez que o modal abre, força o Leaflet a recalcular o
    // tamanho e recentralizar no local atual.
    modalEl.addEventListener('shown.bs.modal', function () {
        mapa.invalidateSize();
        mapa.setView(marcador.getLatLng(), mapa.getZoom());
    });
});
