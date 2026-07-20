// crud.js — editar, excluir e adicionar tipos de solicitação
import { showLoading, hideLoading, showNotification } from "./utils.js";

export function editarDetalhes(tipo_solicitacaoId) {
    const $modalBody = $("#modalEditarBody");

    // Loading spinner
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-warning" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($("#modalEditar")[0]);
    modal.show();

    $.get(`/tipo_solicitacao/${tipo_solicitacaoId}/api`)
        .done(function (data) {
            if (data.error) {
                $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                return;
            }

            const editarHtml = `
                <form id="formEdicao" data-tipo_solicitacao-id="${tipo_solicitacaoId}">
                    <div class="row g-3">
                        <div class="col-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-info-circle me-2"></i>Detalhes do Tipo de Solicitação
                                </div>
                                <div class="card-body">
                                    <div class="mb-3">
                                        <label class="form-label"><strong>ID:</strong></label>
                                        <input type="text" class="form-control" value="${data.id}" readonly>
                                    </div>
                                    <div class="mb-3 row g-2">
                                        <div class="col-md-8">
                                            <label class="form-label"><strong>Viabilidade:</strong></label>
                                            <input type="text" name="viabilidade" class="form-control" value="${data.viabilidade || ""}" required>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label"><strong>Viabilidade Abrev:</strong></label>
                                            <input type="text" name="viabilidade_abrev" class="form-control" value="${data.viabilidade_abrev || ""}" required>
                                        </div>
                                    </div>
                                    <div class="mb-3 row g-2">
                                        <div class="col-md-8">
                                            <label class="form-label"><strong>Análise:</strong></label>
                                            <input type="text" name="analise" class="form-control" value="${data.analise || ""}" required>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label"><strong>Análise Abrev:</strong></label>
                                            <input type="text" name="analise_abrev" class="form-control" value="${data.analise_abrev || ""}" required>
                                        </div>
                                    </div>
                                    <div class="mb-3 row g-2">
                                        <div class="col-md-8">
                                            <label class="form-label"><strong>Pedido:</strong></label>
                                            <input type="text" name="pedido" class="form-control" value="${data.pedido || ""}" required>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label"><strong>Pedido Abrev:</strong></label>
                                            <input type="text" name="pedido_abrev" class="form-control" value="${data.pedido_abrev || ""}" required>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </form>
            `;

            $modalBody.html(editarHtml);
        })
        .fail(function (xhr, status, error) {
            console.error("Erro:", error);
            $modalBody.html(`<div class="alert alert-danger">Erro ao carregar dados do tipo de solicitação</div>`);
        });
}

export function salvarEdicao() {
    const form = document.getElementById("formEdicao");
    const tipo_solicitacaoId = form.getAttribute("data-tipo_solicitacao-id");
    const formData = new FormData(form);

    // Converter FormData para objeto
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    $.ajax({
        url: `/tipo_solicitacao/${tipo_solicitacaoId}/editar`,
        method: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function () {
            bootstrap.Modal.getInstance(document.getElementById("modalEditar")).hide();
            alert("Tipo de solicitação atualizado com sucesso!");
            location.reload();
        },
        error: function (xhr, status, error) {
            console.error("Erro ao salvar:", error);
            alert("Erro ao salvar as alterações. Tente novamente.");
        }
    });
}

export function confirmarExclusao() {
    const form = document.getElementById("formEdicao");
    const tipo_solicitacaoId = form.getAttribute("data-tipo_solicitacao-id");

    // Primeira confirmação
    if (!confirm("Tem certeza que deseja excluir este tipo de solicitação? Esta operação não pode ser desfeita.")) {
        return;
    }

    // Segunda verificação: digitar "EXCLUIR"
    const confirmacao = prompt("Para confirmar, digite a palavra: EXCLUIR");
    if (confirmacao !== "EXCLUIR") {
        alert("❌ Confirmação incorreta. Exclusão cancelada.");
        return;
    }

    $.ajax({
        url: `/tipo_solicitacao/${tipo_solicitacaoId}/excluir`,
        method: "POST",
        success: function () {
            bootstrap.Modal.getInstance(document.getElementById("modalEditar")).hide();
            alert("✅ Tipo de solicitação excluído com sucesso!");
            location.reload();
        },
        error: function (xhr, status, error) {
            let mensagemErro = "❌ Erro ao excluir o tipo de solicitação!";

            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensagemErro = xhr.responseJSON.message;
            } else if (xhr.status === 409) {
                mensagemErro = "❌ Não é possível excluir este tipo de solicitação!\n\n" +
                    "Existem registros relacionados na tabela de Estudos.\n\n";
            }

            alert(mensagemErro);
            console.error("Erro detalhado:", xhr.responseText);
        }
    });
}

