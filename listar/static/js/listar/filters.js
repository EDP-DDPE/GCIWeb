import { debounce } from "./utils.js";

export function setupFilters(onFilter) {

    // --- FILTRO GLOBAL ---
    $("#globalSearch")
        .off("input")  // remove eventos duplicados
        .on("input", debounce(e => {
            const value = e.target.value.trim();
            onFilter({ search: value });
        }, 400)); // debounce de 400ms


    // --- FILTRO POR COLUNA ---
    $(".filter-input")
        .off("input") // remove eventos anteriores
        .on("input", debounce(e => {
            const col = $(e.target).data("filter");
            const value = $(e.target).val().trim();
            onFilter({ column: col, value });
        }, 400));
}