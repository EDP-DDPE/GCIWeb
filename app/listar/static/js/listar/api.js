import { state } from "./main.js";

// api.js
export function fetchEstudos({ page, perPage, search, sort, direction }) {
    return $.get("/listar/api/estudos", {
        page: state.page,
        per_page: state.perPage,
        search: state.search,
        sort: state.sort,
        direction: state.direction,
        filters: JSON.stringify(state.columnFilters)
    });
}