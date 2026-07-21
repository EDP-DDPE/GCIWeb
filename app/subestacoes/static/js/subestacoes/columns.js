// columns.js — seleção/visibilidade de colunas e persistência das configurações
import { state } from "./main.js";

export function setupColumns() {
    $(".column-toggle").on("change", function (event) {
        toggleColumn(event);
        saveTableSettings();
    });
}

export function toggleColumnSelector() {
    $("#columnDropdown").toggle();
}

export function toggleColumn(event) {
    const column = $(event.target).val();
    const isVisible = $(event.target).is(":checked");
    $(`[data-column="${column}"]`).toggle(isVisible);
}

export function selectAllColumns() {
    $(".column-toggle").each(function () {
        $(this).prop("checked", true);
        $(`[data-column="${$(this).val()}"]`).show();
    });
    saveTableSettings();
}

export function deselectAllColumns() {
    $(".column-toggle").each(function () {
        if ($(this).val() !== "acoes") { // Manter sempre ações visíveis
            $(this).prop("checked", false);
            $(`[data-column="${$(this).val()}"]`).hide();
        }
    });
    saveTableSettings();
}

export function applyColumnVisibility() {
    $(".column-toggle").each(function () {
        const column = $(this).val();
        const isVisible = $(this).is(":checked");
        $(`[data-column="${column}"]`).toggle(isVisible);
    });
}

export function saveTableSettings() {
    const settings = {
        pageSize: state.pageSize,
        columnVisibility: {}
    };

    $(".column-toggle").each(function () {
        settings.columnVisibility[$(this).val()] = $(this).is(":checked");
    });

    try {
        localStorage.setItem("subestacoesTableSettings", JSON.stringify(settings));
    } catch (e) {
        // localStorage não disponível
    }
}

export function loadTableSettings() {
    try {
        const settings = JSON.parse(localStorage.getItem("subestacoesTableSettings") || "{}");

        if (settings.pageSize) {
            state.pageSize = settings.pageSize;
            $("#pageSize").val(state.pageSize);
        }

        if (settings.columnVisibility) {
            $.each(settings.columnVisibility, function (column, visible) {
                const $checkbox = $(`#col-${column}`);
                if ($checkbox.length) {
                    $checkbox.prop("checked", visible);
                    toggleColumn({ target: $checkbox[0] });
                }
            });
        }
    } catch (e) {
        // Erro ao carregar configurações
    }
}

// Expor para os onclick do HTML
window.toggleColumnSelector = toggleColumnSelector;
window.selectAllColumns = selectAllColumns;
window.deselectAllColumns = deselectAllColumns;