export function apiCarregarAlternativa(id) {
    return $.get(`/alternativas/${id}`);
}

export function apiExcluirAlternativa(id) {
    return $.ajax({
        url: `/alternativas/excluir/${id}`,
        method: "DELETE"
    });
}

export function apiListarCircuitos(id_edp, subgrupo) {
    return $.get(`/api/circuitos/${id_edp}/${subgrupo}`);
}

export function apiCalcularFatorK(id_edp, subgrupo, dataAbertura, tipo) {
    return $.get(`/api/fator_k/${id_edp}/${subgrupo}/${dataAbertura}/${tipo}`);
}

export function apiCarregarDadosEstudo(idEstudo) {
    return $.get(`/api/alternativa/estudo/${idEstudo}`);
}