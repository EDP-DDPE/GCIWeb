// sorting.js — ordenação das colunas
import { state } from "./main.js";
import { renderTable } from "./table.js";

export function setupSorting() {
    $(".sort-icon").on("click", handleSort);
}

export function handleSort(event) {
    const column = $(event.target).data("sort");

    if (state.sortColumn === column) {
        state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
    } else {
        state.sortColumn = column;
        state.sortDirection = "asc";
    }

    $(".sort-icon").removeClass("fa-sort-up fa-sort-down").addClass("fa-sort");
    $(event.target)
        .removeClass("fa-sort")
        .addClass(`fa-sort-${state.sortDirection === "asc" ? "up" : "down"}`);

    state.filteredData.sort((a, b) => {
        let aVal = a[column];
        let bVal = b[column];

        // Tratamento especial para números
        if (column === "id") {
            aVal = parseInt(aVal);
            bVal = parseInt(bVal);
        }

        // Coordenadas ordenam como número quando possível
        if (column === "lat" || column === "longitude") {
            const na = parseFloat(String(aVal).replace(",", "."));
            const nb = parseFloat(String(bVal).replace(",", "."));
            if (!isNaN(na) && !isNaN(nb)) {
                aVal = na;
                bVal = nb;
            }
        }

        if (aVal < bVal) return state.sortDirection === "asc" ? -1 : 1;
        if (aVal > bVal) return state.sortDirection === "asc" ? 1 : -1;
        return 0;
    });

    renderTable();
}