// main.js
import { fetchEstudos } from "./api.js";
import { renderTable, renderPagination, updateRecordInfo, renderTableHeader} from "./table.js";
import { setupFilters } from "./filters.js";
import { setupSorting } from "./sorting.js";
import { setupColumnVisibility } from "./columns.js";
import { setupColumnResizing } from "./resize.js";
import { initializeTooltips } from "./utils.js";
import { COLUMNS_CONFIG } from "./columns_config.js";
import { renderColumnDropdown } from "./column_dropdown.js";
import { exportData,toggleExportMenu } from "./export.js";
import { abrirStatus, configurarFormularioStatus, showStatusLoading, hideStatusLoading } from "./status.js";


configurarFormularioStatus();
window.toggleExportMenu = toggleExportMenu;
window.exportData = exportData;
window.__lastLoadedItems = [];

function loadColumnSelector() {
    const container = $("#columnDropdown");
    container.empty();


    COLUMNS_CONFIG.forEach(col => {
        container.append(`
            <div class="form-check">
                <input class="form-check-input column-toggle"
                    type="checkbox"
                    value="${col.key}"
                    id="col-${col.key}"
                    ${col.visible ? "checked" : ""} />

                <label class="form-check-label" for="col-${col.key}">
                    ${col.label}
                </label>
            </div>
        `);
    });
}

export let state = {
    page: 1,
    perPage: 25,
    search: "",
    sort: "id_estudo",
    direction: "desc",
    columnFilters: {}
};

export function load() {
    window.showLoading();

    fetchEstudos(state).done(resp => {
        window.__lastLoadedItems = resp.items;
        renderTable(resp.items);
        renderPagination(resp.page, resp.pages, p => {
            state.page = p;
            load();
        });
        updateRecordInfo(resp);
        window.hideLoading();
    });
}

$(document).ready(() => {

    renderColumnDropdown();
    renderTableHeader();

    setupFilters(values => {
        if (values.search !== undefined) {
            state.search = values.search;
        }

        if (values.column !== undefined) {
            state.columnFilters[values.column] = values.value || "";

            // se apagou o valor, remove o filtro
            if (!values.value) {
                delete state.columnFilters[values.column];
            }
        }

        state.page = 1;
        load();
    });

    setupSorting((col, dir) => {
        state.sort = col;
        state.direction = dir;
        load();
    });

    $("#pageSize").on("change", function () {
        state.perPage = parseInt($(this).val());
        state.page = 1;
        load();
    });

    setupColumnVisibility();
    setupColumnResizing();

    load();
});

$("#btnColumnSelector").on("click", () => {
    $("#columnDropdown").toggle();
});

$("#btnExport").on("click", () => {
    $("#exportMenu").toggle();
});

$(document).on("click", function (e) {
    if (!$(e.target).closest(".column-selector").length) {
        $("#columnDropdown").hide();
    }
    if (!$(e.target).closest(".export-dropdown").length) {
        $("#exportMenu").hide();
    }
});

// Atualizar lista mantendo estado
window.atualizarLista = function() {
    load();  // Recarrega com paginação + filtros + ordenação atuais
};
