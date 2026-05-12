import { COLUMNS_CONFIG } from "./columns_config.js";
import { renderTableHeader, renderTable } from "./table.js";
import { state, bindHeaderInteractions } from "./main.js";

export function setupColumnVisibility() {
    $("#columnDropdown").on("change", ".column-toggle", function () {
        const column = $(this).val();
        const visible = $(this).is(":checked");

        const colCfg = COLUMNS_CONFIG.find(c => c.key === column);
        colCfg.visible = visible;

        renderTableHeader();
        renderTable(window.__lastLoadedItems);
        bindHeaderInteractions();
    });
}