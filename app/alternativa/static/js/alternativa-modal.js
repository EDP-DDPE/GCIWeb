import { apiCarregarAlternativa } from "./alternativa-api.js";
import { apiCarregarDadosEstudo } from "./alternativa-api.js";
import { atualizarCircuitos } from "./alternativa-form.js";
import { preencherFormulario, limparFormulario } from "./alternativa-form.js";

export function abrirModalNovo() {
    showLoading();

    limparFormulario();
    configurarModo("novo");

    const idEstudo = $("#id_estudo").val();

    apiCarregarDadosEstudo(idEstudo)
        .then(estudo => {

                $("#dem_fp_antes").val(estudo.dem_fp_ant);
                $("#dem_p_antes").val(estudo.dem_p_ant);

                $("#dem_fp_depois").val(estudo.dem_fp_dep);
                $("#dem_p_depois").val(estudo.dem_p_dep);

                $("#latitude_ponto_conexao").val(estudo.latitude);
                $("#longitude_ponto_conexao").val(estudo.longitude);

                if (estudo.tensao == 'AT') {
                    $("#subgrupo_select").val('A2')
                } else {
                    $("#subgrupo_select").val('A4')
                }


                // recalcula ERD se precisar
                if (typeof window.recalcularERD === "function") {
                    window.recalcularERD();
                }


            // Agora que tudo está pronto → abre o modal
            const modalEl = document.getElementById("alternativaModal");
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

            modal.show();

            hideLoading(); // 🔥 sempre será chamado
        })
        .catch(() => hideLoading());
}


export function abrirModalEditar(id) {
    showLoading();
    limparFormulario();
    configurarModo("editar", id);

    apiCarregarAlternativa(id)
        .then(data => {
            preencherFormulario(data);

            atualizarCircuitos(data.id_edp, data.subgrupo_tarifario)
                .then(() => {
                    $("#circuito_select").val(data.id_circuito).trigger("change");
        //            new bootstrap.Modal("#alternativaModal").show();
                    const modalEl = document.getElementById("alternativaModal");
                    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                    hideLoading();
                    modal.show();
                });

        })
        .catch(err => {
        hideLoading();
        alert("Erro ao carregar: " + err.responseText)});
}

export function abrirModalVisualizar(id) {
    showLoading();
    limparFormulario();
    configurarModo("visualizar");

    apiCarregarAlternativa(id)
        .then(data => {
            preencherFormulario(data);
            bloquearFormulario();

            atualizarCircuitos(data.id_edp, data.subgrupo_tarifario).then(() => {
            $("#circuito_select").val(data.id_circuito).trigger('change');
        //            new bootstrap.Modal("#alternativaModal").show();
                const modalEl = document.getElementById("alternativaModal");
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                hideLoading();
                modal.show();
            });

        })
        .catch(() => hideLoading());
}

export function configurarModo(modo, id = null) {

    if (modo === "novo") {
        $("#alternativaModalLabel").text("Nova Alternativa");
        const id_estudo = $("#id_estudo").val();
        $("#formAlternativa").attr("action", `/estudo/${id_estudo}/alternativas/`);
        $("#btnExcluirAlternativa").hide();
        $("#salvar_alternativa").show();
        desbloquearFormulario();
    }

    if (modo === "editar") {
        $("#alternativaModalLabel").text("Editar Alternativa");
        $("#formAlternativa").attr("action", `/alternativas/${id}`);
        $("#btnExcluirAlternativa").show().data("id", id);
        $("#salvar_alternativa").show();
        desbloquearFormulario();
    }

    if (modo === "visualizar") {
        $("#alternativaModalLabel").text("Visualizar Alternativa");
        $("#btnExcluirAlternativa").hide();
        $("#salvar_alternativa").hide();
        bloquearFormulario();
    }
}

export function bloquearFormulario() {
//    $("#formAlternativa input, #formAlternativa select, #formAlternativa textarea").prop("disabled", true);
    $("#formAlternativa").addClass("readonly");
}

export function desbloquearFormulario() {
//    $("#formAlternativa input, #formAlternativa select, #formAlternativa textarea").prop("disabled", false);
    $("#formAlternativa").removeClass("readonly");
}

document.getElementById("alternativaModal")
    .addEventListener("hide.bs.modal", () => {
        document.activeElement?.blur();
    });

document.querySelector("#alternativaModal .btn-close")
.addEventListener("click", () => {
    document.activeElement?.blur();
});

document.querySelector("#alternativaModal .btn.btn-secondary")
    .addEventListener("click", () => {
        document.activeElement?.blur();
    });


// Remove backdrop preso após o modal fechar
document.getElementById("alternativaModal")
    .addEventListener("hidden.bs.modal", () => {
        document.querySelectorAll(".modal-backdrop").forEach(b => b.remove());
        document.body.classList.remove("modal-open");
        document.body.style.removeProperty("overflow");
        document.body.style.removeProperty("padding-right");
    });