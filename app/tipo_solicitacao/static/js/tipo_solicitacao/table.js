// table.js — leitura dos dados, renderização da tabela e paginação
import { state } from "./main.js";
import { showLoading, hideLoading, initializeTooltips } from "./utils.js";
import { applyColumnVisibility } from "./columns.js";

// Inicializar dados a partir das linhas renderizadas pelo Jinja
export function initializeData() {
    const tableRows = $("#tableBody tr");
    state.currentData = tableRows.map(function () {
        const cells = $(this).find("td");
        return {
            id: cells.eq(0).text().trim(),
            viabilidade: cells.eq(1).text().trim(),
            viabilidade_abrev: cells.eq(2).text().trim(),
            analise: cells.eq(3).text().trim(),
            analise_abrev: cells.eq(4).text().trim(),
            pedido: cells.eq(5).text().trim(),
            pedido_abrev: cells.eq(6).text().trim(),
            status_doc: cells.eq(7).text().trim(),
            acoes: cells.eq(8).clone(),
            element: this
        };
    }).get();

    state.filteredData = [...state.currentData];
    updatePagination();
    renderTable();
}

// Renderizar tabela
export function renderTable() {
    showLoading();

    setTimeout(() => {
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

            // status_doc: clona o TD original para preservar o badge colorido
            const original = state.currentData.find(d => d.id === item.id);
            if (original) {
                const $originalRow = $(original.element);
                const $statusCell = $originalRow.find('[data-column="status_doc"]').clone(true);
                $row.append($statusCell);
            } else {
                $("<td>").attr("data-column", "status_doc").text(item.status_doc).appendTo($row);
            }

            const $tdAcoes = $("<td>").attr("data-column", "acoes");
            $tdAcoes.append(item.acoes.clone(true));
            $row.append($tdAcoes);

            $tbody.append($row);
        });

        applyColumnVisibility();
        initializeTooltips();
        hideLoading();
    }, 200);
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