import { COLUMNS_CONFIG } from "./columns_config.js";
import { state } from "./main.js";

export function toggleExportMenu() {
    const menu = document.getElementById("exportMenu");

    if (!menu) return;

    // alterna visibilidade
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// fechar menu ao clicar fora
document.addEventListener("click", e => {
    const menu = document.getElementById("exportMenu");
    const btn = e.target.closest(".export-dropdown button");

    if (!menu) return;

    if (!btn && !menu.contains(e.target)) {
        menu.style.display = "none";
    }
});

export async function exportData(format) {

    // 1️⃣ Monta lista de colunas visíveis
    const visibleColumns = COLUMNS_CONFIG
        .filter(col => col.visible)
        .map(col => col.key);

    // 2️⃣ Monta URL da API com filtros + ordenação + colunas
    const params = new URLSearchParams({
        page: state.page,
        per_page: state.per_page,
        sort: state.sort,
        direction: state.direction,
        search: state.globalSearch || "",
        columns: visibleColumns.join(","),
        export: format,    // ← indica ao backend que é exportação
        per_page: 999999   // EXPORTA TUDO (desconsidera paginação visual)
    });

    const url = `/listar/api/estudos?${params.toString()}`;

    // 3️⃣ Faz requisição
    const response = await fetch(url);

    if (!response.ok) {
        alert("Erro ao gerar arquivo de exportação.");
        return;
    }

    // 4️⃣ Recebe o blob do arquivo
    const blob = await response.blob();

    // 5️⃣ Cria nome automático
    const filename = `atlas_export.${format}`;

    // 6️⃣ Baixa arquivo
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}
