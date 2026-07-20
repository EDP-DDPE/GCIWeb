// table.js — carregamento via API, renderização da tabela e paginação
import { state } from "./main.js";
import { showLoading, hideLoading, initializeTooltips } from "./utils.js";
import { applyColumnVisibility } from "./columns.js";

// Busca os dados na API e re-renderiza a tabela (substitui o antigo initializeData)
export function loadData() {
    showLoading();

    return $.get("/tipo_solicitacao/api/listar")
        .done(function (resp) {
            state.permissoes = resp.permissoes || {};

            state.currentData = (resp.items || []).map(item => ({
                id: String(item.id),
                viabilidade: item.viabilidade || "",
                viabilidade_abrev: item.viabilidade_abrev || "",
                analise: item.analise || "",
                analise_abrev: item.analise_abrev || "",
                pedido: item.pedido || "",
                pedido_abrev: item.pedido_abrev || "",
                status_doc: item.status.texto,   // texto puro (busca, filtro e ordenação)
                status: item.status              // objeto completo (renderiza o badge)
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

function buildStatusBadge(status) {
    const title = (status.dias !== null && status.dias !== undefined)
        ? `Próxima revisão: ${status.data_limite}`
        : "Nenhum documento cadastrado";

    return `
        <span class="badge bg-${status.classe} d-flex align-items-center gap-1"
              style="width: fit-content;"
              data-bs-toggle="tooltip"
              title="${title}">
            <i class="bi ${status.icone}"></i>
            ${status.texto}
        </span>
    `;
}

function buildActions(item) {
    const podeEditar = state.permissoes && state.permissoes.editar;

    let html = `
        <div class="btn-group" role="group">
            <button class="btn btn-sm btn-warning"
                onclick="editarDetalhes(${item.id})"
                data-bs-toggle="tooltip"
                title="Editar Tipo de Solicitação"
                ${podeEditar ? "" : "disabled"}>
                <i class="bi bi-pencil-square"></i>
            </button>

            <button class="btn btn-sm btn-info"
                onclick="abrirModalDocumento(${item.id}, 0)"
                data-bs-toggle="tooltip"
                title="Documento Padrão">
                <i class="bi bi-file-earmark-text"></i>
            </button>
    `;

    if (item.analise && item.analise.includes("MMGD")) {
        html += `
            <button class="btn btn-sm btn-success"
                onclick="abrirModalDocumento(${item.id}, 1)"
                data-bs-toggle="tooltip"
                title="Documento Padrão – Fluxo Inverso">
                <i class="bi bi-file-earmark-text"></i>
            </button>
        `;
    }

    return html + "</div>";
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
        $("<td>").attr("data-column", "viabilidade").text(item.viabilidade).appendTo($row);
        $("<td>").attr("data-column", "viabilidade_abrev").text(item.viabilidade_abrev).appendTo($row);
        $("<td>").attr("data-column", "analise").text(item.analise).appendTo($row);
        $("<td>").attr("data-column", "analise_abrev").text(item.analise_abrev).appendTo($row);
        $("<td>").attr("data-column", "pedido").text(item.pedido).appendTo($row);
        $("<td>").attr("data-column", "pedido_abrev").text(item.pedido_abrev).appendTo($row);
        $("<td>").attr("data-column", "status_doc").html(buildStatusBadge(item.status)).appendTo($row);
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

    // Atualizar informações
    $("#startRecord").text(totalRecords > 0 ? start : 0);
    $("#endRecord").text(end);
    $("#totalRecords").text(totalRecords);

    // Mostrar informação de filtro se necessário
    const $filteredInfo = $("#filteredInfo");
    const $originalTotal = $("#originalTotal");
    if (totalRecords < state.currentData.length) {
        $originalTotal.text(state.currentData.length);
        $filteredInfo.show();
    } else {
        $filteredInfo.hide();
    }

    // Gerar paginação
    const $pagination = $("#pagination");
    $pagination.empty();
    if (totalPages <= 1) return;

    // Botão PRIMEIRA página
    const $firstLi = $("<li>").addClass(`page-item ${state.currentPage === 1 ? "disabled" : ""}`)
        .html(`<a class="page-link" href="#" onclick="changePage(1)" title="Primeira página">
            <i class="bi bi-chevron-double-left"></i>
        </a>`);
    $pagination.append($firstLi);

    // Botão ANTERIOR
    const $prevLi = $("<li>").addClass(`page-item ${state.currentPage === 1 ? "disabled" : ""}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${state.currentPage - 1})">
            <i class="bi bi-chevron-left"></i>
        </a>`);
    $pagination.append($prevLi);

    // Input para digitar número da página
    const $inputLi = $("<li>").addClass("page-item")
        .html(`
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
        `);
    $pagination.append($inputLi);

    // Botão PRÓXIMO
    const $nextLi = $("<li>").addClass(`page-item ${state.currentPage === totalPages ? "disabled" : ""}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${state.currentPage + 1})">
            <i class="bi bi-chevron-right"></i>
        </a>`);
    $pagination.append($nextLi);

    // Botão ÚLTIMA página
    const $lastLi = $("<li>").addClass(`page-item ${state.currentPage === totalPages ? "disabled" : ""}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${totalPages})" title="Última página">
            <i class="bi bi-chevron-double-right"></i>
        </a>`);
    $pagination.append($lastLi);
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