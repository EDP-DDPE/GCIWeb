    // Estado global da aplicação
    let currentData = [];
    let filteredData = [];
    let currentPage = 1;
    let pageSize = 25;
    let sortColumn = '';
    let sortDirection = 'asc';
    let columnFilters = {};
    let idEstudo = null;

    // Inicialização
    $(document).ready(function() {

        $('#id_status_tipo').select2({
            dropdownParent: $('#statusModal'),
            theme: 'bootstrap-5',
            placeholder: 'Selecione uma opção...',
            allowClear: false
        });

        initializeData();
        setupEventListeners();
        setupColumnResizing();
        initializeTooltips();
        status_event_listeners();


    });

    // Inicializar dados
    function initializeData() {
        const tableRows = $('#tableBody tr');
        currentData = tableRows.map(function() {
            const cells = $(this).find('td');
            return {
                id: cells.eq(0).text().trim(),
                num_doc: cells.eq(1).text().trim(),
                nome_projeto: cells.eq(2).text().trim(),
                empresa: cells.eq(3).text().trim(),
                municipio: cells.eq(4).text().trim(),
                eng_responsavel: cells.eq(5).text().trim(),
                data_registro: cells.eq(6).text().trim(),
                qtd_alternativas: cells.eq(7).text().trim(),
                qtd_anexos: cells.eq(8).text().trim(),
                status: cells.eq(9).text().trim(),
                acoes: cells.eq(10).html(),
                element: this
            };
        }).get();

        filteredData = [...currentData];
        updatePagination();
        renderTable();
    }

    // Configurar event listeners
    function setupEventListeners() {
        // Busca global
        $('#globalSearch').on('input', debounce(applyGlobalSearch, 300));

        // Filtros por coluna
        $('.filter-input').on('input', debounce(applyColumnFilter, 300));

        // Tamanho da página
        $('#pageSize').on('change', changePageSize);

        // Ordenação
        $('.sort-icon').on('click', handleSort);

        // Seleção de colunas
        $('.column-toggle').on('change', toggleColumn);

        // Fechar dropdowns ao clicar fora
        $(document).on('click', closeDropdowns);
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Busca global
    function applyGlobalSearch() {
        const searchTerm = $('#globalSearch').val().toLowerCase();

        if (!searchTerm) {
            filteredData = [...currentData];
        } else {
            filteredData = currentData.filter(item =>
                Object.values(item).some(value =>
                    String(value).toLowerCase().includes(searchTerm)
                )
            );
        }

        currentPage = 1;
        updatePagination();
        renderTable();
    }

    // Filtros por coluna
    function applyColumnFilter(event) {
        const column = $(event.target).data('filter');
        const value = $(event.target).val().toLowerCase();

        if (value === '') {
            delete columnFilters[column];
        } else {
            columnFilters[column] = value;
        }

        // Aplicar todos os filtros
        filteredData = currentData.filter(item => {
            for (let [col, filter] of Object.entries(columnFilters)) {
                if (col === 'data_registro' && filter) {
                    // Para datas, comparar apenas a parte da data
                    const itemDate = new Date(item[col]).toISOString().split('T')[0];
                    if (itemDate !== filter) return false;
                } else {
                    if (!String(item[col]).toLowerCase().includes(filter)) return false;
                }
            }
            return true;
        });

        currentPage = 1;
        updatePagination();
        renderTable();
    }

    // Ordenação
    function handleSort(event) {
        const column = $(event.target).data('sort');

        if (sortColumn === column) {
            sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            sortColumn = column;
            sortDirection = 'asc';
        }

        // Atualizar ícones de ordenação
        $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');

        $(event.target).removeClass('fa-sort').addClass(`fa-sort-${sortDirection === 'asc' ? 'up' : 'down'}`);

        // Ordenar dados
        filteredData.sort((a, b) => {
            let aVal = a[column];
            let bVal = b[column];

            // Tratamento especial para números
            if (column === 'id') {
                aVal = parseInt(aVal);
                bVal = parseInt(bVal);
            }

            // Tratamento especial para datas
            if (column === 'data_registro') {
                aVal = new Date(aVal);
                bVal = new Date(bVal);
            }

            if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        renderTable();
    }

    // Mudança do tamanho da página
    function changePageSize() {
        pageSize = parseInt($('#pageSize').val());
        currentPage = 1;
        updatePagination();
        renderTable();
    }

    // Renderizar tabela
    function renderTable() {
        showLoading();

        setTimeout(() => {
            const $tbody = $('#tableBody');
            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            const pageData = filteredData.slice(start, end);

            $tbody.empty();

            pageData.forEach(item => {
                const row = $('<tr>').html(`
                    <td data-column="id">${item.id}</td>
                    <td data-column="num_doc">${item.num_doc}</td>
                    <td data-column="nome_projeto">${item.nome_projeto}</td>
                    <td data-column="empresa">${item.empresa}</td>
                    <td data-column="municipio">${item.municipio}</td>
                    <td data-column="eng_responsavel">${item.eng_responsavel}</td>
                    <td data-column="data_registro">${item.data_registro}</td>
                    <td data-column="qtd_alternativas">${item.qtd_alternativas}</td>
                    <td data-column="qtd_anexos">${item.qtd_anexos}</td>
                    <td data-column="status">${item.status}</td>
                    <td data-column="acoes">${item.acoes}</td>
                `);
                $tbody.append(row);
            });

            // Aplicar visibilidade das colunas
            applyColumnVisibility();

            // Reativar tooltips
            initializeTooltips();

            hideLoading();
        }, 200);
    }

    // Atualizar paginação
    function updatePagination() {
        const totalRecords = filteredData.length;
        const totalPages = Math.ceil(totalRecords / pageSize);
        const start = Math.min((currentPage - 1) * pageSize + 1, totalRecords);
        const end = Math.min(currentPage * pageSize, totalRecords);

        // Atualizar informações
        $('#startRecord').text(totalRecords > 0 ? start : 0);
        $('#endRecord').text(end);
        $('#totalRecords').text(totalRecords);

        // Mostrar informação de filtro se necessário
        const $filteredInfo = $('#filteredInfo');
        const $originalTotal = $('#originalTotal');
        if (totalRecords < currentData.length) {
            $originalTotal.text(currentData.length);
            $filteredInfo.show();
        } else {
            $filteredInfo.hide();
        }

        // Gerar paginação
        const $pagination = $('#pagination');
        $pagination.empty();

        if (totalPages <= 1) return;

        // Botão anterior
        const $prevLi = $('<li>').addClass(`page-item ${currentPage === 1 ? 'disabled' : ''}`)
            .html(`<a class="page-link" href="#" onclick="changePage(${currentPage - 1})">Anterior</a>`);
        $pagination.append($prevLi);

        // Páginas
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const $li = $('<li>').addClass(`page-item ${i === currentPage ? 'active' : ''}`)
                .html(`<a class="page-link" href="#" onclick="changePage(${i})">${i}</a>`);
            $pagination.append($li);
        }

        // Botão próximo
        const $nextLi = $('<li>').addClass(`page-item ${currentPage === totalPages ? 'disabled' : ''}`)
            .html(`<a class="page-link" href="#" onclick="changePage(${currentPage + 1})">Próximo</a>`);
        $pagination.append($nextLi);
    }

    // Mudar página
    function changePage(page) {
        if (page < 1 || page > Math.ceil(filteredData.length / pageSize)) return;
        currentPage = page;
        renderTable();
        updatePagination();
    }

    // Seleção de colunas
    function toggleColumnSelector() {
        $('#columnDropdown').toggle();
    }

    function toggleColumn(event) {
        const column = $(event.target).val();
        const isVisible = $(event.target).is(':checked');

        $(`[data-column="${column}"]`).toggle(isVisible);
    }

    function selectAllColumns() {
        $('.column-toggle').each(function() {
            $(this).prop('checked', true);
            const column = $(this).val();
            $(`[data-column="${column}"]`).show();
        });
    }

    function deselectAllColumns() {
        $('.column-toggle').each(function() {
            if ($(this).val() !== 'acoes') { // Manter sempre ações visíveis
                $(this).prop('checked', false);
                const column = $(this).val();
                $(`[data-column="${column}"]`).hide();
            }
        });
    }

    function applyColumnVisibility() {
        $('.column-toggle').each(function() {
            const column = $(this).val();
            const isVisible = $(this).is(':checked');
            $(`[data-column="${column}"]`).toggle(isVisible);
        });
    }

    // Redimensionamento de colunas
    function setupColumnResizing() {
        const $table = $('#estudosTable');
        let isResizing = false;
        let currentColumn = null;
        let startX = 0;
        let startWidth = 0;

        $('.resize-handle').on('mousedown', function(e) {
            e.preventDefault();
            isResizing = true;
            currentColumn = $(this).closest('th');
            startX = e.clientX;
            startWidth = parseInt(currentColumn.css('width'), 10);

            $(document).on('mousemove', handleResize);
            $(document).on('mouseup', stopResize);

            // Adicionar classe para cursor
            $('body').css('cursor', 'col-resize');
            $table.css('user-select', 'none');
        });

        function handleResize(e) {
            if (!isResizing) return;

            const width = startWidth + e.clientX - startX;
            if (width > 50) { // Largura mínima
                currentColumn.css({
                    'width': width + 'px',
                    'min-width': width + 'px'
                });
            }
        }

        function stopResize() {
            isResizing = false;
            currentColumn = null;
            $('body').css('cursor', '');
            $table.css('user-select', '');

            $(document).off('mousemove', handleResize);
            $(document).off('mouseup', stopResize);
        }
    }

    // Exportação de dados
    function toggleExportMenu() {
        $('#exportMenu').toggle();
    }

    function exportData(format) {
        const exportData = filteredData.map(item => ({
            ID: item.id,
            'Nº Documento': item.num_doc,
            'Projeto': item.nome_projeto,
            'Empresa': item.empresa,
            'Município': item.municipio,
            'Responsável': item.eng_responsavel,
            'Data Criação': item.data_registro,
            'Nº Alternativas': item.qtd_alternativas,
            'Nº Anexos': item.qtd_anexos,
            'Status': item.status
        }));

        switch(format) {
            case 'csv':
                exportToCSV(exportData);
                break;
            case 'excel':
                exportToExcel(exportData);
                break;
            case 'pdf':
                exportToPDF(exportData);
                break;
        }

        $('#exportMenu').hide();
    }

    function exportToCSV(data) {
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(header => `"${row[header]}"`).join(','))
        ].join('\n');

        downloadFile(csv, 'estudos.csv', 'text/csv');
    }

    function exportToExcel(data) {
        // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
        const csv = exportToCSV(data);
        downloadFile(csv, 'estudos.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    }

    function exportToPDF(data) {
        // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
        let content = 'LISTA DE ESTUDOS\n\n';

        const headers = Object.keys(data[0]);
        content += headers.join('\t') + '\n';
        content += '='.repeat(100) + '\n';

        data.forEach(row => {
            content += headers.map(header => row[header]).join('\t') + '\n';
        });

        downloadFile(content, 'estudos.pdf', 'application/pdf');
    }

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = $('<a>').attr({
            href: url,
            download: filename
        })[0];

        $('body').append(link);
        link.click();
        $(link).remove();
        URL.revokeObjectURL(url);
    }

    // Utilitários
    function showLoading() {
        $('#loadingOverlay').show();
    }

    function hideLoading() {
        $('#loadingOverlay').hide();
    }

    function clearAllFilters() {
        // Limpar busca global
        $('#globalSearch').val('');

        // Limpar filtros por coluna
        $('.filter-input').val('');

        // Resetar dados
        columnFilters = {};
        filteredData = [...currentData];
        currentPage = 1;

        // Resetar ordenação
        sortColumn = '';
        sortDirection = 'asc';
        $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');

        updatePagination();
        renderTable();
    }

    function refreshData() {
        showLoading();

        // Simular reload dos dados (em uma aplicação real, faria uma nova requisição)
        setTimeout(() => {
            // Aqui você faria uma nova requisição para buscar dados atualizados
             $.get('/listar').done(function(data) {
                const tempDOM = $('<div>').html(data);
                const newRows = tempDOM.find('#tableBody > tr');

                if (newRows.length > 0) {
                    // Substitui o conteúdo do tbody atual
                    const $tbody = $('#tableBody');
                    $tbody.empty().append(newRows);

                    initializeData();
                    initializeTooltips();
                }

             });

            hideLoading();

            // Mostrar notificação de sucesso
            showNotification('Dados atualizados com sucesso!', 'success');
        }, 1000);
    }

    function showNotification(message, type = 'info') {
        // Criar elemento de notificação
        const $notification = $('<div>').addClass(`alert alert-${type} alert-dismissible fade show position-fixed`)
            .css({
                'top': '20px',
                'right': '20px',
                'z-index': '9999',
                'min-width': '300px'
            })
            .html(`
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `);

        $('body').append($notification);

        // Auto remover após 3 segundos
        setTimeout(() => {
            $notification.remove();
        }, 3000);
    }

    function closeDropdowns(event) {
        if (!$(event.target).closest('.column-selector').length) {
            $('#columnDropdown').hide();
        }
        if (!$(event.target).closest('.export-dropdown').length) {
            $('#exportMenu').hide();
        }
    }

    function initializeTooltips() {
        // Inicializar tooltips do Bootstrap se disponível
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            $('[data-bs-toggle="tooltip"]').each(function() {
                new bootstrap.Tooltip(this, { container: 'body' });
            });
        }
    }
    // Função original para detalhes (mantida)
    function verDetalhes(estudoId) {
        const $modalBody = $('#modalDetalhesBody');
        $modalBody.html(`
            <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `);

        const modal = new bootstrap.Modal($('#modalDetalhes')[0]);
        modal.show();

        $.get(`/api/estudos/${estudoId}`)
            .done(function(data) {
                if (data.error) {
                    $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                    return;
                }

                const detalhesHtml = `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-info-circle me-2"></i>Informações Básicas
                                </div>
                                <div class="card-body">
                                    <p><strong>Protocolo:</strong> ${data.protocolo || 'N/A'}</p>
                                    <p><strong>Nº Documento:</strong> ${data.num_doc || 'N/A'}</p>
                                    <p><strong>Projeto:</strong> ${data.nome_projeto || 'N/A'}</p>
                                    <p><strong>Descrição:</strong> ${data.descricao || 'N/A'}</p>
                                    <p><strong>Cliente:</strong> ${data.empresa?.nome || 'N/A'}</p>
                                    <p><strong>CNPJ:</strong> ${data.empresa?.cnpj || 'N/A'}</p>
                                    <p><strong>Município:</strong> ${data.municipio?.nome || 'N/A'}</p>
                                    <p><strong>Regional:</strong> ${data.regional?.nome || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-cogs me-2"></i>Detalhes Técnicos
                                </div>
                                <div class="card-body">
                                    <p><strong>Viabilidade:</strong> ${data.tipo_solicitacao?.viabilidade || 'N/A'}</p>
                                    <p><strong>Análise:</strong> ${data.tipo_solicitacao?.analise || 'N/A'}</p>
                                    <p><strong>Pedido:</strong> ${data.tipo_solicitacao?.pedido || 'N/A'}</p>
                                    <p><strong>Criado por:</strong> ${data.criado_por?.nome || 'N/A'}</p>
                                    <p><strong>Responsável Região:</strong> ${data.responsavel_regiao?.usuario?.nome || 'N/A'}</p>
                                    <p><strong>Data Registro:</strong> ${data.data_registro || 'N/A'}</p>
                                    <p><strong>Latitude:</strong> ${data.latitude_cliente || 'N/A'}</p>
                                    <p><strong>Longitude:</strong> ${data.longitude_cliente || 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-chart-bar me-2"></i>Demandas (kW)
                                </div>
                                <div class="card-body">
                                    <div class='row'>
                                        <div class="col-md-6">
                                            <p><strong>Demanda Atual Carga FP:</strong> ${data.dem_carga_atual_fp || 'N/A'}</p>
                                            <p><strong>Demanda Atual Carga P:</strong> ${data.dem_carga_atual_p || 'N/A'}</p>
                                            <p><strong>Demanda Atual Geração FP:</strong> ${data.dem_ger_atual_fp || 'N/A'}</p>
                                            <p><strong>Demanda Atual Geração P:</strong> ${data.dem_ger_atual_p || 'N/A'}</p>
                                        </div>
                                        <div class="col-md-6">
                                            <p><strong>Demanda Solicitada Carga FP:</strong> ${data.dem_carga_solicit_fp || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Carga P:</strong> ${data.dem_carga_solicit_p || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Geração FP:</strong> ${data.dem_ger_solicit_fp || 'N/A'}</p>
                                            <p><strong>Demanda Solicitada Geração P:</strong> ${data.dem_ger_solicit_p || 'N/A'}</p>
                                        </div>
                                    </row>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="bi bi-list-check"></i>Alternativas
                                </div>
                                <div class="card-body">
                                     ${data.alternativas && data.alternativas.length > 0 ? `
                                        <div class="table-responsive">
                                            <table class="table table-striped table-sm align-middle mb-0">
                                                <thead class="table-light">
                                                    <tr>
                                                        <th>Alternativa</th>
                                                        <th>Descrição</th>
                                                        <th>Custo Modular (R$)</th>
                                                        <th>Circuito</th>
                                                        <th>Tensão</th>
                                                        <th>Escolhida?</th>
                                                        <th>Imagem</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${data.alternativas.map(a => `
                                                        <tr>
                                                            <td>${a.letra_alternativa || '-'}</td>
                                                            <td>${a.descricao || '-'}</td>
                                                            <td>${a.custo_modular?.toLocaleString('pt-BR', {minimumFractionDigits: 2}) || '-'}</td>
                                                            <td>${a.circuito?.nome || '-'}</td>
                                                            <td>${a.circuito?.tensao || '-'}</td>
                                                            <td>
                                                                ${a.flag_alternativa_escolhida
                                                                    ? '<span class="badge bg-success">Sim</span>'
                                                                    : '<span class="badge bg-secondary">Não</span>'
                                                                }
                                                            </td>
                                                            <td>
                                                              ${a.has_image
                                                                    ? `<button class="btn btn-sm btn-outline-primary ver-imagem-db"
                                                                                data-id="${a.id}">
                                                                            <i class="bi bi-image"></i> Ver Imagem
                                                                       </button>`
                                                                    : '<span class="text-muted">Sem imagem</span>'
                                                                }
                                                            </td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                    ` : '<p>Nenhuma alternativa cadastrada.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-file-upload me-2"></i>Anexos
                                </div>
                                <div class="card-body">

                                    ${data.anexos && data.anexos.length > 0 ? `
                                        <ul class="list-group list-group-flush">
                                            ${data.anexos.map(a => {
                                                const caminho = a.endereco.replace(/\\/g, '/'); // troca '\' por '/'
                                                return `
                                                    <li class="list-group-item  d-flex justify-content-between align-items-center">${a.nome_arquivo || 'N/A'}
                                                        <a href="/listar/download/${caminho}" class="btn btn-sm btn-outline-primary">
                                                          <i class="bi bi-download"></i> Baixar
                                                        </a>
                                                    </li>
                                                `;
                                            }).join('')}
                                        </ul>
                                    ` : '<p>Nenhum anexo.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row g-3 mt-3">
                        <div class="col-md-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-history me-2"></i>Status Histórico
                                </div>
                                <div class="card-body">
                                    ${data.status_historico && data.status_historico.length > 0 ? `
                                        <ul class="list-group list-group-flush">
                                            ${data.status_historico.map(s => `
                                                <li class="list-group-item">
                                                    <strong>${s.status || 'N/A'}</strong> - ${s.data || 'N/A'} - ${s.criado_por || 'N/A'}
                                                    ${s.observacao ? `<br><small>${s.observacao}</small>` : ''}
                                                </li>
                                            `).join('')}
                                        </ul>
                                    ` : '<p>Sem histórico de status.</p>'}
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                if (!$('#modalImagemDB').length) {
                    $('body').append(`
                        <div class="modal fade" id="modalImagemDB" tabindex="-1" aria-labelledby="modalImagemDBLabel"
                             aria-hidden="true" data-bs-backdrop="static">
                          <div class="modal-dialog modal-xl modal-dialog-centered">
                            <div class="modal-content" style="z-index: 99999 !important;">
                              <div class="modal-header bg-dark text-white">
                                <h5 class="modal-title" id="modalImagemDBLabel">
                                  <i class="bi bi-image"></i> Imagem da Alternativa
                                </h5>
                                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Fechar"></button>
                              </div>
                              <div class="modal-body text-center">
                                  <div id="loadingImg" class="my-3" style="display:none;">
                                    <div class="spinner-border text-primary" role="status">
                                      <span class="visually-hidden">Carregando...</span>
                                    </div>
                                  </div>

                                  <div id="panzoom-container" class="d-inline-block border rounded p-2 bg-light">
                                    <img id="imagemDB" src="" alt="Imagem da alternativa" class="img-fluid rounded shadow d-none" style="cursor: grab;">
                                  </div>

                                  <div class="mt-3">
                                    <button id="zoomIn" class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-zoom-in"></i></button>
                                    <button id="zoomOut" class="btn btn-sm btn-outline-primary me-2"><i class="bi bi-zoom-out"></i></button>
                                    <button id="resetZoom" class="btn btn-sm btn-outline-secondary"><i class="bi bi-arrow-repeat"></i></button>
                                  </div>
                              </div>

                            </div>
                          </div>
                        </div>
                    `);
                }

                $modalBody.html(detalhesHtml);
            })
            .fail(function(xhr, status, error) {
                console.error('Erro:', error);
                $modalBody.html(`<div class="alert alert-danger">Erro ao carregar detalhes do documento</div>`);
            });
    }

    // Funcionalidades adicionais

    // Salvar configurações no localStorage (se disponível)
    function saveTableSettings() {
        const settings = {
            pageSize: pageSize,
            columnVisibility: {}
        };

        $('.column-toggle').each(function() {
            settings.columnVisibility[$(this).val()] = $(this).is(':checked');
        });

        try {
            localStorage.setItem('estudosTableSettings', JSON.stringify(settings));
        } catch(e) {
            // localStorage não disponível
        }
    }

    function loadTableSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('estudosTableSettings') || '{}');

            if (settings.pageSize) {
                pageSize = settings.pageSize;
                $('#pageSize').val(pageSize);
            }

            if (settings.columnVisibility) {
                $.each(settings.columnVisibility, function(column, visible) {
                    const $checkbox = $(`#col-${column}`);
                    if ($checkbox.length) {
                        $checkbox.prop('checked', visible);
                        toggleColumn({ target: $checkbox[0] });
                    }
                });
            }
        } catch(e) {
            // Erro ao carregar configurações
        }
    }

    // Eventos para salvar configurações
    $('#pageSize').on('change', saveTableSettings);
    $('.column-toggle').on('change', saveTableSettings);

    // Atalhos de teclado
    $(document).on('keydown', function(e) {
        // Ctrl + F para busca global
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            $('#globalSearch').focus();
        }

        // Escape para limpar filtros
        if (e.key === 'Escape') {
            clearAllFilters();
        }

        // Ctrl + R para atualizar
        if (e.ctrlKey && e.key === 'r') {
            e.preventDefault();
            refreshData();
        }
    });

    // Adicionar indicador de registros selecionados/filtrados
    function updateFilterIndicator() {
        const hasFilters = Object.keys(columnFilters).length > 0 ||
                          $('#globalSearch').val().trim() !== '';

        let $indicator = $('.filter-indicator');
        if (!$indicator.length) {
            $indicator = $('<div>').addClass('filter-indicator badge bg-info ms-2');
            $('h2').append($indicator);
        }

        if (hasFilters) {
            $indicator.text('Filtros ativos').show();
        } else {
            $indicator.hide();
        }
    }


  // Código do modal Status
  // Quando abrir o modal

  function status_event_listeners() {
    $('#statusModal').on('show.bs.modal', function (event) {
        let button = $(event.relatedTarget);
        idEstudo = button.data('id-estudo');
        $('#status_id_estudo').val(idEstudo);

        carregarHistorico(idEstudo);
    });

    $(document).on('click', '.ver-imagem-db', function() {
        const idAlt = $(this).data('id');

        // mostra loading
        $('#imagemDB').addClass('d-none');
        $('#loadingImg').show();

        $('#modalImagemDB').modal('show');

        $.getJSON(`/api/imagem_alternativa/${idAlt}`)
            .done(function(resp) {
                if (resp.imagem) {
                    $('#imagemDB').attr('src', resp.imagem).removeClass('d-none');
                } else {
                    $('#imagemDB').replaceWith('<p class="text-danger">Sem imagem disponível.</p>');
                }
            })
            .fail(function() {
                $('#imagemDB').replaceWith('<p class="text-danger">Erro ao carregar a imagem.</p>');
            })
            .always(function() {
                $('#loadingImg').hide();
            });
    });

    $('#modalImagemDB').on('hidden.bs.modal', function () {
        $('body').addClass('modal-open'); // mantém o scroll travado do modal anterior
    });

    let panzoomInstance = null;

    $(document).on('shown.bs.modal', '#modalImagemDB', function() {
        const image = document.getElementById('imagemDB');
        const container = document.getElementById('panzoom-container');

        // Destroi instância anterior se existir
        if (panzoomInstance) {
            panzoomInstance.destroy();
        }

        // Inicializa Panzoom
        panzoomInstance = Panzoom(container, {
            contain: 'outside',
            maxScale: 8,
            minScale: 0.5,
            cursor: 'grab',
            step: 0.3,
        });

        // Zoom com scroll
        container.parentElement.addEventListener('wheel', panzoomInstance.zoomWithWheel);

        // Botões de controle
        $('#zoomIn').off('click').on('click', () => panzoomInstance.zoomIn());
        $('#zoomOut').off('click').on('click', () => panzoomInstance.zoomOut());
        $('#resetZoom').off('click').on('click', () => panzoomInstance.reset());
    });



    $(document).on('click', '.btn-editar', function () {
        let status = $(this).data('status');
        $('#status_id_status').val(status.id_status);
        $('#id_status_tipo').val(status.id_status_tipo);
        $('#observacao').val(status.observacao);
    });

    $(document).on('click', '.btn-excluir', function () {
        let status = $(this).data('status');
        excluirStatus(status)

    });

      // Submeter form (novo ou edição)
    $('#statusForm').submit(function (e) {
        e.preventDefault();

        let formData = $(this).serialize();

        $.post('/estudos/' + idEstudo + '/status/save', formData, function (res) {
          carregarHistorico(idEstudo);
          $('#statusForm')[0].reset();
          $('#status_id_status').val('');
        });
    });
  }

  // Função para carregar o histórico via AJAX
  function carregarHistorico(idEstudo) {
    $.get('/estudos/' + idEstudo + '/status', function (data) {
      let tbody = $('#status-historico-body');
      tbody.empty();

      data.forEach(status => {
        tbody.append(`
          <tr>
            <td>${status.data}</td>
            <td>${status.status_tipo}</td>
            <td>${status.observacao || ''}</td>
            <td>${status.criado_por}</td>
            <td>
             <!-- <button class="btn btn-sm btn-warning btn-editar" data-status='${JSON.stringify(status)}'>Editar</button> -->
             <!-- <button class="btn btn-sm btn-danger btn-excluir" data-status='${status.id_status}'>Excluir</button> -->
            </td>
          </tr>
        `);
      });
    });
  }

  // Editar status

  function excluirStatus(idStatus) {
      Swal.fire({
        title: 'Confirmar Exclusão',
        text: 'Tem certeza que deseja excluir este status?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
      }).then((result) => {
        if (result.isConfirmed) {
          fetch('/status/excluir/' + idStatus, {
            method: 'DELETE',
            headers: {
              'Content-Type': 'application/json',
            }
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              document.querySelector(`tr[data-status-id="${idStatus}"]`).remove();

              Swal.fire(
                'Excluído!',
                'O status foi excluído com sucesso.',
                'success'
              );
            } else {
              Swal.fire('Erro!', 'Não foi possível excluir o status.', 'error');
            }
          })
          .catch(error => {
//            console.error('Erro:', error);
            Swal.fire('Erro!', 'Ocorreu um erro ao excluir o status.', 'error');
          });
        }
      });
    }



