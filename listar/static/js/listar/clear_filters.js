import { state, load } from "./main.js";

export function clearAllFilters() {
    state.search = "";
    state.columnFilters = {};
    state.page = 1;

    $("#globalSearch").val("");
    $(".filter-input").val("");

    load();
}

window.clearAllFilters = clearAllFilters;
