// filters.js — busca global, filtros por coluna e limpeza de filtros
import { state } from "./main.js";
import { debounce } from "./utils.js";
import { renderTable, updatePagination } from "./table.js";

export function setupFilters() {
    // Busca global
    $("#globalSearch").on("input", debounce(applyGlobalSearch, 300));

    // Filtros por coluna
    $(".filter-input").on("input", debounce(applyColumnFilter, 300));
}

// Busca global
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

// Filtros por coluna
export function applyColumnFilter(event) {
    const column = $(event.target).data("filter");
    const value = $(event.target).val().toLowerCase();

    if (value === "") {
        delete state.columnFilters[column];
    } else {
        state.columnFilters[column] = value;
    }

    // Aplicar todos os filtros
    state.filteredData = state.currentData.filter(item => {
        for (let [col, filter] of Object.entries(state.columnFilters)) {
            if (col === "data_registro" && filter) {
                // Para datas, comparar apenas a parte da data
                const itemDate = new Date(item[col]).toISOString().split("T")[0];
                if (itemDate !== filter) return false;
            } else {
                if (!String(item[col]).toLowerCase().includes(filter)) return false;
            }
        }
        return true;
    });

    state.currentPage = 1;
    updatePagination();
    renderTable();
}

export function clearAllFilters() {
    // Limpar busca global
    $("#globalSearch").val("");

    // Limpar filtros por coluna
    $(".filter-input").val("");

    // Resetar dados
    state.columnFilters = {};
    state.filteredData = [...state.currentData];
    state.currentPage = 1;

    // Resetar ordenação
    state.sortColumn = "";
    state.sortDirection = "asc";
    $(".sort-icon").removeClass("fa-sort-up fa-sort-down").addClass("fa-sort");

    updatePagination();
    renderTable();
}

// Indicador de filtros ativos (opcional)
export function updateFilterIndicator() {
    const hasFilters = Object.keys(state.columnFilters).length > 0 ||
        $("#globalSearch").val().trim() !== "";

    let $indicator = $(".filter-indicator");
    if (!$indicator.length) {
        $indicator = $("<div>").addClass("filter-indicator badge bg-info ms-2");
        $("h2").append($indicator);
    }

    if (hasFilters) {
        $indicator.text("Filtros ativos").show();
    } else {
        $indicator.hide();
    }
}

// Expor para o onclick do botão "Limpar Filtros"
window.clearAllFilters = clearAllFilters;