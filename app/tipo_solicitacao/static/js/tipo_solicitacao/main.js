// main.js — ponto de entrada da página Tipos de Solicitação
import { initializeTooltips } from "./utils.js";
import { loadData, changePageSize } from "./table.js";
import { setupFilters, clearAllFilters } from "./filters.js";
import { setupSorting } from "./sorting.js";
import { setupColumns, loadTableSettings, saveTableSettings } from "./columns.js";
import { setupColumnResizing } from "./resize.js";
import { refreshData } from "./crud.js";
import "./export.js";
import "./documentos.js";

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

    // Limpar input de arquivo ao fechar os modais de documento
    const modalDoc = document.getElementById("modalDocumento");
    if (modalDoc) {
        modalDoc.addEventListener("hidden.bs.modal", function () {
            $("#arquivoDocumento").val("");
        });
    }

    const modalDocInverso = document.getElementById("modalDocumentoInverso");
    if (modalDocInverso) {
        modalDocInverso.addEventListener("hidden.bs.modal", function () {
            $("#arquivoDocumentoInverso").val("");
        });
    }

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