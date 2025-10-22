// =========================
// Gestão de Aprovação JS
// =========================

let grafico = null;

$(document).ready(function () {
  inicializarTooltips();
  inicializarGraficoResumo();
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

function salvarComentario(id) {
  enviarAcao(id, "Comentado");
}

function enviarAcao(id, status) {
  const comentario = $(`#comentario-${id}`).val();

  $.ajax({
    url: `/gestao/aprovacao/${id}/status`,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify({ status, comentario }),
    success: function (res) {
      const badge =
        status === "Aprovado"
          ? "bg-success"
          : status === "Reprovado"
          ? "bg-danger"
          : "bg-info";

      $(`#estudo-${id} td:nth-child(6)`).html(
        `<span class="badge ${badge}">${status}</span>`
      );

      showNotification(`Projeto ${status.toLowerCase()} com sucesso!`, "success");
      atualizarGrafico(status);
      $(`#comentario-${id}`).val("");
    },
    error: function () {
      showNotification("Erro ao enviar ação.", "danger");
    },
  });
}

// --- Atualiza o gráfico dinamicamente ---
function atualizarGrafico(status) {
  if (!grafico) return;

  if (status === "Aprovado") {
    dataResumo.aprovado++;
    dataResumo.pendente--;
  } else if (status === "Reprovado") {
    dataResumo.reprovado++;
    dataResumo.pendente--;
  }

  grafico.data.datasets[0].data = [
    dataResumo.aprovado,
    dataResumo.reprovado,
    dataResumo.pendente < 0 ? 0 : dataResumo.pendente,
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
