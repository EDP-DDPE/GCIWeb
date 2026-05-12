import { apiExcluirAlternativa } from "./alternativa-api.js";

export function inicializarExclusao() {

    $("#btnExcluirAlternativa").click(function () {

        const id = $(this).data("id");
        if (!id) {
            alert("Nenhuma alternativa selecionada.");
            return;
        }

        if (!confirm("Deseja realmente excluir esta alternativa?")) return;
        showLoading();
        apiExcluirAlternativa(id)
            .then(() => {
                hideLoading();
                alert("Alternativa excluída com sucesso!");
                location.reload();
            })
            .catch(err => {
                hideLoading();
                alert("Erro ao excluir: " + err.responseText);
            });
    });
}
