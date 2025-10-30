$(document).ready(function() {

    $('#municipio-select').prop('disabled', true);
    $('#resp-regiao-select').prop('disabled', true);
    $('#regional-select').prop('disabled', true);

    // 🔹 Função auxiliar para mostrar o "loading" dentro do select
    function showLoading($select, text = "Carregando...") {
        $select.prop('disabled', true)
               .empty()
               .append(`<option>${text}</option>`);
    }

    // 🔹 Função auxiliar para preencher e habilitar um select
    function populateSelect($select, items, placeholder, valueKey = 'id', textKey = 'nome') {
        $select.prop('disabled', false)
               .empty()
               .append(`<option value="">${placeholder}</option>`);
        $.each(items, function(index, item) {
            $select.append(`<option value="${item[valueKey]}">${item[textKey]}</option>`);
        });
    }

    // 🔹 EDP → carrega regionais e desativa os outros
    $('#edp-select').change(function() {
        var edpId = $(this).val();

        // Resetar os selects dependentes
        $('#regional-select').prop('disabled', true).empty().append('<option>Selecione uma regional...</option>');
        $('#municipio-select').prop('disabled', true).empty().append('<option>Selecione um município...</option>');
        $('#resp-regiao-select').prop('disabled', true).empty().append('<option>Selecione um responsável...</option>');

        if (edpId) {
            // Mostra loading em "regional"
            showLoading($('#regional-select'));

            // Busca regionais
            $.get('/api/regionais/' + edpId, function(data) {
                populateSelect($('#regional-select'), data.regionais, 'Selecione uma regional...');
            }).fail(function() {
                $('#regional-select').empty().append('<option>Erro ao carregar regionais</option>');
            }).always(function() {
                $('#regional-select').prop('disabled', false);
                $('#resp-regiao-select').prop('disabled', true).empty().append('<option>Selecione um responsável...</option>');
                $('#municipio-select').prop('disabled', true).empty().append('<option>Selecione um município...</option>');;
            });
        }
    });

    // 🔹 Regional → carrega municípios e responsáveis
    $('#regional-select').change(function() {
        var regionalId = $(this).val();

        // Resetar selects dependentes
        $('#municipio-select').prop('disabled', true).empty().append('<option>Selecione um município...</option>');
        $('#resp-regiao-select').prop('disabled', true).empty().append('<option>Selecione um responsável...</option>');

        if (regionalId) {
            // Loading
            showLoading($('#municipio-select'));
            showLoading($('#resp-regiao-select'), "Carregando responsáveis...");

            // Buscar municípios
            $.get('/api/municipios_by_regional/' + regionalId, function(data) {
                populateSelect($('#municipio-select'), data.municipios, 'Selecione um município...');
            }).fail(function() {
                $('#municipio-select').empty().append('<option>Erro ao carregar municípios</option>');
            }).always(function() {
                $('#municipio-select').prop('disabled', false);
                $('#resp-regiao-select').prop('disabled', false);
            });

            // Buscar responsáveis
            $.get('/api/resp_regioes/' + regionalId, function(data) {
                populateSelect($('#resp-regiao-select'), data.responsaveis, 'Selecione um responsável...');
            }).fail(function() {
                $('#resp-regiao-select').empty().append('<option>Erro ao carregar responsáveis</option>');
            }).always(function() {
                $('#resp-regiao-select').prop('disabled', false);
            });
        }
    });

    // 🔹 Município → apenas habilita se selecionado (sem carregar nada)
    $('#municipio-select').change(function() {
        var municipioId = $(this).val();
        if (municipioId) {
            $('#resp-regiao-select').prop('disabled', false);
        }
    });

    // Valores iniciais do banco ou padrão
    var initialLat = parseFloat($('#latitude').val()) || -23.550520;
    var initialLng = parseFloat($('#longitude').val()) || -46.633309;

    var map = L.map('map').setView([initialLat, initialLng], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    var marker = L.marker([initialLat, initialLng], {draggable: true}).addTo(map);

    // Tenta centralizar no local atual do usuário se os campos estiverem vazios
    if (!$('#latitude').val() || !$('#longitude').val()) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                var lat = position.coords.latitude;
                var lng = position.coords.longitude;

                $('#latitude').val(lat.toFixed(8));
                $('#longitude').val(lng.toFixed(8));

                marker.setLatLng([lat, lng]);
                map.setView([lat, lng], 15);
            });
        }
    }

    // Atualiza campos ao arrastar marcador
    marker.on('dragend', function(e) {
        var pos = marker.getLatLng();
        $('#latitude').val(pos.lat.toFixed(8));
        $('#longitude').val(pos.lng.toFixed(8));
    });

    // Atualiza marcador e campos ao clicar no mapa
    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        $('#latitude').val(e.latlng.lat.toFixed(8));
        $('#longitude').val(e.latlng.lng.toFixed(8));
    });

    // Função para atualizar marcador a partir dos inputs
    function updateMarkerFromInput() {
        var lat = parseFloat($('#latitude').val());
        var lng = parseFloat($('#longitude').val());
        if (!isNaN(lat) && !isNaN(lng)) {
            marker.setLatLng([lat, lng]);
            map.setView([lat, lng], 13);
        }
    }

    //$('#latitude, #longitude').on('change', updateMarkerFromInput);

    // Corrige mapa ao abrir a aba
    $('#localizacao-tab').on('shown.bs.tab', function() {
        map.invalidateSize();
    });

    $('#municipio-select').change(function() {
        var nomeMunicipio = $('#municipio-select option:selected').text();
        var nomeEstado = $('#edp-select option:selected').text();

        if (nomeMunicipio) {
            // Buscar todos os municípios do Brasil
            $.getJSON('https://servicodados.ibge.gov.br/api/v1/localidades/estados/' + nomeEstado + '/municipios', function(data) {
                // Procurar pelo município escolhido (comparação case-insensitive)
                var municipio = data.find(function(m) {
                    return removerAcentos(m.nome) === removerAcentos(nomeMunicipio);
                });
                if (municipio) {

                    $.getJSON('https://servicodados.ibge.gov.br/api/v4/malhas/municipios/' + municipio.id + '/metadados', function(data) {
                        var data = data[0]
                        var lat = (data.centroide.latitude !== undefined ? data.centroide.latitude : -23.550520);
                        var lng = (data.centroide.longitude !== undefined ? data.centroide.longitude : -46.633309);

                        var popupContent = `
                            <div style="
                                width: 280px;
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                color: #333;
                                line-height: 1.4;
                                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                                border-radius: 12px;
                                padding: 0;
                                overflow: hidden;
                                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                            ">
                                <!-- Header -->
                                <div style="
                                    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                                    color: white;
                                    padding: 16px;
                                    text-align: center;
                                    position: relative;
                                ">
                                    <div style="
                                        position: absolute;
                                        top: -10px;
                                        right: -10px;
                                        width: 40px;
                                        height: 40px;
                                        background: rgba(255,255,255,0.2);
                                        border-radius: 50%;
                                        opacity: 0.3;
                                    "></div>
                                    <h3 style="
                                        margin: 0;
                                        font-size: 18px;
                                        font-weight: 600;
                                        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                                    ">📍 ${municipio.nome}</h3>
                                    <p style="
                                        margin: 4px 0 0 0;
                                        font-size: 13px;
                                        opacity: 0.9;
                                        font-weight: 400;
                                    ">${municipio.microrregiao.mesorregiao.UF.nome}</p>
                                </div>

                                <!-- Content -->
                                <div style="padding: 16px;">
                                    <!-- Info Grid -->
                                    <div style="
                                        display: grid;
                                        gap: 12px;
                                        margin-bottom: 16px;
                                    ">
                                        <div style="
                                            display: grid;
                                            grid-template-columns: 1fr 1fr;
                                            gap: 8px;
                                        ">
                                            <div style="
                                                background: white;
                                                padding: 10px;
                                                border-radius: 6px;
                                                text-align: center;
                                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                            ">
                                                <div style="
                                                    font-size: 10px;
                                                    color: #6b7280;
                                                    text-transform: uppercase;
                                                    font-weight: 600;
                                                    margin-bottom: 2px;
                                                ">Latitude</div>
                                                <div style="
                                                    font-size: 12px;
                                                    color: #374151;
                                                    font-weight: 500;
                                                    font-family: 'Courier New', monospace;
                                                ">${lat.toFixed(6)}</div>
                                            </div>
                                            <div style="
                                                background: white;
                                                padding: 10px;
                                                border-radius: 6px;
                                                text-align: center;
                                                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                            ">
                                                <div style="
                                                    font-size: 10px;
                                                    color: #6b7280;
                                                    text-transform: uppercase;
                                                    font-weight: 600;
                                                    margin-bottom: 2px;
                                                ">Longitude</div>
                                                <div style="
                                                    font-size: 12px;
                                                    color: #374151;
                                                    font-weight: 500;
                                                    font-family: 'Courier New', monospace;
                                                ">${lng.toFixed(6)}</div>
                                            </div>
                                        </div>

                                        <div style="
                                            background: white;
                                            padding: 12px;
                                            border-radius: 8px;
                                            border-left: 4px solid #f59e0b;
                                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                        ">
                                            <div style="
                                                font-size: 11px;
                                                color: #6b7280;
                                                text-transform: uppercase;
                                                font-weight: 600;
                                                margin-bottom: 2px;
                                                letter-spacing: 0.5px;
                                            ">Área Total</div>
                                            <div style="
                                                font-size: 14px;
                                                color: #374151;
                                                font-weight: 600;
                                            ">${data.area.dimensao.toLocaleString('pt-BR')} ${data.area.unidade.nome}</div>
                                        </div>
                                    </div>

                                    <!-- Região Limítrofe -->
                                    <div style="
                                        background: white;
                                        padding: 12px;
                                        border-radius: 8px;
                                        border-left: 4px solid #8b5cf6;
                                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                                    ">
                                        <div style="
                                            font-size: 11px;
                                            color: #6b7280;
                                            text-transform: uppercase;
                                            font-weight: 600;
                                            margin-bottom: 8px;
                                            letter-spacing: 0.5px;
                                            display: flex;
                                            align-items: center;
                                            gap: 4px;
                                        ">
                                            <span>🗺️</span> Região Limítrofe
                                        </div>
                                        <div style="
                                            max-height: 100px;
                                            overflow-y: auto;
                                            padding-right: 4px;
                                        ">
                                            ${data["regiao-limitrofe"].map((p, index) => `
                                                <div style="
                                                    background: #f8fafc;
                                                    padding: 6px 8px;
                                                    margin-bottom: 4px;
                                                    border-radius: 4px;
                                                    font-size: 11px;
                                                    color: #475569;
                                                    border: 1px solid #e2e8f0;
                                                ">
                                                    <span style="font-weight: 500;">Ponto ${index + 1}:</span>
                                                    <span style="font-family: 'Courier New', monospace;">
                                                        ${p.latitude.toFixed(4)}, ${p.longitude.toFixed(4)}
                                                    </span>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;

                        // Atualiza marcador e mapa
                        marker.setLatLng([lat, lng]);
                        marker.bindPopup(popupContent);
                        marker.openPopup();
                        map.setView([lat, lng], 12);

                        // Atualiza campos do formulário
                        $('#latitude').val(lat.toFixed(8));
                        $('#longitude').val(lng.toFixed(8));

                    }).fail(function() {
                        console.error("Erro ao buscar metadados do municipio");
                        });

                } else {
                    console.error("Município não encontrado na API do IBGE");
                }
            }).fail(function() {
                console.error("Erro ao buscar municípios");
            });
        }
    });

    // Validação de coordenadas
