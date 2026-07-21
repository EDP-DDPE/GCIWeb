// crud.js — adicionar, editar e excluir subestações
import { showNotification } from "./utils.js";
import { loadData } from "./table.js";

// ---------- EDITAR ----------

export function editarSubestacao(id) {
    const $modalBody = $("#modalEditarBody");

    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-warning" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($("#modalEditar")[0]);
    modal.show();

    $.get(`/subestacoes/${id}/api`)
        .done(function (data) {
            $modalBody.html(`
                <form id="formEditarSubestacao" data-subestacao-id="${id}">
                    <div class="card shadow-sm">
                        <div class="card-header bg-secondary text-white">
                            <i class="fas fa-bolt me-2"></i>Editar Subestação
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>Nome:</strong></label>
                                <input type="text" name="nome" class="form-control" value="${data.nome || ""}" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Sigla:</strong></label>
                                <input type="text" name="sigla" class="form-control" value="${data.sigla || ""}" required maxlength="10">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Latitude:</strong></label>
                                <input type="text" name="lat" class="form-control" value="${data.lat || ""}">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Longitude:</strong></label>
                                <input type="text" name="longitude" class="form-control" value="${data.longitude || ""}">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>EDP (Estado):</strong></label>
                                <select name="id_edp" class="form-select" id="edp-edit-select" required></select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Município:</strong></label>
                                <select name="id_municipio" class="form-select" id="municipio-edit-select" required></select>
                            </div>
                        </div>
                    </div>
                </form>
            `);

            carregarEdpsSelect(data.id_edp, data.id_municipio);
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar dados da subestação.</div>');
        });
}

function carregarEdpsSelect(edpSelecionado, municipioSelecionado) {
    $.get("/subestacoes/edps/api")
        .done(function (edps) {
            const $edpSelect = $("#edp-edit-select");
            const options = edps.map(e =>
                `<option value="${e.id}" ${e.id === edpSelecionado ? "selected" : ""}>${e.empresa}</option>`
            );
            $edpSelect.html('<option value="">Selecione...</option>' + options.join(""));

            $edpSelect.select2({
                theme: "bootstrap-5",
                dropdownParent: $("#modalEditar")
            });

            if (edpSelecionado) {
                carregarMunicipiosSelect(edpSelecionado, municipioSelecionado);
            }

            $edpSelect.on("change", function () {
                carregarMunicipiosSelect($(this).val(), null);
            });
        });
}

function carregarMunicipiosSelect(edpId, municipioSelecionado) {
    const $municipioSelect = $("#municipio-edit-select");

    if (!edpId) {
        $municipioSelect.html("<option>Selecione o Estado primeiro...</option>").prop("disabled", true);
        return;
    }

    $.get(`/subestacoes/municipios/api/${edpId}`)
        .done(function (municipios) {
            if (!municipios.length) {
                $municipioSelect.html('<option value="">Nenhum município encontrado</option>').prop("disabled", true);
            } else {
                const options = municipios.map(m =>
                    `<option value="${m.id}" ${m.id === municipioSelecionado ? "selected" : ""}>${m.municipio}</option>`
                ).join("");
                $municipioSelect.html('<option value="">Selecione...</option>' + options).prop("disabled", false);
            }

            $municipioSelect.select2({
                theme: "bootstrap-5",
                dropdownParent: $("#modalEditar")
            });
        })
        .fail(() => $municipioSelect.html("<option>Erro ao carregar municípios</option>").prop("disabled", true));
}

export function salvarEdicao() {
    const form = document.getElementById("formEditarSubestacao");
    const id = form.getAttribute("data-subestacao-id");

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = Object.fromEntries(new FormData(form).entries());

    $.ajax({
        url: `/subestacoes/${id}/editar`,
        method: "POST",
        data: JSON.stringify(formData),
        contentType: "application/json",
        success: function (response) {
            bootstrap.Modal.getInstance(document.getElementById("modalEditar")).hide();
            showNotification(response.message || "Subestação atualizada com sucesso!", "success");
            loadData();
        },
        error: function (xhr) {
            console.error("Erro:", xhr.responseText);
            alert("❌ Erro ao salvar alterações.");
        }
    });
}

// ---------- EXCLUIR ----------

