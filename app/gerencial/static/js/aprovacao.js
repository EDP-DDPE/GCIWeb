// Página gerencial de aprovação — tabela dinâmica (busca, filtros por coluna,
// ordenação, seleção de colunas, exportação e paginação) + gráfico de resumo.
(function () {
    "use strict";

    // Colunas disponíveis (mesmas da view do listar). `visible` define o
    // conjunto padrão exibido; o usuário liga/desliga pelo seletor de colunas.
    const COLUMNS = [
        { key: "id_estudo", label: "ID", visible: false },
        { key: "num_doc", label: "Nº Documento", visible: true },
        { key: "protocolo", label: "Protocolo", visible: false },
        { key: "nome_projeto", label: "Projeto", visible: true },
        { key: "descricao", label: "Descrição", visible: false },
        { key: "instalacao", label: "Instalação", visible: false },
        { key: "n_alternativas", label: "Nº Alternativas", visible: false },
        { key: "empresa", label: "Empresa", visible: true },
        { key: "regional", label: "Regional", visible: false },
        { key: "nome_criador", label: "Criado por", visible: false },
        { key: "nome_responsavel", label: "Responsável", visible: true },
        { key: "nome_empresa", label: "Nome Empresa", visible: false },
        { key: "municipio", label: "Município", visible: true },
        { key: "data_registro", label: "Data Registro", visible: false },
        { key: "viabilidade", label: "Viabilidade", visible: false },
        { key: "analise", label: "Análise", visible: true },
        { key: "pedido", label: "Pedido", visible: false },
        { key: "data_abertura_cliente", label: "Abertura Cliente", visible: false },
        { key: "data_desejada_cliente", label: "Data Desejada", visible: false },
        { key: "data_vencimento_cliente", label: "Vencimento Cliente", visible: false },
        { key: "data_prevista_conexao", label: "Conexão Prevista", visible: false },
        { key: "data_vencimento_ddpe", label: "Vencimento DDPE", visible: false },
        { key: "tensao", label: "Tensão", visible: false },
        { key: "qtd_anexos", label: "Nº Anexos", visible: false },
        { key: "custo_modular", label: "Custo Modular", visible: true },
        { key: "alternativa_circuito", label: "Circuito", visible: false },
        { key: "subestacao", label: "Subestação", visible: false },
        { key: "ultimo_status", label: "Status", visible: true },
        { key: "acoes", label: "Ações", visible: true },
    ];

    const state = {
        page: 1,
        perPage: 25,
        search: "",
        sort: "custo_modular",
        direction: "desc",
        columnFilters: {},
        minValor: parseFloat($("#valorFiltro").val()) || 0,
        hasNext: false,
    };

    let grafico = null;
    let lastItems = [];

    // ===================== Helpers =====================
    function debounce(fn, delay = 400) {
        let t;
        return function (...args) {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    function visibleColumns() {
        return COLUMNS.filter(c => c.visible);
    }

    function visibleKeys() {
        const keys = visibleColumns().map(c => c.key).filter(k => k !== "acoes");
        if (!keys.includes("id_estudo")) keys.push("id_estudo");
        return keys;
    }

    function formatarMoeda(v) {
        const n = parseFloat(v);
        if (isNaN(n)) return v || "";
        return "R$ " + n.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function escapeHtml(s) {
        return String(s ?? "").replace(/[&<>"']/g, c =>
            ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
    }

    function badgeStatus(status) {
        if (!status) return '<span class="badge bg-light text-muted">Sem status</span>';
        let cor = "bg-secondary";
        if (status === "Aprovado" || status === "Aprovado Gestor") cor = "bg-success";
        else if (["Reprovado", "Reprovado Gestor", "Rejeitado Gestor"].includes(status)) cor = "bg-danger";
        return `<span class="badge ${cor}">${escapeHtml(status)}</span>`;
    }

    // ===================== Dados =====================
    function fetchData() {
        return $.get("/gestao/api/aprovacao", {
            page: state.page,
            per_page: state.perPage,
            search: state.search,
            sort: state.sort,
            direction: state.direction,
            filters: JSON.stringify(state.columnFilters),
            columns: visibleKeys().join(","),
            min_valor: state.minValor,
        });
    }

    function load() {
        if (window.showLoading) window.showLoading();
        fetchData()
            .done(resp => {
                lastItems = resp.items || [];
                state.hasNext = resp.has_next;
                renderBody(lastItems);
                renderPagination(resp);
                updateInfo(resp);
            })
            .fail(err => console.error("Erro ao carregar estudos:", err))
            .always(() => { if (window.hideLoading) window.hideLoading(); });
    }

    function loadChart() {
        $.getJSON("/gestao/api/resumo", { min_valor: state.minValor }, function (resumo) {
            const dados = [resumo.Aprovado || 0, resumo.Reprovado || 0, resumo.Pendente || 0];
            if (grafico) {
                grafico.data.datasets[0].data = dados;
                grafico.update();
                return;
            }
            const ctx = document.getElementById("graficoResumo");
            if (!ctx) return;
            grafico = new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: ["Aprovado", "Reprovado", "Pendente"],
                    datasets: [{ data: dados, backgroundColor: ["#198754", "#dc3545", "#6c757d"], borderWidth: 1 }],
                },
                options: {
                    maintainAspectRatio: false,
                    aspectRatio: 2,
                    plugins: {
                        legend: { position: "bottom" },
                        tooltip: { callbacks: { label: c => `${c.label}: ${c.raw}` } },
                    },
                },
            });
        });
    }

    // ===================== Render =====================
    function renderHeader() {
        const $h = $("#tableHeader").empty();
        const $f = $("#filterRow").empty();

        visibleColumns().forEach(col => {
            const sortIcon = col.key === state.sort
                ? (state.direction === "asc" ? "fa-sort-up" : "fa-sort-down")
                : "fa-sort";

            $h.append(`
                <th class="resizable-header" data-column="${col.key}">
                    <div class="header-content d-flex align-items-center justify-content-between">
                        <span>${col.label}</span>
                        ${col.key !== "acoes"
                            ? `<i class="fas ${sortIcon} sort-icon" data-sort="${col.key}" style="cursor:pointer;"></i>`
                            : ""}
                    </div>
                    <div class="resize-handle"></div>
                </th>`);

            if (col.key === "acoes") {
                $f.append(`<th data-column="${col.key}"></th>`);
            } else {
                const val = state.columnFilters[col.key] || "";
                $f.append(`
                    <th data-column="${col.key}">
                        <input type="text" class="filter-input" data-filter="${col.key}"
                               value="${escapeHtml(val)}" placeholder="Filtrar ${col.label}...">
                    </th>`);
            }
        });

        bindHeaderEvents();
    }

    function renderBody(data) {
        const $tbody = $("#tableBody").empty();

        if (!data.length) {
            const span = visibleColumns().length || 1;
            $tbody.append(`<tr><td colspan="${span}" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-4 d-block mb-2"></i>Nenhum projeto encontrado.</td></tr>`);
            return;
        }

        data.forEach(item => {
            const id = item.id_estudo;
            const $row = $(`<tr id="estudo-${id}"></tr>`);

            visibleColumns().forEach(col => {
                if (col.key === "acoes") {
                    $row.append(`<td data-column="acoes">${buildActions(item)}</td>`);
                } else if (col.key === "custo_modular") {
                    $row.append(`<td data-column="custo_modular">${formatarMoeda(item.custo_modular)}</td>`);
                } else if (col.key === "ultimo_status") {
                    $row.append(`<td data-column="ultimo_status">${badgeStatus(item.ultimo_status)}</td>`);
                } else {
                    let v = item[col.key];
                    $row.append(`<td data-column="${col.key}">${escapeHtml(v ?? "")}</td>`);
                }
            });

            $tbody.append($row);
        });

        $('[data-bs-toggle="tooltip"]').each(function () { new bootstrap.Tooltip(this); });
    }

    function buildActions(item) {
        const p = item._permissoes || {};
        const id = item.id_estudo;
        let html = `<div class="d-flex align-items-center gap-1">`;
        html += `<textarea class="form-control form-control-sm" rows="1" style="min-width:140px;"
                    id="comentario-${id}" placeholder="Comentário..."></textarea>`;
        if (p.aprovar) {
            html += `<button class="btn btn-success btn-sm" title="Aprovar" data-acao="aprovar" data-id="${id}">
                        <i class="bi bi-hand-thumbs-up"></i></button>`;
            html += `<button class="btn btn-danger btn-sm" title="Reprovar" data-acao="reprovar" data-id="${id}">
                        <i class="bi bi-hand-thumbs-down"></i></button>`;
        }
        if (p.visualizar) {
            html += `<button class="btn btn-info btn-sm" title="Ver detalhes" data-acao="detalhes" data-id="${id}">
                        <i class="bi bi-eye"></i></button>`;
        }
        html += `</div>`;
        return html;
    }

    function renderPagination(resp) {
        const $p = $("#pagination").empty();
        const add = (label, page, disabled, active) => {
            $p.append(`<li class="page-item ${disabled ? "disabled" : ""} ${active ? "active" : ""}">
                <a class="page-link" href="#" data-page="${page}">${label}</a></li>`);
        };
        add("Anterior", resp.page - 1, resp.page === 1, false);
        add(resp.page, resp.page, false, true);
        add("Próximo", resp.page + 1, !resp.has_next, false);

        $("#pagination a").on("click", function (e) {
            e.preventDefault();
            const $li = $(this).closest("li");
            if ($li.hasClass("disabled") || $li.hasClass("active")) return;
            const np = parseInt($(this).data("page"));
            if (!isNaN(np)) { state.page = np; load(); }
        });
    }

    function updateInfo(resp) {
        const qtd = resp.items.length;
        const start = qtd ? ((resp.page - 1) * resp.per_page) + 1 : 0;
        const end = ((resp.page - 1) * resp.per_page) + qtd;
        $("#startRecord").text(start);
        $("#endRecord").text(end);
        $("#totalRecords").text(`Página ${resp.page}`);
    }

    // ===================== Seletor de colunas =====================
    function renderColumnDropdown() {
        const $c = $("#columnDropdown").empty();
        COLUMNS.forEach(col => {
            $c.append(`
                <div class="form-check">
                    <input class="form-check-input column-toggle" type="checkbox"
                           value="${col.key}" id="col-${col.key}" ${col.visible ? "checked" : ""}>
                    <label class="form-check-label" for="col-${col.key}">${col.label}</label>
                </div>`);
        });
        $c.append(`<hr>
            <button class="btn btn-sm btn-outline-primary me-2" id="btnSelectAll">Todas</button>
            <button class="btn btn-sm btn-outline-secondary" id="btnSelectNone">Nenhuma</button>`);
    }

    // ===================== Eventos do cabeçalho =====================
    function bindHeaderEvents() {
        $(".filter-input").off("input").on("input", debounce(function () {
            const col = $(this).data("filter");
            const value = $(this).val().trim();
            if (value) state.columnFilters[col] = value;
            else delete state.columnFilters[col];
            state.page = 1;
            load();
        }, 400));

        $(".sort-icon").off("click").on("click", function () {
            const col = $(this).data("sort");
            state.direction = (state.sort === col && state.direction === "desc") ? "asc" : "desc";
            state.sort = col;
            state.page = 1;
            renderHeader();
            load();
        });

        setupColumnResizing();
    }

    // Redimensionamento de colunas arrastando o `.resize-handle` (igual ao listar).
    function setupColumnResizing() {
        let isResizing = false;
        let currentColumn = null;
        let startX = 0;
        let startWidth = 0;
        let colIndex = 0;

        function handleResize(e) {
            if (!isResizing) return;
            const newWidth = startWidth + (e.clientX - startX);
            if (newWidth < 60) return;
            const css = { width: newWidth + "px", minWidth: newWidth + "px", maxWidth: newWidth + "px" };
            currentColumn.css(css);
            $("#filterRow th").eq(colIndex).css(css);
            $("#tableBody tr").each(function () {
                $(this).find("td").eq(colIndex).css(css);
            });
        }

        function stopResize() {
            isResizing = false;
            $(document).off(".columnResize");
        }

        $(".resize-handle").off("mousedown").on("mousedown", function (e) {
            e.preventDefault();
            e.stopPropagation();
            isResizing = true;
            currentColumn = $(this).closest("th");
            colIndex = currentColumn.index();
            startX = e.clientX;
            startWidth = currentColumn.outerWidth();
            $(document).on("mousemove.columnResize", handleResize);
            $(document).on("mouseup.columnResize", stopResize);
        });
    }

    // ===================== Ações de aprovação =====================
    function enviarAcao(id, status) {
        const comentario = $(`#comentario-${id}`).val() || "";
        $.ajax({
            url: `/gestao/aprovacao/${id}/status`,
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({ status, comentario }),
            success: function (res) {
                // O backend grava o StatusTipo com o mesmo nome enviado
                // ("Aprovado"/"Reprovado"), que passa a ser o último status.
                $(`#estudo-${id} [data-column="ultimo_status"]`).html(badgeStatus(status));
                $(`#comentario-${id}`).val("");
                showToast(res.message || `Projeto ${status.toLowerCase()} com sucesso!`, "success");
                loadChart();
            },
            error: function (xhr) {
                const msg = (xhr.responseJSON && xhr.responseJSON.message) || "Erro ao enviar ação.";
                showToast(msg, "error");
            },
        });
    }

    // ===================== Exportação =====================
    async function exportData(format) {
        const params = new URLSearchParams({
            search: state.search,
            sort: state.sort,
            direction: state.direction,
            filters: JSON.stringify(state.columnFilters),
            columns: visibleKeys().join(","),
            min_valor: state.minValor,
            export: format,
            per_page: 999999,
            page: 1,
        });
        const resp = await fetch(`/gestao/api/aprovacao?${params.toString()}`);
        if (!resp.ok) { showToast("Erro ao gerar arquivo de exportação.", "error"); return; }
        const blob = await resp.blob();
        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = `aprovacao_export.${format}`;
        link.click();
    }

    // ===================== Init =====================
    $(document).ready(function () {
        renderColumnDropdown();
        renderHeader();
        loadChart();
        load();

        // Busca global
        $("#globalSearch").on("input", debounce(function () {
            state.search = $(this).val().trim();
            state.page = 1;
            load();
        }, 400));

        // Custo mínimo
        $("#btnFiltrarValor").on("click", function () {
            state.minValor = parseFloat($("#valorFiltro").val()) || 0;
            state.page = 1;
            load();
            loadChart();
        });
        $("#valorFiltro").on("keypress", function (e) {
            if (e.which === 13) $("#btnFiltrarValor").click();
        });

        // Registros por página
        $("#pageSize").on("change", function () {
            state.perPage = parseInt($(this).val());
            state.page = 1;
            load();
        });

        // Limpar filtros
        $("#btnClearFilters").on("click", function () {
            state.columnFilters = {};
            state.search = "";
            $("#globalSearch").val("");
            $(".filter-input").val("");
            state.page = 1;
            load();
        });

        // Seletor de colunas
        $("#btnColumnSelector").on("click", e => { e.stopPropagation(); $("#columnDropdown").toggle(); });
        // Ao ligar/desligar coluna, recarrega do servidor: a API só retorna
        // as colunas selecionadas, então uma coluna recém-ligada viria vazia
        // se renderizássemos apenas o cache local.
        $("#columnDropdown").on("change", ".column-toggle", function () {
            const col = COLUMNS.find(c => c.key === $(this).val());
            if (col) col.visible = $(this).is(":checked");
            renderHeader();
            load();
        });
        $("#columnDropdown").on("click", "#btnSelectAll", () => {
            COLUMNS.forEach(c => c.visible = true);
            renderColumnDropdown(); renderHeader(); load();
        });
        $("#columnDropdown").on("click", "#btnSelectNone", () => {
            COLUMNS.forEach(c => c.visible = (c.key === "acoes"));
            renderColumnDropdown(); renderHeader(); load();
        });

        // Botão Atualizar
        $("#btnAtualizar").on("click", function () { load(); loadChart(); });

        // Exportar
        $("#btnExport").on("click", e => { e.stopPropagation(); $("#exportMenu").toggle(); });
        $("#exportMenu").on("click", "a[data-export]", function (e) {
            e.preventDefault();
            exportData($(this).data("export"));
            $("#exportMenu").hide();
        });

        // Fechar dropdowns ao clicar fora
        $(document).on("click", function (e) {
            if (!$(e.target).closest(".column-selector").length) $("#columnDropdown").hide();
            if (!$(e.target).closest(".export-dropdown").length) $("#exportMenu").hide();
        });

        // Ações por linha (delegado, pois as linhas são dinâmicas)
        $("#tableBody").on("click", "button[data-acao]", function () {
            const id = $(this).data("id");
            const acao = $(this).data("acao");
            if (acao === "aprovar") enviarAcao(id, "Aprovado");
            else if (acao === "reprovar") enviarAcao(id, "Reprovado");
            else if (acao === "detalhes" && window.verDetalhes) window.verDetalhes(id);
        });
    });

})();