//    $('#latitude_cliente, #longitude_cliente').on('input', function() {
//        var val = parseFloat($(this).val());
//        var field = $(this).attr('id');
//
//        if (field === 'latitude_cliente' && (val < -90 || val > 90)) {
//            $(this).addClass('is-invalid');
//        } else if (field === 'longitude_cliente' && (val < -180 || val > 180)) {
//            $(this).addClass('is-invalid');
//        } else {
//            $(this).removeClass('is-invalid');
//        }
//    });

   /**
     * Converte automaticamente valores de #latitude e #longitude para graus decimais.
     * Reconhece decimal, DMS e UTM textual.
     * Zona UTM: 23S (SP) ou 24S (ES), conforme #edp-select.
     */

     function print(texto) {
        console.log(texto)
     }

   function normalizarCoordenadas() {
      const edpText = ($('#edp-select option:selected').text() || '').toUpperCase();
      const zone = edpText.includes('SP') ? 23 : 24; // SP -> 23S, ES -> 24S
      const hemisphere = 'S';

      let latStr = $('#latitude').val();
      let lonStr = $('#longitude').val();



      //if (!latStr || !lonStr) return; // precisa dos dois para decidir

      // normaliza vírgula e espaços
      latStr = latStr.replace(/,/g, '.').replace(/\s+/g, ' ');
      lonStr = lonStr.replace(/,/g, '.').replace(/\s+/g, ' ');

      console.log("latStr: " + latStr)
      console.log("lonStr: " + lonStr)


      const bothUTM = isLikelyUTMPair(latStr, lonStr);
      const bothGeo = isLikelyGeoPair(latStr, lonStr);

      console.log("bothUTM: " + bothUTM)


      if (bothGeo) {
        const lat = parseCoordinate(latStr, true)
        const lon = parseCoordinate(lonStr, false)
        console.log("bothGeo: "+ bothGeo + " lat: " + lat + " lon: " + lon)
        $('#latitude').val(lat.toFixed(8));
        $('#longitude').val(lon.toFixed(8));
        updateMarkerFromInput()
        return;

      }

      if (bothUTM) {
        // Decide qual é easting e qual é northing (com tolerância por inversão)
        let easting, northing;

        // Heurística por magnitude: easting ~ 160000..834000 | northing ~ 0..10,000,000
        const n1 = parseFloat(latStr);
        const n2 = parseFloat(lonStr);

        if (isEasting(n1) && isNorthing(n2)) {
          easting = n1; northing = n2;
        } else if (isNorthing(n1) && isEasting(n2)) {
          easting = n2; northing = n1;
        } else {
          // fallback: assume latitude como northing e longitude como easting (padrão comum do usuário)
          easting = parseFloat(lonStr);
          northing = parseFloat(latStr);
        }

        const { lat, lon } = utmToLatLon({ zone, easting, northing, hemisphere });

        showToast("UTM convertido para Graus Decimais.", "info")

        $('#latitude').val(lat.toFixed(8));
        $('#longitude').val(lon.toFixed(8));
        updateMarkerFromInput()
        okClasses();
        return;
      }



      // Formatos mistos: espera até os dois serem do mesmo tipo
      waitClasses();
    }

    // Opcional: chame ao mudar qualquer um dos campos
    $('#latitude, #longitude, #edp-select').on('change blur', function() {
        normalizarCoordenadas();
    });
