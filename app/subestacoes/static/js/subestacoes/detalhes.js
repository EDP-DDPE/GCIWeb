// detalhes.js — modal "Ver Detalhes" com mapa Leaflet

let mapaDetalhes = null;

export function verDetalhes(id) {
    const $modalBody = $("#modalDetalhesBody");

    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($("#modalDetalhes")[0]);
    modal.show();

    $.get(`/subestacoes/${id}/api`)
        .done(function (data) {
            const temCoordenadas = data.lat && data.longitude;

            $modalBody.html(`
                <div class="row g-3">
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-info text-white">
                                <i class="fas fa-bolt me-2"></i>Dados da Subestação
                            </div>
                            <div class="card-body">
                                <p><strong>ID:</strong> ${data.id}</p>
                                <p><strong>Nome:</strong> ${data.nome || "-"}</p>
                                <p><strong>Sigla:</strong> ${data.sigla || "-"}</p>
                                <p><strong>Município:</strong> ${data.municipio || "-"}</p>
                                <p><strong>EDP:</strong> ${data.edp || "-"}</p>
                                <p><strong>Latitude:</strong> ${data.longitude || "-"}</p>
                                <p><strong>Longitude:</strong> ${data.lat || "-"}</p>
                                <p><strong>Fronteira:</strong> ${data.fronteira ? "Sim" : "Não"}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-secondary text-white">
                                <i class="fas fa-map-marked-alt me-2"></i>Localização
                            </div>
                            <div class="card-body p-0">
                                ${temCoordenadas
                                    ? '<div id="mapaDetalhes" style="height: 320px;"></div>'
                                    : '<div class="p-3 text-muted">Sem coordenadas cadastradas.</div>'}
                            </div>
                        </div>
                    </div>
                </div>
            `);

            if (temCoordenadas) {
                inicializarMapa(parseFloat(data.longitude), parseFloat(data.lat), data.nome);
            }
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar detalhes da subestação.</div>');
        });
}

function inicializarMapa(lat, lng, nome) {
    // Destrói instância anterior (evita "Map container is already initialized")
    if (mapaDetalhes) {
        mapaDetalhes.remove();
        mapaDetalhes = null;
    }

    mapaDetalhes = L.map("mapaDetalhes").setView([lat, lng], 14);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
    }).addTo(mapaDetalhes);

    L.marker([lat, lng]).addTo(mapaDetalhes).bindPopup(nome || "Subestação").openPopup();

    // O modal só tem tamanho final depois de aberto: recalcula o mapa
    setTimeout(() => mapaDetalhes.invalidateSize(), 300);
}

// Limpa o mapa ao fechar o modal
$(document).on("hidden.bs.modal", "#modalDetalhes", function () {
    if (mapaDetalhes) {
        mapaDetalhes.remove();
        mapaDetalhes = null;
    }
});

// Expor para os onclick do HTML
window.verDetalhes = verDetalhes;