export function confirmarExclusao() {
    const form = document.getElementById("formEditarSubestacao");
    const id = form.getAttribute("data-subestacao-id");

    if (!confirm("Tem certeza que deseja excluir esta subestação? Esta operação não pode ser desfeita.")) {
        return;
    }

    const confirmacao = prompt("Para confirmar, digite a palavra: EXCLUIR");
    if (confirmacao !== "EXCLUIR") {
        alert("❌ Confirmação incorreta. Exclusão cancelada.");
        return;
    }

    $.ajax({
        url: `/subestacoes/${id}/excluir`,
        method: "POST",
        success: function () {
            bootstrap.Modal.getInstance(document.getElementById("modalEditar")).hide();
            showNotification("✅ Subestação excluída com sucesso!", "success");
            loadData();
        },
        error: function (xhr) {
            let mensagemErro = "❌ Erro ao excluir subestação!";

            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensagemErro = xhr.responseJSON.message;
            } else if (xhr.status === 409) {
                mensagemErro = "❌ Não é possível excluir esta subestação!\n\n" +
                    "Existem circuitos vinculados a ela.\n\n" +
                    "⚠️ Remova os registros relacionados antes de excluir.";
            }

            alert(mensagemErro);
            console.error("Erro detalhado:", xhr.responseText);
        }
    });
}

// ---------- ADICIONAR ----------

export function abrirModalAdicionar() {
    const $modalBody = $("#modalAdicionarBody");

    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($("#modalAdicionar")[0]);
    modal.show();

    $.get("/subestacoes/edps/api")
        .done(function (edps) {
            const edpOptions = edps.map(edp => `<option value="${edp.id}">${edp.empresa}</option>`).join("");

            $modalBody.html(`
                <form id="formAdicionarSubestacao" novalidate>
                    <div class="card shadow-sm">
                        <div class="card-header bg-secondary text-white">
                            <i class="fas fa-bolt me-2"></i>Nova Subestação
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>Nome:</strong> <span class="text-danger">*</span></label>
                                <input type="text" name="nome" class="form-control" placeholder="Digite o nome da Subestação" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Sigla:</strong> <span class="text-danger">*</span></label>
                                <input type="text" name="sigla" class="form-control" placeholder="Digite a sigla" required maxlength="10">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>EDP (Estado):</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_edp" id="edp-select" required>
                                    <option value="">Selecione...</option>
                                    ${edpOptions}
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Município:</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_municipio" id="municipio-select" required disabled>
                                    <option value="">Selecione o Estado primeiro...</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Latitude:</strong></label>
                                <input type="text" name="lat" class="form-control" placeholder="Ex: -20.123456">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Longitude:</strong></label>
                                <input type="text" name="longitude" class="form-control" placeholder="Ex: -40.987654">
                            </div>
                        </div>
                    </div>
                </form>
            `);

            $("#edp-select, #municipio-select").select2({
                theme: "bootstrap-5",
                placeholder: "Selecione...",
                width: "100%",
                dropdownParent: $("#modalAdicionar")
            });

            $("#edp-select").on("change", function () {
                const idEdp = $(this).val();
                const $municipio = $("#municipio-select");

                if (!idEdp) {
                    $municipio.html('<option value="">Selecione o Estado primeiro...</option>').prop("disabled", true);
                    return;
                }

                $municipio.html("<option>Carregando...</option>").prop("disabled", true);

                $.get(`/subestacoes/municipios/api/${idEdp}`)
                    .done(function (municipios) {
                        if (!municipios.length) {
                            $municipio.html('<option value="">Nenhum município encontrado</option>').prop("disabled", true);
                        } else {
                            const options = municipios.map(m => `<option value="${m.id}">${m.municipio}</option>`).join("");
                            $municipio.html('<option value="">Selecione...</option>' + options).prop("disabled", false);
                        }
                    })
                    .fail(function () {
                        $municipio.html("<option>Erro ao carregar municípios</option>").prop("disabled", true);
                    });
            });
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar EDPs!</div>');
        });
}

export function salvarNova() {
    const form = document.getElementById("formAdicionarSubestacao");

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = Object.fromEntries(new FormData(form).entries());

    $.ajax({
        url: "/subestacoes/nova",
        method: "POST",
        data: JSON.stringify(formData),
        contentType: "application/json",
        success: function (response) {
            bootstrap.Modal.getInstance(document.getElementById("modalAdicionar")).hide();
            showNotification("✅ " + (response.msg || "Subestação cadastrada com sucesso!"), "success");
            loadData();
        },
        error: function (xhr) {
            alert("❌ Falha ao salvar. " + (xhr.responseJSON?.erro || "Verifique os dados e tente novamente."));
        }
    });
}

// ---------- ATUALIZAR ----------

export function refreshData() {
    loadData().done(() => {
        showNotification("Dados atualizados com sucesso!", "success");
    });
}

// Expor para os onclick do HTML
window.editarSubestacao = editarSubestacao;
window.salvarEdicao = salvarEdicao;
window.confirmarExclusao = confirmarExclusao;
window.abrirModalAdicionar = abrirModalAdicionar;
window.salvarNova = salvarNova;
window.refreshData = refreshData;