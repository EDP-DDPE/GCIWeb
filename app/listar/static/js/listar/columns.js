import { COLUMNS_CONFIG } from "./columns_config.js";
import { renderTableHeader, renderTable } from "./table.js";
import { setupSorting } from "./sorting.js";
import { setupFilters } from "./filters.js";
import { setupColumnResizing } from "./resize.js";
import { state, load, bindHeaderInteractions } from "./main.js";

export function setupColumnVisibility() {
    $("#columnDropdown").on("change", ".column-toggle", function () {
        const column = $(this).val();
        const visible = $(this).is(":checked");

        const colCfg = COLUMNS_CONFIG.find(c => c.key === column);
        colCfg.visible = visible;

        // recria header + body
        renderTableHeader();
        renderTable(window.__lastLoadedItems);
        bindHeaderInteractions();
    });
}