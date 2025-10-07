    // Estado global da aplicação
    let currentData = [];
    let filteredData = [];
    let currentPage = 1;
    let pageSize = 25;
    let sortColumn = '';
    let sortDirection = 'asc';
    let columnFilters = {};
    let idEstudo = null;

    // NOVAS VARIÁVEIS GLOBAIS PARA AS DEFINIÇÕES DE COLUNAS E AÇÕES
    let allColumnDefinitions = [];  // Armazenará as definições de colunas do HTML
    let allActionDefinitions = [];  // Armazenará as definições de ações do HTML

    // Inicialização - ALTERADO
    $(document).ready(function() {

        initializeData();
        setupEventListeners();
        setupColumnResizing();
        initializeTooltips();
        status_event_listeners();
        loadTableSettings();  // Carregar as configurações salvas
    });

    // Inicializar dados - ALTERADO
    function initializeData() {
        const table = $('#estudosTable');
        const rawItems = table.data('itens');  // Pega os itens diretamente do JSON
        const rawColumns = table.data('colunas');  // Pega as definições de colunas do JSON
        const rawActions = table.data('acoes');  // Pega as definições de ações do JSON

        //console.log('Colunas:', { rawColumns });
        //console.log('Ações:', { rawActions });

        // Preenche as variáveis globais
        allColumnDefinitions = rawColumns.concat([{ value: 'acoes', nome: 'Ações', visivel: true}])
        allActionDefinitions = rawActions || [];

        currentData = rawItems;  // currentData agora é o array de objetos completo
        filteredData = [...currentData];

        // Aplica a visibiidade inicial das colunas e as configurações salvas
        applyInitialColumnVisibility(rawColumns);  // Nova função para aplicar visibilidade inicial
        updatePagination();
        renderTable();
    }

    // Função para aplicar a visibilidade inicial das colunas (chamada uma vez na inicialização)
    function applyInitialColumnVisibility(rawColumns){
        rawColumns.forEach(colDef => {
            const $checkbox = $(`#col-${colDef.value}`);
            if ($checkbox.length) {
                $checkbox.prop('checked', colDef.visivel);
                // Chama toggleColumn para aplicar a visibilidade no DOM
                toggleColumn({ target: $checkbox[0] });
            }
        });

        // Garante que a coluna de ações esteja visível por padrão
        $('#col-acoes').prop('checked', true);
        $(`[data-column="acoes"]`).show();
    }

    // Configurar event listeners - NÃO MUDA
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

    // Debounce function - NÃO MUDA
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

    // Busca global - NÃO MUDA
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

    // Filtros por coluna - NÃO MUDA, VERIFICAR data_registro
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
                // Tratamento para propriedades aninhadas (ex: empresa.nome)
                let itemValue;
                if (col.includes('.')) {
                    const parts = col.split('.');
                    let current = item;
                    for (const part of parts) {
                        current = current ? current[part] : undefined;
                    }
                    itemValue = current !== undefined ? String(current) : '';
                } else {
                    itemValue = String(item[col] !== undefined ? item[col] : '');
                }

                if (col == 'data_registro' && filter) {
                    const itemDate = new Date(itemValue).toISOString().split('T')[0];
                    if (itemDate !== filter) return false;
                } else {
                    if (!itemValue.toLowerCase().includes(filter)) return false;
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
       console.log('Sort column:', column);
       console.log('Event target:', event.target);
       console.log('Data sort attribute:', $(event.target).attr('data-sort'));

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
            let aVal, bVal;

            // Função auxiliar para obter valor de propriedade aninhada
            const getNestedValue = (obj, path) => {
                return path.split('.').reduce((acc, part) => acc && acc[part], obj);
            };

            if (column.includes('.')){
                aVal = getNestedValue(a, column);
                bVal = getNestedValue(b, column);
            } else {
                aVal = a[column];
                bVal = b[column];
            }

            // Tratamento especial para números 
            if (column === 'id' || typeof aVal === 'number') { // Pode ser necessário refinar a detecção de números
                aVal = parseFloat(aVal);
                bVal = parseFloat(bVal);
            }

            // Tratamento especial para datas
            if (column === 'data_registro' || (typeof aVal === 'string' && !isNaN(new Date(aVal)))) { // Detecta strings que podem ser datas
                aVal = new Date(aVal);
                bVal = new Date(bVal);
            }

            if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });

        renderTable();
    }

    // function handleSort(event) {
    // // event.currentTarget é o elemento ao qual o event listener foi anexado (neste caso, o .sortable-header)
    // const $sortableElement = $(event.currentTarget); 
    // const column = $sortableElement.data('sort');

    // console.log('Coluna para ordenação:', column); // Verifique no console se o valor está correto

    // if (!column) {
    //     console.log('Erro: Atributo data-sort não encontrado no elemento clicado.');
    //     return; // Sai da função se não encontrar a coluna
    // }

    // if (sortColumn === column) {
    //     sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    // } else {
    //     sortColumn = column;
    //     sortDirection = 'asc';
    // }

    // // 1. Resetar todos os ícones de ordenação para o estado padrão
    // $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');

    // // 2. Encontrar o ícone específico dentro do cabeçalho clicado e atualizá-lo
    // const $currentSortIcon = $sortableElement.find('i.sort-icon');
    // if ($currentSortIcon.length) {
    //     $currentSortIcon.removeClass('fa-sort').addClass(`fa-sort-${sortDirection === 'asc' ? 'up' : 'down'}`);
    // } else {
    //     console.log('Erro: Ícone de ordenação não encontrado dentro do cabeçalho da coluna:', column);
    // }

    // // Ordenar dados (seu código existente)
    // filteredData.sort((a, b) => {
    //     let aVal, bVal;
    //     const getNestedValue = (obj, path) => {
    //         return path.split('.').reduce((acc, part) => acc && acc[part], obj);
    //     };

    //     if (column.includes('.')){
    //         aVal = getNestedValue(a, column);
    //         bVal = getNestedValue(b, column);
    //     } else {
    //         aVal = a[column];
    //         bVal = b[column];
    //     }

    //     // Tratamento para valores undefined/null
    //     aVal = aVal === undefined || aVal === null ? '' : aVal;
    //     bVal = bVal === undefined || bVal === null ? '' : bVal;

    //     // Tratamento especial para números 
    //     if (column === 'id' || (!isNaN(parseFloat(aVal)) && isFinite(aVal) && !isNaN(parseFloat(bVal)) && isFinite(bVal))) {
    //         aVal = parseFloat(aVal);
    //         bVal = parseFloat(bVal);
    //     }
    //     // Tratamento especial para datas
    //     if (column === 'data_registro' || (typeof aVal === 'string' && !isNaN(new Date(aVal)) && typeof bVal === 'string' && !isNaN(new Date(bVal)))) {
    //         aVal = new Date(aVal);
    //         bVal = new Date(bVal);
    //     }

    //     // Comparação de strings case-insensitive
    //     if (typeof aVal === 'string' && typeof bVal === 'string') {
    //         aVal = aVal.toLowerCase();
    //         bVal = bVal.toLowerCase();
    //     }

    //     if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    //     if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    //     return 0;
    // });
    
    // currentPage = 1; // Resetar para a primeira página após a ordenação
    // updatePagination();
    // renderTable();
    // }

    // Mudança do tamanho da página - NÃO MUDA
    function changePageSize() {
        pageSize = parseInt($('#pageSize').val());
        currentPage = 1;
        updatePagination();
        renderTable();
    }

    // Renderizar tabela - AGORA É DINÂMICA
    function renderTable() {
        showLoading();
        setTimeout(() => {
            const $tbody = $('#tableBody');
            const start = (currentPage - 1) * pageSize;
            const end = start + pageSize;
            const pageData = filteredData.slice(start, end);

            $tbody.empty(); // Limpa o corpo da tabela

            pageData.forEach(item => {
                let rowHtml = '';
                allColumnDefinitions.forEach(colDef => {
                    const colValue = colDef.value;
                    let cellContent = '';

                    if (colValue === 'acoes') {
                        // Constrói os botões de ação dinamicamente
                        let actionButtonsHtml = '<div class="btn-group" role="group">';
                        allActionDefinitions.forEach(action => {
                            // Assumindo que 'item.id' é o identificador único para as ações
                            const itemId = item.id; // Ou outro identificador, dependendo da sua estrutura de dados

                            // Verifica se a ação tem uma função JS para chamar (ex: verDetalhes)
                            if (action.js_function) {
                                actionButtonsHtml += `
                                    <button class="btn btn-sm btn-${action.type === 'view' ? 'info' : (action.type === 'edit' ? 'warning' : 'primary')}"
                                            onclick="${action.js_function}(${itemId})"
                                            data-bs-toggle="tooltip" title="${action.tooltip || ''}">
                                        <i class="${action.icon}"></i>
                                    </button>
                                `;
                            } else if (action.url_prefix) {
                                // Se tiver um prefixo de URL, constrói o link
                                const actionUrl = `${action.url_prefix}${itemId}`;
                                actionButtonsHtml += `
                                    <a href="${actionUrl}"
                                       class="btn btn-sm btn-${action.type === 'edit' ? 'warning' : (action.type === 'manage_alternatives' ? 'success' : 'primary')}"
                                       data-bs-toggle="tooltip" title="${action.tooltip || ''}">
                                        <i class="${action.icon}"></i>
                                    </a>
                                `;
                            }
                            // Adicione outras lógicas para diferentes tipos de ações se necessário
                        });
                        actionButtonsHtml += '</div>';
                        cellContent = actionButtonsHtml;

                    } else {
                        // Pega o valor da propriedade do item, tratando propriedades aninhadas
                        if (colValue.includes('.')) {
                            const parts = colValue.split('.');
                            let current = item;
                            for (const part of parts) {
                                current = current ? current[part] : undefined;
                            }
                            cellContent = current !== undefined ? current : '';
                        } else {
                            cellContent = item[colValue] !== undefined ? item[colValue] : '';
                        }
                    }
                    rowHtml += `<td data-column="${colValue}">${cellContent}</td>`;
                });
                const row = $('<tr>').html(rowHtml);
                $tbody.append(row);
            });

            // Aplica a visibilidade das colunas (já existente)
            applyColumnVisibility();
            // Reativar tooltips para os novos elementos
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
            'Data Criação': item.data_registro
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

    // clearAllFilters - precisa ser ajustado para limpar os filtros de coluna dinamicamente
    function clearAllFilters() {
        $('#globalSearch').val('');
        $('.filter-input').val(''); // Limpa todos os inputs de filtro
        columnFilters = {}; // Reseta o objeto de filtros
        filteredData = [...currentData];
        currentPage = 1;
        sortColumn = '';
        sortDirection = 'asc';
        $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');
        updatePagination();
        renderTable();
    }

    function refreshData() {
        showLoading();
        setTimeout(() => {
            // Em uma aplicação real, você faria uma nova requisição AJAX aqui:
            // $.get('/api/estudos').done(function(newData) {
            //     currentData = newData; // Atualiza com os novos dados
            //     filteredData = [...currentData]; // Reseta filtros
            //     currentPage = 1;
            //     updatePagination();
            //     renderTable();
            //     hideLoading();
            //     showNotification('Dados atualizados com sucesso!', 'success');
            // }).fail(function() {
            //     hideLoading();
            //     showNotification('Erro ao atualizar dados.', 'danger');
            // });

            // Como o código acima está comentado, ele apenas simula o sucesso:
            hideLoading();
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
                new bootstrap.Tooltip(this);
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
                                    <p><strong>Tipo Viabilidade:</strong> ${data.tipo_pedido?.viabilidade || 'N/A'}</p>
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
                                    <i class="fas fa-chart-bar me-2"></i>Demandas
                                </div>
                                <div class="card-body">
                                    <p><strong>Demanda FP:</strong> ${data.dem_carga_solicit_fp || 'N/A'}</p>
                                    <p><strong>Demanda P:</strong> ${data.dem_carga_solicit_p || 'N/A'}</p>
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
                                            ${data.anexos.map(a => `<li class="list-group-item">${a.nome_arquivo || 'N/A'} (${a.tipo_mime || 'N/A'})</li>`).join('')}
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
        console.log(idEstudo)
        $('#status_id_estudo').val(idEstudo);

        carregarHistorico(idEstudo);
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
              <button class="btn btn-sm btn-warning btn-editar" data-status='${JSON.stringify(status)}'>Editar</button>
              <button class="btn btn-sm btn-danger btn-excluir" data-status='${status.id_status}'>Excluir</button>
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



