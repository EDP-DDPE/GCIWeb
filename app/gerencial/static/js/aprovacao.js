let grafico = null;

$(document).ready(function () {
  inicializarTooltips();
  inicializarGraficoResumo();
});

function verDetalhes(estudoId) {
        const $modalBody = $('#modalDetalhesBody');
        $modalBody.html(`
            <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `);

        const modal = new bootstrap.Modal($('#modalDetalhes')[0]);
        modal.show();

        $.get(`/api/estudos/${estudoId}`)
            .done(function(data) {
                if (data.error) {
                    $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                    return;
                }

                const detalhesHtml = `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-info-circle me-2"></i>Informações Básicas
                                </div>
                                <div class="card-body">
                                    <p><strong>Protocolo:</strong> ${data.protocolo || 'N/A'}</p>
                                    <p><strong>Nº Documento:</strong> ${data.num_doc || 'N/A'}</p>
                                    <p><strong>Projeto:</strong> ${data.nome_projeto || 'N/A'}</p>
                                    <p><strong>Descrição:</strong> ${data.descricao || 'N/A'}</p>
                                    <p><strong>Cliente:</strong> ${data.empresa?.nome || 'N/A'}</p>
                                    <p><strong>CNPJ:</strong> ${data.empresa?.cnpj || 'N/A'}</p>
                                    <p><strong>Município:</strong> ${data.municipio?.nome || 'N/A'}</p>
                                    <p><strong>Regional:</strong> ${data.regional?.nome || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-cogs me-2"></i>Detalhes Técnicos
                                </div>
                                <div class="card-body">
                                    <p><strong>Viabilidade:</strong> ${data.tipo_solicitacao?.viabilidade || 'N/A'}</p>
                                    <p><strong>Análise:</strong> ${data.tipo_solicitacao?.analise || 'N/A'}</p>
                                    <p><strong>Pedido:</strong> ${data.tipo_solicitacao?.pedido || 'N/A'}</p>
                                    <p><strong>Criado por:</strong> ${data.criado_por?.nome || 'N/A'}</p>
                                    <p><strong>Responsável Região:</strong> ${data.responsavel_regiao?.usuario?.nome || 'N/A'}</p>
                                    <p><strong>Data Registro:</strong> ${data.data_registro || 'N/A'}</p>
                                    <p><strong>Latitude:</strong> ${data.latitude_cliente || 'N/A'}</p>
                                    <p><strong>Longitude:</strong> ${data.longitude_cliente || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-chart-bar me-2"></i>Demandas
                                </div>
                                <div class="card-body">
                                    <div class='row'>
                                        <div class="col-md-6">
                                            <p><strong>Demanda Atual Carga FP:</strong> ${data.dem_carga_atual_fp || 'N/A'}</p>
                                            <p><strong>Demanda Atual Carga P:</strong> ${data.dem_carga_atual_p || 'N/A'}</p>
                                            <p><strong>Demanda Atual Geração FP:</strong> ${data.dem_ger_atual_fp || 'N/A'}</p>
                                            <p><strong>Demanda Atual Geração P:</strong> ${data.dem_ger_atual_p || 'N/A'}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><strong>Demanda Solicitada Carga FP:</strong> ${data.dem_carga_solicit_fp || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Carga P:</strong> ${data.dem_carga_solicit_p || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Geração FP:</strong> ${data.dem_ger_solicit_fp || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Geração P:</strong> ${data.dem_ger_solicit_p || 'N/A'}</p>
                                        </div>
                                    </row>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="bi bi-list-check"></i>Alternativas
                                </div>
                                <div class="card-body">
                                     ${data.alternativas && data.alternativas.length > 0 ? `
                                        <div class="table-responsive">
                                            <table class="table table-striped table-sm align-middle mb-0">
                                                <thead class="table-light">
                                                    <tr>
                                                        <th>ID</th>
                                                        <th>Descrição</th>
                                                        <th>Custo Modular (R$)</th>
                                                        <th>Circuito</th>
                                                        <th>Tensão</th>
                                                        <th>Escolhida?</th>
                                                        <th>Imagem</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${data.alternativas.map(a => `
                                                        <tr>
                                                            <td>${a.id || '-'}</td>
                                                            <td>${a.descricao || '-'}</td>
                                                            <td>${a.custo_modular?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) || '-'}</td>
                                                            <td>${a.circuito?.nome || '-'}</td>
                                                            <td>${a.circuito?.tensao || '-'}</td>
                                                            <td>
                                                                ${a.flag_alternativa_escolhida
                                                                    ? '<span class="badge bg-success">Sim</span>'
                                                                    : '<span class="badge bg-secondary">Não</span>'
                                                                }
                                                            </td>
                                                            <td>
                                                              ${a.has_image
                                                                    ? `<button class="btn btn-sm btn-outline-primary ver-imagem-db"
                                                                                data-id="${a.id}">
                                                                            <i class="bi bi-image"></i> Ver Imagem
                                                                       </button>`
                                                                    : '<span class="text-muted">Sem imagem</span>'
                                                                }
                                                            </td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                    ` : '<p>Nenhuma alternativa cadastrada.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-file-upload me-2"></i>Anexos
                                </div>
                                <div class="card-body">

                                    ${data.anexos && data.anexos.length > 0 ? `
                                        <ul class="list-group list-group-flush">
                                            ${data.anexos.map(a => {
                                                const caminho = a.endereco.replace(/\\/g, '/'); // troca '\' por '/'
                                                return `
                                                    <li class="list-group-item  d-flex justify-content-between align-items-center">${a.nome_arquivo || 'N/A'}
                                                        <a href="/listar/download/${caminho}" class="btn btn-sm btn-outline-primary">
                                                          <i class="bi bi-download"></i> Baixar
                                                        </a>
                                                    </li>
                                                `;
                                            }).join('')}
                                        </ul>
                                    ` : '<p>Nenhum anexo.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-history me-2"></i>Status Histórico
                                </div>
                                <div class="card-body">
                                    ${data.status_historico && data.status_historico.length > 0 ? `
                                        <ul class="list-group list-group-flush">
                                            ${data.status_historico.map(s => `
                                                <li class="list-group-item">
                                                    <strong>${s.status || 'N/A'}</strong> - ${s.data || 'N/A'} - ${s.criado_por || 'N/A'}
                                                    ${s.observacao ? `<br><small>${s.observacao}</small>` : ''}
                                                </li>
                                            `).join('')}
                                        </ul>
                                    ` : '<p>Sem histórico de status.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                if (!$('#modalImagemDB').length) {
                    $('body').append(`
                        <div class="modal fade" id="modalImagemDB" tabindex="-1" aria-labelledby="modalImagemDBLabel"
                             aria-hidden="true" data-bs-backdrop="static">
                          <div class="modal-dialog modal-xl modal-dialog-centered">
                            <div class="modal-content" style="z-index: 99999 !important;">
                              <div class="modal-header bg-dark text-white">
                                <h5 class="modal-title" id="modalImagemDBLabel">
                                  <i class="bi bi-image"></i> Imagem da Alternativa
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Fechar"></button>
                              </div>
                              <div class="modal-body text-center">
                                  <div id="loadingImg" class="my-3" style="display:none;">
                                    <div class="spinner-border text-primary" role="status">
                                      <span class="visually-hidden">Carregando...</span>
                                    </div>
                                  </div>

                                  <div id="panzoom-container" class="d-inline-block border rounded p-2 bg-light">
                                    <img id="imagemDB" src="" alt="Imagem da alternativa" class="img-fluid rounded shadow d-none" style="cursor: grab;">
                                  </div>

                                  <div class="mt-3">
                                    <button id="zoomIn" class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-zoom-in"></i></button>
                                    <button id="zoomOut" class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-zoom-out"></i></button>
                                    <button id="resetZoom" class="btn btn-sm btn-outline-secondary"><i class="bi bi-arrow-repeat"></i></button>
                                  </div>
                              </div>

                            </div>
                          </div>
                        </div>
                    `);
                }

                $modalBody.html(detalhesHtml);
            })
            .fail(function(xhr, status, error) {
                console.error('Erro:', error);
                $modalBody.html(`<div class="alert alert-danger">Erro ao carregar detalhes do documento</div>`);
            });
    }

    $(document).on('click', '.ver-imagem-db', function() {
        const idAlt = $(this).data('id');

        // mostra loading
        $('#imagemDB').addClass('d-none');
        $('#loadingImg').show();

        $('#modalImagemDB').modal('show');

        $.getJSON(`/api/imagem_alternativa/${idAlt}`)
            .done(function(resp) {
                if (resp.imagem) {
                    $('#imagemDB').attr('src', resp.imagem).removeClass('d-none');
                } else {
                    $('#imagemDB').replaceWith('<p class="text-danger">Sem imagem disponível.</p>');
                }
            })
            .fail(function() {
                $('#imagemDB').replaceWith('<p class="text-danger">Erro ao carregar a imagem.</p>');
            })
            .always(function() {
                $('#loadingImg').hide();
            });
    });

    $('#modalImagemDB').on('hidden.bs.modal', function () {
        $('body').addClass('modal-open'); // mantém o scroll travado do modal anterior
    });

    let panzoomInstance = null;

    $(document).on('shown.bs.modal', '#modalImagemDB', function() {
        const image = document.getElementById('imagemDB');
        const container = document.getElementById('panzoom-container');

        // Destroi instância anterior se existir
        if (panzoomInstance) {
            panzoomInstance.destroy();
        }

        // Inicializa Panzoom
        panzoomInstance = Panzoom(container, {
            contain: 'outside',
            maxScale: 8,
            minScale: 0.5,
            cursor: 'grab',
            step: 0.3,
        });

        // Zoom com scroll
        container.parentElement.addEventListener('wheel', panzoomInstance.zoomWithWheel);

        // Botões de controle
        $('#zoomIn').off('click').on('click', () => panzoomInstance.zoomIn());
        $('#zoomOut').off('click').on('click', () => panzoomInstance.zoomOut());
        $('#resetZoom').off('click').on('click', () => panzoomInstance.reset());
    });

// --- Inicialização ---

function inicializarTooltips() {
  $('[data-bs-toggle="tooltip"]').each(function () {
    new bootstrap.Tooltip(this);
  });
}

function inicializarGraficoResumo() {
  const ctx = document.getElementById("graficoResumo");
  grafico = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Aprovado", "Reprovado", "Pendente"],
      datasets: [
        {
          data: [dataResumo.aprovado, dataResumo.reprovado, dataResumo.pendente],
          backgroundColor: ["#198754", "#dc3545", "#6c757d"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,     // permite controlar a altura via CSS
      aspectRatio: 2,                 // backup
      plugins: {
        legend: { position: "bottom" },
        tooltip: {
          callbacks: {
            label: (context) => `${context.label}: ${context.raw}`,
          },
        },
      },
    },
  });
}

// --- Ações ---

function filtrarValor() {
  const valor = $("#valorFiltro").val() || 0;
  window.location.href = `/gestao/aprovacao?min_valor=${valor}`;
}

function aprovarProjeto(id) {
  enviarAcao(id, "Aprovado");
}

function reprovarProjeto(id) {
  enviarAcao(id, "Reprovado");
}


function enviarAcao(id, status) {
  const comentario = $(`#comentario-${id}`).val();

  $.ajax({
    url: `/gestao/aprovacao/${id}/status`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ status, comentario }),
    success: function (res) {
      // Badge coerente com a decisão do Gestor
      let badgeClasse = "bg-info";
      let textoBadge = "Comentado Gestor";

      if (status === "Aprovado") {
        badgeClasse = "bg-success";
        textoBadge = "Aprovado Gestor";
        dataResumo.aprovado++;
        dataResumo.pendente = Math.max(0, dataResumo.pendente - 1);
      } else if (status === "Reprovado") {
        badgeClasse = "bg-danger";
        textoBadge = "Rejeitado Gestor";
        dataResumo.reprovado++;
        dataResumo.pendente = Math.max(0, dataResumo.pendente - 1);
      }

      $(`#estudo-${id} td:nth-child(6)`).html(
        `<span class="badge ${badgeClasse}">${textoBadge}</span>`
      );

      showNotification(res.message || `Projeto ${status.toLowerCase()} com sucesso!`, "success");
      atualizarGrafico();
      $(`#comentario-${id}`).val("");
    },
    error: function (xhr) {
      const msg = (xhr.responseJSON && xhr.responseJSON.message) ? xhr.responseJSON.message : "Erro ao enviar ação.";
      showNotification(msg, "danger");
    },
  });
}

// --- Atualiza o gráfico dinamicamente ---
function atualizarGrafico() {
  if (!grafico) return;
  grafico.data.datasets[0].data = [
    dataResumo.aprovado,
    dataResumo.reprovado,
    dataResumo.pendente,
  ];
  grafico.update();
}

// --- Notificações ---
function showNotification(message, type = "info") {
  const $notification = $(`
    <div class="alert alert-${type} alert-dismissible fade show position-fixed shadow"
         style="top:20px; right:20px; z-index:9999; min-width:300px;">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  `);
  $("body").append($notification);
  setTimeout(() => $notification.alert("close"), 3000);
}