import { COLUMNS_CONFIG } from "./columns_config.js";

export function renderColumnDropdown() {
    const container = $("#columnDropdown");
    container.empty();

    COLUMNS_CONFIG.forEach(col => {
        container.append(`
            <div class="form-check">
                <input class="form-check-input column-toggle"
                       type="checkbox"
                       value="${col.key}"
                       id="col-${col.key}"
                       ${col.visible ? "checked" : ""}>
                <label class="form-check-label" for="col-${col.key}">
                    ${col.label}
                </label>
            </div>
        `);
    });

    // Botões "Todas" e "Nenhuma"
    container.append(`
        <hr>
        <button class="btn btn-sm btn-outline-primary me-2" id="btnSelectAll">Todas</button>
        <button class="btn btn-sm btn-outline-secondary" id="btnSelectNone">Nenhuma</button>
    `);
}
