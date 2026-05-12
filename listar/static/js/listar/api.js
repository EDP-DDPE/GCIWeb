import { state } from "./main.js";
import { getVisibleColumnKeys } from "./columns_config.js";

export function fetchEstudos() {
    return $.get("/listar/api/estudos", {
        page: state.page,
        per_page: state.perPage,
        search: state.search,
        sort: state.sort,
        direction: state.direction,
        filters: JSON.stringify(state.columnFilters),
        columns: getVisibleColumnKeys().join(",")
    });
}