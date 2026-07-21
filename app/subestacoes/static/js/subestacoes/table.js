// table.js — carregamento via API, renderização da tabela e paginação
import { state } from "./main.js";
import { showLoading, hideLoading, initializeTooltips } from "./utils.js";
import { applyColumnVisibility } from "./columns.js";

// Busca os dados na API e re-renderiza a tabela
export function loadData() {
    showLoading();

    return $.get("/subestacoes/api/listar")
        .done(function (resp) {
            state.permissoes = resp.permissoes || {};

            state.currentData = (resp.items || []).map(item => ({
                id: String(item.id),
                nome: item.nome || "",
                sigla: item.sigla || "",
                municipio: item.municipio || "",
                edp: item.edp || "",
                lat: item.lat || "",
                longitude: item.longitude || ""
            }));

            state.filteredData = [...state.currentData];

            // Se a página atual ficou fora do alcance (ex.: após exclusão), ajusta
            const totalPages = Math.max(1, Math.ceil(state.filteredData.length / state.pageSize));
            if (state.currentPage > totalPages) state.currentPage = totalPages;

            updatePagination();
            renderTable();
        })
        .fail(function () {
            alert("Erro ao carregar dados do servidor.");
        })
        .always(hideLoading);
}

function buildActions(item) {
    const podeEditar = state.permissoes && state.permissoes.editar;

    return `
        <div class="btn-group" role="group">
            <button class="btn btn-sm btn-info"
                onclick="verDetalhes(${item.id})"
                data-bs-toggle="tooltip"
                title="Ver detalhes">
                <i class="bi bi-eye"></i>
            </button>
            <button class="btn btn-sm btn-warning"
                onclick="editarSubestacao(${item.id})"
                data-bs-toggle="tooltip"
                title="Editar subestação"
                ${podeEditar ? "" : "disabled"}>
                <i class="bi bi-pencil-square"></i>
            </button>
        </div>
    `;
}

// Renderizar tabela
export function renderTable() {
    const $tbody = $("#tableBody");
    const start = (state.currentPage - 1) * state.pageSize;
    const end = start + state.pageSize;
    const pageData = state.filteredData.slice(start, end);

    $tbody.empty();

    pageData.forEach(item => {
        const $row = $("<tr>");

        $("<td>").attr("data-column", "id").text(item.id).appendTo($row);
        $("<td>").attr("data-column", "nome").text(item.nome).appendTo($row);
        $("<td>").attr("data-column", "sigla").text(item.sigla).appendTo($row);
        $("<td>").attr("data-column", "municipio").text(item.municipio).appendTo($row);
        $("<td>").attr("data-column", "edp").text(item.edp).appendTo($row);
        $("<td>").attr("data-column", "lat").text(item.lat).appendTo($row);
        $("<td>").attr("data-column", "longitude").text(item.longitude).appendTo($row);
        $("<td>").attr("data-column", "acoes").html(buildActions(item)).appendTo($row);

        $tbody.append($row);
    });

    applyColumnVisibility();
    initializeTooltips();
}

// Atualizar paginação (versão com input)
export function updatePagination() {
    const totalRecords = state.filteredData.length;
    const totalPages = Math.ceil(totalRecords / state.pageSize);
    const start = Math.min((state.currentPage - 1) * state.pageSize + 1, totalRecords);
    const end = Math.min(state.currentPage * state.pageSize, totalRecords);

    $("#startRecord").text(totalRecords > 0 ? start : 0);
    $("#endRecord").text(end);
    $("#totalRecords").text(totalRecords);

    const $filteredInfo = $("#filteredInfo");
    const $originalTotal = $("#originalTotal");
    if (totalRecords < state.currentData.length) {
        $originalTotal.text(state.currentData.length);
        $filteredInfo.show();
    } else {
        $filteredInfo.hide();
    }

    const $pagination = $("#pagination");
    $pagination.empty();
    if (totalPages <= 1) return;

    // Botão PRIMEIRA página
    $pagination.append(
        $("<li>").addClass(`page-item ${state.currentPage === 1 ? "disabled" : ""}`)
            .html(`<a class="page-link" href="#" onclick="changePage(1)" title="Primeira página">
                <i class="bi bi-chevron-double-left"></i>
            </a>`)
    );

    // Botão ANTERIOR
    $pagination.append(
        $("<li>").addClass(`page-item ${state.currentPage === 1 ? "disabled" : ""}`)
            .html(`<a class="page-link" href="#" onclick="changePage(${state.currentPage - 1})">
                <i class="bi bi-chevron-left"></i>
            </a>`)
    );

    // Input para digitar número da página
    $pagination.append(
        $("<li>").addClass("page-item").html(`
            <div class="d-flex align-items-center px-2">
                <span class="me-2">Página</span>
                <input type="number"
                       id="pageInput"
                       class="form-control form-control-sm"
                       style="width: 60px; text-align: center;"
                       value="${state.currentPage}"
                       min="1"
                       max="${totalPages}"
                       onchange="changePage(parseInt(this.value))"
                       onkeypress="if(event.key==='Enter') changePage(parseInt(this.value))">
                <span class="ms-2">de ${totalPages}</span>
            </div>
        `)
    );

    // Botão PRÓXIMO
    $pagination.append(
        $("<li>").addClass(`page-item ${state.currentPage === totalPages ? "disabled" : ""}`)
            .html(`<a class="page-link" href="#" onclick="changePage(${state.currentPage + 1})">
                <i class="bi bi-chevron-right"></i>
            </a>`)
    );

    // Botão ÚLTIMA página
    $pagination.append(
        $("<li>").addClass(`page-item ${state.currentPage === totalPages ? "disabled" : ""}`)
            .html(`<a class="page-link" href="#" onclick="changePage(${totalPages})" title="Última página">
                <i class="bi bi-chevron-double-right"></i>
            </a>`)
    );
}

// Mudar página
export function changePage(page) {
    if (page < 1 || page > Math.ceil(state.filteredData.length / state.pageSize)) return;
    state.currentPage = page;
    renderTable();
    updatePagination();
}

// Mudança do tamanho da página
export function changePageSize() {
    state.pageSize = parseInt($("#pageSize").val());
    state.currentPage = 1;
    updatePagination();
    renderTable();
}

// Expor para os onclick gerados no HTML da paginação
window.changePage = changePage;