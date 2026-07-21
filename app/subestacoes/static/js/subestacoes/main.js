// main.js — ponto de entrada da página Subestações
import { initializeTooltips } from "./utils.js";
import { loadData, changePageSize } from "./table.js";
import { setupFilters, clearAllFilters } from "./filters.js";
import { setupSorting } from "./sorting.js";
import { setupColumns, loadTableSettings, saveTableSettings } from "./columns.js";
import { setupColumnResizing } from "./resize.js";
import { refreshData } from "./crud.js";
import "./export.js";
import "./detalhes.js";

// Estado global da aplicação (compartilhado entre os módulos)
export let state = {
    currentData: [],
    filteredData: [],
    currentPage: 1,
    pageSize: 25,
    sortColumn: "",
    sortDirection: "asc",
    columnFilters: {},
    permissoes: {}
};

// Inicialização
$(document).ready(function () {
    loadData();
    setupFilters();
    setupSorting();
    setupColumns();
    setupColumnResizing();
    initializeTooltips();
    loadTableSettings();

    // Tamanho da página
    $("#pageSize").on("change", function () {
        changePageSize();
        saveTableSettings();
    });

    // Fechar dropdowns ao clicar fora
    $(document).on("click", function (e) {
        if (!$(e.target).closest(".column-selector").length) {
            $("#columnDropdown").hide();
        }
        if (!$(e.target).closest(".export-dropdown").length) {
            $("#exportMenu").hide();
        }
    });

    // Atalhos de teclado
    $(document).on("keydown", function (e) {
        // Ctrl + F para busca global
        if (e.ctrlKey && e.key === "f") {
            e.preventDefault();
            $("#globalSearch").focus();
        }

        // Escape para limpar filtros
        if (e.key === "Escape") {
            clearAllFilters();
        }

        // Ctrl + R para atualizar
        if (e.ctrlKey && e.key === "r") {
            e.preventDefault();
            refreshData();
        }
    });
});