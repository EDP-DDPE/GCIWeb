// export.js — exportação de dados (CSV / Excel / PDF)
import { state } from "./main.js";
import { downloadFile } from "./utils.js";

export function toggleExportMenu() {
    $("#exportMenu").toggle();
}

export function exportData(format) {
    const dados = state.filteredData.map(item => ({
        ID: item.id,
        "Viabilidade": item.viabilidade,
        "Viabilidade Abrev.": item.viabilidade_abrev,
        "Analise": item.analise,
        "Analise Abrev.": item.analise_abrev,
        "Pedido": item.pedido,
        "Pedido Abrev.": item.pedido_abrev
    }));

    switch (format) {
        case "csv":
            exportToCSV(dados);
            break;
        case "excel":
            exportToExcel(dados);
            break;
        case "pdf":
            exportToPDF(dados);
            break;
    }

    $("#exportMenu").hide();
}

function buildCSV(data) {
    const headers = Object.keys(data[0]);
    return [
        headers.join(","),
        ...data.map(row => headers.map(header => `"${row[header]}"`).join(","))
    ].join("\n");
}

function exportToCSV(data) {
    downloadFile(buildCSV(data), "tipo_solicitacao.csv", "text/csv");
}

function exportToExcel(data) {
    // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
    // Gera o mesmo CSV, apenas com extensão/mimetype de Excel
    downloadFile(
        buildCSV(data),
        "tipo_solicitacao.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
}

function exportToPDF(data) {
    // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
    let content = "LISTA DE TIPOS DE SOLICITACAO\n\n";

    const headers = Object.keys(data[0]);
    content += headers.join("\t") + "\n";
    content += "=".repeat(100) + "\n";

    data.forEach(row => {
        content += headers.map(header => row[header]).join("\t") + "\n";
    });

    downloadFile(content, "tipo_solicitacao.pdf", "application/pdf");
}

// Expor para os onclick do HTML (botão "Exportar" e itens do menu)
window.toggleExportMenu = toggleExportMenu;
window.exportData = exportData;