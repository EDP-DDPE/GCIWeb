// table.js
import { initializeTooltips } from "./utils.js";
import { COLUMNS_CONFIG } from "./columns_config.js";

export function renderTable(data) {
    const $tbody = $("#tableBody");
    $tbody.empty();

    data.forEach(item => {
        const row = $("<tr></tr>");

        COLUMNS_CONFIG.forEach(col => {
            if (!col.visible) return;

            let value = item[col.key];
            if (value === null || value === undefined) value = "";

            // Coluna de ações já vem renderizada do backend
            if (col.key === "acoes") {
                row.append(`<td data-column="${col.key}">${value}</td>`);
            } else {
                row.append(`<td data-column="${col.key}">${value}</td>`);
            }
        });

        $tbody.append(row);
    });

    initializeTooltips();
}

export function renderPagination(page, totalPages, onPageChange) {
    const $pagination = $("#pagination");
    $pagination.empty();

    if (totalPages <= 1) return;

    const addButton = (label, p, disabled = false, active = false) => {
        $pagination.append(`
            <li class="page-item ${disabled ? "disabled" : ""} ${active ? "active" : ""}">
                <a class="page-link" href="#" data-page="${p}">${label}</a>
            </li>
        `);
    };

    // anterior
    addButton("Anterior", page - 1, page === 1);

    // páginas
    for (let p = Math.max(1, page - 2); p <= Math.min(totalPages, page + 2); p++) {
        addButton(p, p, false, p === page);
    }

    // próximo
    addButton("Próximo", page + 1, page === totalPages);

    // eventos
    $("#pagination a").on("click", function (e) {
        e.preventDefault();
        const newPage = parseInt($(this).data("page"));
        if (!isNaN(newPage)) onPageChange(newPage);
    });
}

export function updateRecordInfo(response) {
    const start = (response.page - 1) * response.per_page + 1;
    const end = Math.min(response.page * response.per_page, response.total);

    $("#startRecord").text(start);
    $("#endRecord").text(end);
    $("#totalRecords").text(response.total);
}

export function renderTableHeader() {
    const headerRow = $("#tableHeader");
    const filterRow = $("#filterRow");

    headerRow.empty();
    filterRow.empty();

    COLUMNS_CONFIG.forEach(col => {
        if (!col.visible) {
            headerRow.append(`<th data-column="${col.key}" style="display:none;"></th>`);
            filterRow.append(`<th data-column="${col.key}" style="display:none;"></th>`);
            return;
        }

        // Cabeçalho com sort e resize
        headerRow.append(`
            <th class="resizable-header" data-column="${col.key}">
                <div class="d-flex align-items-center justify-content-between">
                    <span>${col.label}</span>
                    <div class="d-flex align-items-center">
                        ${col.key !== "acoes" ? `<i class="fas fa-sort sort-icon" data-sort="${col.key}"></i>` : ""}
                        <div class="resize-handle"></div>
                    </div>
                </div>
            </th>
        `);

        // Linha de filtros (exceto Ações)
        if (col.key === "acoes") {
            filterRow.append(`<th data-column="${col.key}"></th>`);
        } else {
            filterRow.append(`
                <th data-column="${col.key}">
                    <input type="text" class="filter-input" data-filter="${col.key}" placeholder="Filtrar ${col.label}...">
                </th>
            `);
        }
    });
}