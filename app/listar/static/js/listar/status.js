export function abrirStatus(idEstudo) {
    $("#status_id_estudo").val(idEstudo);
    window.hideStatusLoading();

    // Pré-preenche a data de ocorrência com hoje (o usuário pode alterar).
    if (!$("#status_data_ocorrencia").val()) {
        $("#status_data_ocorrencia").val(new Date().toISOString().slice(0, 10));
    }

    // Limpa tabela enquanto carrega
    $("#status-historico-body").html(`
        <tr><td colspan="6" class="text-center text-muted py-4">
            Carregando histórico...
        </td></tr>
    `);

    $.get(`/listar/api/status/${idEstudo}`)
        .done(historico => {

            if (!historico.length) {
                $("#status-historico-body").html(`
                    <tr><td colspan="6" class="text-center text-muted py-4">
                        Nenhum status cadastrado
                    </td></tr>
                `);
                return;
            }

            const rows = historico.map(s => `
                <tr>
                    <td>${s.data_ocorrencia || "-"}</td>
                    <td>${s.status}</td>
                    <td>${s.observacao || "-"}</td>
                    <td>${s.criado_por}</td>
                    <td>${s.data}</td>
                    <td class="text-center"></td>
                </tr>
            `).join("");

            $("#status-historico-body").html(rows);
        });

    // Abre o modal
    const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById("statusModal"));
    modal.show();
}

// Expor para HTML
window.abrirStatus = abrirStatus;

export function configurarFormularioStatus() {
    window.hideStatusLoading();
    $("#statusForm").on("submit", function (e) {
        window.hideStatusLoading();
        e.preventDefault();

        const payload = {
            id_estudo: $("#status_id_estudo").val(),
            id_status_tipo: $("#id_status_tipo").val(),
            observacao: $("#observacao").val(),
            data_ocorrencia: $("#status_data_ocorrencia").val(),
        };

        $.ajax({
            url: "/listar/api/status/salvar",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify(payload),
            beforeSend: function () {
                window.showStatusLoading();
            }
        })
        .done(() => {
            abrirStatus(payload.id_estudo); // atualiza lista
            this.reset();
        })
        .fail(err => {
            alert("Erro ao salvar status.");
            console.error(err);
        })
        .always(() => {
            window.hideStatusLoading();         // ← SAI LOADING
        });
    });
}

export function showStatusLoading() {
    $("#statusLoadingOverlay").show();
}

export function hideStatusLoading() {
    $("#statusLoadingOverlay").hide();
}

window.configurarFormularioStatus = configurarFormularioStatus;
window.showStatusLoading = showStatusLoading;
window.hideStatusLoading = hideStatusLoading;

