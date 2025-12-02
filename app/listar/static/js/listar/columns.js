import { COLUMNS_CONFIG } from "./columns_config.js";
import { renderTableHeader, renderTable} from "./table.js";
import { setupSorting } from "./sorting.js";
import { setupFilters } from "./filters.js";
import { setupColumnResizing } from "./resize.js";
import { state, load } from "./main.js";


export function setupColumnVisibility() {
    $("#columnDropdown").on("change", ".column-toggle", function () {
        const column = $(this).val();
        const visible = $(this).is(":checked");

        // Atualiza config
        const colCfg = COLUMNS_CONFIG.find(c => c.key === column);
        colCfg.visible = visible;

        // Reconstrói o header + filtros
        renderTableHeader();
        renderTable(window.__lastLoadedItems);

        setupSorting((col, dir) => {
            state.sort = col;
            state.direction = dir;
            load();
        });

        setupFilters(values => {
            if (values.search !== undefined) state.search = values.search;
            state.page = 1;
            load();
        });

        setupColumnResizing();


        // Atualiza a tabela atual (tbody)
        $(`[data-column="${column}"]`).toggle(visible);
    });
}
