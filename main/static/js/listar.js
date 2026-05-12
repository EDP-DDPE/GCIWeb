// listar.js

document.addEventListener("DOMContentLoaded", () => {
    initGlobalSearch();
    console.log("Cheguei aqui!");
    initPagination();
    initColumnSelector();
    initFilters();
});

// ------------------------------
// 🔄 Atualizar dados
// ------------------------------
function refreshData() {
    location.reload(); // simples: recarrega a página
}

// ------------------------------
// 🔍 Busca global
// ------------------------------
function initGlobalSearch() {
    const searchInput = document.getElementById("globalSearch");
    if (!searchInput) return;

    searchInput.addEventListener("input", function () {
        const filter = this.value.toLowerCase();
        const rows = document.querySelectorAll("#tableBody tr");

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            row.style.display = text.includes(filter) ? "" : "none";
        });

        updatePagination();
    });
}

// ------------------------------
// 📑 Paginação
// ------------------------------
let currentPage = 1;
let pageSize = 25;

function initPagination() {
    const pageSizeSelect = document.getElementById("pageSize");
    if (!pageSizeSelect) return;

    pageSizeSelect.addEventListener("change", function () {
        pageSize = parseInt(this.value, 10);
        currentPage = 1;
        updatePagination();
    });

    updatePagination();
}

function updatePagination() {
    const rows = [...document.querySelectorAll("#tableBody tr")].filter(r => r.style.display !== "none");
    const total = rows.length;
    const totalPages = Math.ceil(total / pageSize);

    rows.forEach((row, index) => {
        row.style.display = (index >= (currentPage - 1) * pageSize && index < currentPage * pageSize) ? "" : "none";
    });

    document.getElementById("startRecord").textContent = (total === 0) ? 0 : (currentPage - 1) * pageSize + 1;
    document.getElementById("endRecord").textContent = Math.min(currentPage * pageSize, total);
    document.getElementById("totalRecords").textContent = total;

    renderPagination(totalPages);
}

function renderPagination(totalPages) {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement("li");
        li.className = `page-item ${i === currentPage ? "active" : ""}`;
        li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        li.addEventListener("click", (e) => {
            e.preventDefault();
            currentPage = i;
            updatePagination();
        });
        pagination.appendChild(li);
    }
}

// ------------------------------
// 📊 Seletor de colunas
// ------------------------------
function initColumnSelector() {
    document.querySelectorAll(".column-toggle").forEach(checkbox => {
        checkbox.addEventListener("change", function () {
            const colName = this.value;
            toggleColumn(colName, this.checked);
        });
    });
}

function toggleColumn(colName, show) {
    document.querySelectorAll(`[data-column="${colName}"]`).forEach(cell => {
        cell.style.display = show ? "" : "none";
    });
}

function toggleColumnSelector() {
    const dropdown = document.getElementById("columnDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

function selectAllColumns() {
    document.querySelectorAll(".column-toggle").forEach(cb => {
        cb.checked = true;
        toggleColumn(cb.value, true);
    });
}

function deselectAllColumns() {
    document.querySelectorAll(".column-toggle").forEach(cb => {
        cb.checked = false;
        toggleColumn(cb.value, false);
    });
}

// ------------------------------
// 📤 Exportação
// ------------------------------
function toggleExportMenu() {
    const menu = document.getElementById("exportMenu");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
}

function exportData(format) {
    alert(`Exportar como ${format} ainda não implementado.`);
    // Aqui você pode implementar exportação real (CSV, Excel, PDF)
}

// ------------------------------
// 🚮 Filtros por coluna
// ------------------------------
function initFilters() {
    document.querySelectorAll(".filter-input").forEach(input => {
        input.addEventListener("input", applyFilters);
    });
}

function applyFilters() {
    const filters = {};
    document.querySelectorAll(".filter-input").forEach(input => {
        const key = input.dataset.filter;
        filters[key] = input.value.toLowerCase();
    });

    const rows = document.querySelectorAll("#tableBody tr");
    rows.forEach(row => {
        let visible = true;
        Object.entries(filters).forEach(([key, value]) => {
            if (!value) return;
            const cell = row.querySelector(`[data-column="${key}"]`);
            if (cell && !cell.innerText.toLowerCase().includes(value)) {
                visible = false;
            }
        });
        row.style.display = visible ? "" : "none";
    });

    updatePagination();
}

function clearAllFilters() {
    document.querySelectorAll(".filter-input").forEach(input => input.value = "");
    applyFilters();
}
