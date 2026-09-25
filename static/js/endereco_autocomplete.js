// Endereço da garagem via mapa embutido (modal, ver _modal_endereco_mapa.html): busca por texto
// (Places) OU clique/arraste do marcador pra ajustar o local exato — não é só uma busca de texto,
// é um mapa de verdade que o dono usa pra fincar o pino da garagem.
//
// window.iniciarAutocompleteEndereco é o "callback" do script da Google Maps API — só roda
// depois que a lib "places" termina de carregar (ver o <script async ...&callback=...>).
window.iniciarAutocompleteEndereco = async function () {
    var campos = window.GARAGEM_MAPS_CAMPOS;
    var canvas = document.getElementById('mapa-endereco-canvas');
    var buscaEl = document.getElementById('mapa-busca-endereco');
    var modalEl = document.getElementById('modal-endereco-mapa');
    if (!campos || !canvas || !modalEl) return;

    await google.maps.importLibrary('places');
    await google.maps.importLibrary('geocoding');

    // Catanduva-SP como centro padrão, pra quem ainda não definiu nenhum local.
    var latAtual = parseFloat(document.getElementById(campos.lat).value);
    var lngAtual = parseFloat(document.getElementById(campos.lng).value);
    var temLocal = !isNaN(latAtual) && !isNaN(lngAtual);
    var centro = temLocal ? { lat: latAtual, lng: lngAtual } : { lat: -21.1376, lng: -48.9756 };

    var mapa = new google.maps.Map(canvas, { center: centro, zoom: temLocal ? 16 : 13 });
    var marcador = new google.maps.Marker({ position: centro, map: mapa, draggable: true });
    var geocoder = new google.maps.Geocoder();

    function definirLocal(lat, lng, endereco, placeId) {
        document.getElementById(campos.lat).value = lat;
        document.getElementById(campos.lng).value = lng;
        document.getElementById(campos.endereco).value = endereco || '';
        document.getElementById(campos.placeId).value = placeId || '';

        var gatilho = document.getElementById('mapa-endereco-trigger');
        if (gatilho) gatilho.textContent = endereco || (lat.toFixed(6) + ', ' + lng.toFixed(6));
    }

    function moverPara(lat, lng) {
        var posicao = { lat: lat, lng: lng };
        marcador.setPosition(posicao);
        mapa.panTo(posicao);
        // Sem endereço de um resultado de busca — descobre pelo geocoding reverso (coordenada
        // -> endereço), pra continuar mostrando um texto legível em vez de só números.
        geocoder.geocode({ location: posicao }, function (resultados, status) {
            var endereco = (status === 'OK' && resultados[0]) ? resultados[0].formatted_address : '';
            definirLocal(lat, lng, endereco, '');
        });
    }

    marcador.addListener('dragend', function (evento) {
        moverPara(evento.latLng.lat(), evento.latLng.lng());
    });
    mapa.addListener('click', function (evento) {
        moverPara(evento.latLng.lat(), evento.latLng.lng());
    });

    if (buscaEl) {
        buscaEl.componentRestrictions = { country: 'br' };
        buscaEl.addEventListener('gmp-select', async function (evento) {
            var lugar = evento.placePrediction.toPlace();
            await lugar.fetchFields({ fields: ['formattedAddress', 'location', 'id'] });
            if (!lugar.location) return;

            var lat = lugar.location.lat();
            var lng = lugar.location.lng();
            marcador.setPosition({ lat: lat, lng: lng });
            mapa.panTo({ lat: lat, lng: lng });
            mapa.setZoom(16);
            definirLocal(lat, lng, lugar.formattedAddress, lugar.id);
        });
    }

    // O mapa nasce dentro de um modal escondido (display:none) — sem isso ele mede 0x0 e
    // renderiza cinza. Toda vez que o modal abre, força o Maps a recalcular o tamanho e
    // recentralizar no local atual.
    modalEl.addEventListener('shown.bs.modal', function () {
        google.maps.event.trigger(mapa, 'resize');
        mapa.setCenter(marcador.getPosition());
    });
};
