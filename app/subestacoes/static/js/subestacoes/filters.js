// filters.js — busca global, filtros por coluna e limpeza de filtros
import { state } from "./main.js";
import { debounce } from "./utils.js";
import { renderTable, updatePagination } from "./table.js";

export function setupFilters() {
    $("#globalSearch").on("input", debounce(applyGlobalSearch, 300));
    $(".filter-input").on("input", debounce(applyColumnFilter, 300));
}

export function applyGlobalSearch() {
    const searchTerm = $("#globalSearch").val().toLowerCase();

    if (!searchTerm) {
        state.filteredData = [...state.currentData];
    } else {
        state.filteredData = state.currentData.filter(item =>
            Object.values(item).some(value =>
                String(value).toLowerCase().includes(searchTerm)
            )
        );
    }

    state.currentPage = 1;
    updatePagination();
    renderTable();
}

export function applyColumnFilter(event) {
    const column = $(event.target).data("filter");
    const value = $(event.target).val().toLowerCase();

    if (value === "") {
        delete state.columnFilters[column];
    } else {
        state.columnFilters[column] = value;
    }

    state.filteredData = state.currentData.filter(item => {
        for (let [col, filter] of Object.entries(state.columnFilters)) {
            if (!String(item[col]).toLowerCase().includes(filter)) return false;
        }
        return true;
    });

    state.currentPage = 1;
    updatePagination();
    renderTable();
}

export function clearAllFilters() {
    $("#globalSearch").val("");
    $(".filter-input").val("");

    state.columnFilters = {};
    state.filteredData = [...state.currentData];
    state.currentPage = 1;

    state.sortColumn = "";
    state.sortDirection = "asc";
    $(".sort-icon").removeClass("fa-sort-up fa-sort-down").addClass("fa-sort");

    updatePagination();
    renderTable();
}

// Expor para o onclick do botão "Limpar Filtros"
window.clearAllFilters = clearAllFilters;