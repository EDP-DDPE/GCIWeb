import { fetchEstudos } from "./api.js";
import { renderTable, renderPagination, updateRecordInfo, renderTableHeader} from "./table.js";
import { setupFilters } from "./filters.js";
import { setupSorting } from "./sorting.js";
import { setupColumnVisibility } from "./columns.js";
import { setupColumnResizing } from "./resize.js";
import { renderColumnDropdown } from "./column_dropdown.js";
import { exportData,toggleExportMenu } from "./export.js";
import { configurarFormularioStatus } from "./status.js";

configurarFormularioStatus();
window.toggleExportMenu = toggleExportMenu;
window.exportData = exportData;
window.__lastLoadedItems = [];

export let state = {
    page: 1,
    perPage: 25,
    search: "",
    sort: "id_estudo",
    direction: "desc",
    columnFilters: {},
    hasNext: false
};

export function load() {
    window.showLoading();

    fetchEstudos(state).done(resp => {
        window.__lastLoadedItems = resp.items;
        state.hasNext = resp.has_next;

        renderTable(resp.items);
        renderPagination(resp.page, resp.has_next, p => {
            state.page = p;
            load();
        });

        updateRecordInfo(resp);
        window.hideLoading();
    });
}

export function bindHeaderInteractions() {
    setupFilters(values => {
        if (values.search !== undefined) state.search = values.search;

        if (values.column !== undefined) {
            state.columnFilters[values.column] = values.value || "";
            if (!values.value) delete state.columnFilters[values.column];
        }

        state.page = 1;
        load();
    });

    setupSorting((col, dir) => {
        state.sort = col;
        state.direction = dir;
        state.page = 1;
        load();
    });

    setupColumnResizing();
}

$(document).ready(() => {
    renderColumnDropdown();
    renderTableHeader();
    restoreSearchValues();
    bindHeaderInteractions();

    $("#pageSize").on("change", function () {
        state.perPage = parseInt($(this).val());
        state.page = 1;
        load();
    });

    setupColumnVisibility();
    load();
});

$("#btnColumnSelector").on("click", () => $("#columnDropdown").toggle());
$("#btnExport").on("click", () => $("#exportMenu").toggle());

$(document).on("click", function (e) {
    if (!$(e.target).closest(".column-selector").length) $("#columnDropdown").hide();
    if (!$(e.target).closest(".export-dropdown").length) $("#exportMenu").hide();
});

window.atualizarLista = function() {
    load();
};

function restoreSearchValues() {
    $("#globalSearch").val(state.search);
}