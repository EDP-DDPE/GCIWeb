    // table.js
    import { initializeTooltips } from "./utils.js";
    import { state } from "./main.js";
    import { COLUMNS_CONFIG } from "./columns_config.js";
    
    export function renderTable(data) {
        const $tbody = $("#tableBody");
        $tbody.empty();

        data.forEach(item => {
            const row = $("<tr></tr>");

            COLUMNS_CONFIG.forEach(col => {
                if (!col.visible) return;

                if (col.key === "acoes") {
                    row.append(`<td data-column="${col.key}">${buildActions(item)}</td>`);
                } else {
                    let value = item[col.key];

                    if (value === null || value === undefined) value = "";

                    row.append(`<td data-column="${col.key}">${value}</td>`);
                }
            });

            $tbody.append(row);
        });

        initializeTooltips();
    }
    
    export function renderPagination(page, hasNext, onPageChange) {
        const $pagination = $("#pagination");
        $pagination.empty();
    
        const addButton = (label, p, disabled = false, active = false) => {
            $pagination.append(`
                <li class="page-item ${disabled ? "disabled" : ""} ${active ? "active" : ""}">
                    <a class="page-link" href="#" data-page="${p}">${label}</a>
                </li>
            `);
        };
    
        addButton("Anterior", page - 1, page === 1);
        addButton(page, page, false, true);
        addButton("Próximo", page + 1, !hasNext);
    
        $("#pagination a").on("click", function (e) {
            e.preventDefault();
    
            const $li = $(this).closest("li");
            if ($li.hasClass("disabled") || $li.hasClass("active")) return;
    
            const newPage = parseInt($(this).data("page"));
            if (!isNaN(newPage)) onPageChange(newPage);
        });
    }
    
    export function updateRecordInfo(response) {
        const qtd = response.items.length;
    
        const start = qtd ? ((response.page - 1) * response.per_page) + 1 : 0;
        const end = ((response.page - 1) * response.per_page) + response.items.length;
    
        $("#startRecord").text(response.items.length ? start : 0);
        $("#endRecord").text(end);
        $("#totalRecords").text(`Página ${response.page}`);
    }
    
    export function renderTableHeader() {
        const headerRow = $("#tableHeader");
        const filterRow = $("#filterRow");

        headerRow.empty();
        filterRow.empty();

        COLUMNS_CONFIG.forEach(col => {
            if (!col.visible) return;

            headerRow.append(`
                <th class="resizable-header" data-column="${col.key}">
                    <div class="header-content d-flex align-items-center justify-content-between">
                        <span>${col.label}</span>
                        ${
                            col.key !== "acoes"
                                ? `<i class="fas ${getSortIcon(col.key)} sort-icon" data-sort="${col.key}"></i>`
                                : ""
                        }
                    </div>
            
                    <div class="resize-handle"></div>
                </th>
            `);

            if (col.key === "acoes") {
                filterRow.append(`<th data-column="${col.key}"></th>`);
            } else {
                const currentValue = state.columnFilters[col.key] || "";

                filterRow.append(`
                    <th data-column="${col.key}">
                        <input type="text"
                               class="filter-input"
                               data-filter="${col.key}"
                               value="${currentValue}"
                               placeholder="Filtrar ${col.label}...">
                    </th>
                `);
            }
        });
    }
    
    function buildActions(item) {
        const p = item._permissoes || {};
    
        let html = `<div class="btn-group btn-group-sm">`;
    
        if (p.visualizar) {
            html += `
                <button class="btn btn-outline-primary"
                    onclick="verDetalhes(${item.id_estudo})"
                    title="Visualizar">
                    <i class="fas fa-eye"></i>
                </button>
            `;
        }
    
        if (p.editar) {
            html += `
                <a href="/estudos/editar/${item.id_estudo}"
                   class="btn btn-outline-warning"
                   title="Editar">
                   <i class="fas fa-edit"></i>
                </a>
            `;

            html += `
                <a href="/estudo/${item.id_estudo}/alternativas/"
                   class="btn btn-outline-success"
                   title="Gerenciar alternativas">
                   <i class="bi bi-list-check"></i>
                </a>
            
            `;
        }

        html += `
            <button class="btn btn-outline-info"
                onclick="abrirStatus(${item.id_estudo})"
                title="Status">
                <i class="bi bi-clock-history"></i>
            </button>
        `;



    
        html += `</div>`;
    
        return html;
    }

    function getSortIcon(colKey) {
        if (state.sort !== colKey) return "fa-sort";

        return state.direction === "asc"
            ? "fa-sort-up"
            : "fa-sort-down";
    }