export function abrirModalAdicionar() {
    const $modalBody = $("#modalAdicionarBody");

    // Spinner enquanto carrega
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($("#modalAdicionar")[0]);
    modal.show();

    const addHtml = `
        <form id="formAdicionar" novalidate>
            <div class="card shadow-sm">
                <div class="card-header bg-secondary text-white">
                    <i class="fas fa-plus-circle me-2"></i>Novo Tipo de Solicitação
                </div>
                <div class="card-body">

                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Viabilidade:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="viabilidade" id="campo-viabilidade"
                                class="form-control" placeholder="Digite a viabilidade" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Viabilidade.</div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Viabilidade Abrev:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="viabilidade_abrev" id="campo-viabilidade-abrev"
                                class="form-control" placeholder="Digite a Viabilidade abrev" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Viabilidade Abrev.</div>
                        </div>
                    </div>

                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Análise:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="analise" id="campo-analise"
                                class="form-control" placeholder="Digite a análise" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Análise.</div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Análise Abrev:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="analise_abrev" id="campo-analise-abrev"
                                class="form-control" placeholder="Digite a Análise abrev" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Análise Abrev.</div>
                        </div>
                    </div>

                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Pedido:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="pedido" id="campo-pedido"
                                class="form-control" placeholder="Digite o pedido" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Pedido.</div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Pedido Abrev:</strong> <span class="text-danger">*</span></label>
                            <input type="text" name="pedido_abrev" id="campo-pedido-abrev"
                                class="form-control" placeholder="Digite o Pedido abrev" required>
                            <div class="invalid-feedback">Por favor, preencha o campo Pedido Abrev.</div>
                        </div>
                    </div>

                </div>
            </div>
        </form>
    `;

    $modalBody.html(addHtml);
}

export function salvarNovoTipoSolicitacao() {
    const form = document.getElementById("formAdicionar");

    form.classList.remove("was-validated");

    // Validação manual com mensagens personalizadas
    const viabilidade = document.getElementById("campo-viabilidade");
    const analise = document.getElementById("campo-analise");
    const pedido = document.getElementById("campo-pedido");

    let camposVazios = [];

    if (!viabilidade.value.trim()) {
        camposVazios.push("Viabilidade");
        viabilidade.classList.add("is-invalid");
    } else {
        viabilidade.classList.remove("is-invalid");
    }

    if (!analise.value.trim()) {
        camposVazios.push("Análise");
        analise.classList.add("is-invalid");
    } else {
        analise.classList.remove("is-invalid");
    }

    if (!pedido.value.trim()) {
        camposVazios.push("Pedido");
        pedido.classList.add("is-invalid");
    } else {
        pedido.classList.remove("is-invalid");
    }

    if (camposVazios.length > 0) {
        alert(`⚠️ Por favor, preencha o(s) seguinte(s) campo(s) obrigatório(s):\n\n• ${camposVazios.join("\n• ")}`);

        if (!viabilidade.value.trim()) {
            viabilidade.focus();
        } else if (!analise.value.trim()) {
            analise.focus();
        } else if (!pedido.value.trim()) {
            pedido.focus();
        }

        return;
    }

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value.trim();
    });

    $.ajax({
        url: `/tipo_solicitacao/adicionar`,
        method: "POST",
        data: JSON.stringify(data),
        contentType: "application/json",
        success: function () {
            bootstrap.Modal.getInstance(document.getElementById("modalAdicionar")).hide();
            alert("✅ Tipo de solicitação adicionado com sucesso!");
            location.reload();
        },
        error: function (xhr, status, error) {
            console.error("Erro:", error);
            console.error("Resposta do servidor:", xhr.responseText);
            alert("❌ Erro ao adicionar. Tente novamente.");
        }
    });
}

export function refreshData() {
    showLoading();

    // A forma mais simples de garantir dados e badges atualizados
    setTimeout(() => {
        hideLoading();
        showNotification("Atualizando dados...", "info");
        location.reload();
    }, 300);
}

// Expor para os onclick do HTML
window.editarDetalhes = editarDetalhes;
window.salvarEdicao = salvarEdicao;
window.confirmarExclusao = confirmarExclusao;
window.abrirModalAdicionar = abrirModalAdicionar;
window.salvarNovoTipoSolicitacao = salvarNovoTipoSolicitacao;
window.refreshData = refreshData;