//    $('#latitude, #longitude, #edp-select').on('change blur', normalizarCoordenadas());

    // ==== Helpers de UX =========================================================
    function okClasses() {
      $('#latitude, #longitude').removeClass('is-invalid').addClass('is-valid');
    }
    function waitClasses() {
      $('#latitude, #longitude').removeClass('is-valid').removeClass('is-invalid');
    }

    // ==== Detecção de formato ===================================================
    function isLikelyUTMPair(a, b) {
      // UTM costuma ser números inteiros/decimais sem N/S/E/W e sem símbolos de grau
      return isLikelyUTM(a) && isLikelyUTM(b);
    }
    function isLikelyGeoPair(a, b) {
      // Ambos parseáveis como decimal/DMS com possíveis N/S/E/W
      return parseCoordinate(a, true) !== null && parseCoordinate(b, false) !== null;
    }
    function isLikelyUTM(str) {
      // Não pode ter símbolos de grau nem N/S/E/W
      if (/[NSEWO°'″"]/i.test(str)) return false;
      // Tem que parecer número simples
      if (!/^\d+(\.\d+)?$/.test(str)) return false;

      const val = parseFloat(str);
      // Pode ser easting (160k..834k) ou northing (0..10,000,000)
      return isEasting(val) || isNorthing(val);
    }
    function isEasting(v) {
      return v >= 160000 && v <= 834000; // faixa segura
    }
    function isNorthing(v) {
      return v >= 0 && v <= 10000000;
    }

    // ==== Parse de coordenadas (decimal/DMS) ====================================
    function parseCoordinate(value, isLat) {
      if (value === null || value === undefined) return null;
      let str = String(value).trim().toUpperCase();
      if (!str) return null;

      if (value > 160000) return null;

      let sign = 1;
      if (/[SWO]/.test(str)) sign = -1;

      // Se já for decWimal simples (com possível sinal)
      if (/^-?\d+(\.\d+)?$/.test(str)) {
        const num = parseFloat(str);
        return num * sign;
      }

      // Aceita DMS com vários separadores
      // Exemplos: 23°33'01", 23 33 1 S, 23° 33.5'
      const dms = str.match(/(-?\d+(?:\.\d+)?)\D+(\d+(?:\.\d+)?)?\D*(\d+(?:\.\d+)?)?/);
      if (dms) {
        const deg = parseFloat(dms[1]) || 0;
        const min = parseFloat(dms[2]) || 0;
        const sec = parseFloat(dms[3]) || 0;
        let decimal = Math.abs(deg) + (min / 60) + (sec / 3600);
        if (deg < 0) sign = -1; // se usuário já pôs negativo no grau
        decimal = decimal * sign;

        // Checagem rápida de faixa
        if (isLat && Math.abs(decimal) <= 90) return decimal;
        if (!isLat && Math.abs(decimal) <= 180) return decimal;
        return null;
      }

      return null;
    }

    // ==== UTM → Lat/Lon (WGS84) ================================================
    function utmToLatLon({ zone, easting, northing, hemisphere = 'S' }) {
      const a = 6378137.0;        // semi-eixo maior WGS84
      const e = 0.081819191;      // excentricidade
      const k0 = 0.9996;

      const x = easting - 500000.0;
      let y = northing;
      if (hemisphere.toUpperCase() === 'S') y -= 10000000.0;

      const m = y / k0;
      const mu = m / (a * (1 - (e*e)/4 - 3*Math.pow(e,4)/64 - 5*Math.pow(e,6)/256));

      const e1 = (1 - Math.sqrt(1 - e*e)) / (1 + Math.sqrt(1 - e*e));
      const j1 = (3*e1/2 - 27*Math.pow(e1,3)/32);
      const j2 = (21*Math.pow(e1,2)/16 - 55*Math.pow(e1,4)/32);
      const j3 = (151*Math.pow(e1,3)/96);
      const j4 = (1097*Math.pow(e1,4)/512);

      const fp = mu + j1*Math.sin(2*mu) + j2*Math.sin(4*mu) + j3*Math.sin(6*mu) + j4*Math.sin(8*mu);

      const e2 = (e*e)/(1 - e*e);
      const c1 = e2 * Math.pow(Math.cos(fp), 2);
      const t1 = Math.pow(Math.tan(fp), 2);
      const r1 = a * (1 - e*e) / Math.pow(1 - Math.pow(e*Math.sin(fp), 2), 1.5);
      const n1 = a / Math.sqrt(1 - Math.pow(e*Math.sin(fp), 2));

      const d = x / (n1 * k0);

      const q1 = n1 * Math.tan(fp) / r1;
      const q2 = (Math.pow(d, 2) / 2);
      const q3 = (5 + 3*t1 + 10*c1 - 4*Math.pow(c1, 2) - 9*e2) * Math.pow(d, 4) / 24;
      const q4 = (61 + 90*t1 + 298*c1 + 45*Math.pow(t1, 2) - 252*e2 - 3*Math.pow(c1, 2)) * Math.pow(d, 6) / 720;

      const lat = fp - q1 * (q2 - q3 + q4);
      const lon = (d - (1 + 2*t1 + c1) * Math.pow(d, 3) / 6
        + (5 - 2*c1 + 28*t1 - 3*Math.pow(c1, 2) + 8*e2 + 24*Math.pow(t1, 2)) * Math.pow(d, 5) / 120) / Math.cos(fp);

      const lonOrigin = (zone - 1) * 6 - 180 + 3;

      return {
        lat: (lat * 180) / Math.PI,
        lon: lonOrigin + (lon * 180) / Math.PI
      };
    }


}); //fim do ready
