// Estado global da aplicação
let currentData = [];
let filteredData = [];
let currentPage = 1;
let pageSize = 25;
let sortColumn = '';
let sortDirection = 'asc';
let columnFilters = {}


// Inicialização
$(document).ready(function() {
    initializeData();
    setupEventListeners();
    setupColumnResizing();
    initializeTooltips();
});


// Inicializar dados
function initializeData() {
    const tableRows = $('#tableBody tr');
    currentData = tableRows.map(function() {
        const cells = $(this).find('td');
        return {
            id: cells.eq(0).text().trim(),
            nome_empresa: cells.eq(1).text().trim(),
            cnpj: cells.eq(2).text().trim(),
            municipio: cells.eq(3).text().trim(),
            uf: cells.eq(4).text().trim(),
            situacao: cells.eq(5).text().trim(),
            tipo: cells.eq(6).text().trim(),
            porte: cells.eq(7).text().trim(),
            acoes: cells.eq(8).html(),
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
                <td data-column="nome_empresa">${item.nome_empresa}</td>
                <td data-column="cnpj">${item.cnpj}</td>
                <td data-column="municipio">${item.municipio}</td>
                <td data-column="uf">${item.uf}</td>
                <td data-column="situacao">${item.situacao}</td>
                <td data-column="tipo">${item.tipo}</td>
                <td data-column="porte">${item.porte}</td>
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

// Atualizar paginação (versão com input)
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
    
    // Botão PRIMEIRA página
    const $firstLi = $('<li>').addClass(`page-item ${currentPage === 1 ? 'disabled' : ''}`)
        .html(`<a class="page-link" href="#" onclick="changePage(1)" title="Primeira página">
            <i class="bi bi-chevron-double-left"></i>
        </a>`);
    $pagination.append($firstLi);
    
    // Botão ANTERIOR
    const $prevLi = $('<li>').addClass(`page-item ${currentPage === 1 ? 'disabled' : ''}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${currentPage - 1})">
            <i class="bi bi-chevron-left"></i>
        </a>`);
    $pagination.append($prevLi);
    
    // ✅ INPUT para digitar número da página
    const $inputLi = $('<li>').addClass('page-item')
        .html(`
            <div class="d-flex align-items-center px-2">
                <span class="me-2">Página</span>
                <input type="number" 
                       id="pageInput" 
                       class="form-control form-control-sm" 
                       style="width: 60px; text-align: center;" 
                       value="${currentPage}" 
                       min="1" 
                       max="${totalPages}"
                       onchange="changePage(parseInt(this.value))"
                       onkeypress="if(event.key==='Enter') changePage(parseInt(this.value))">
                <span class="ms-2">de ${totalPages}</span>
            </div>
        `);
    $pagination.append($inputLi);
    
    // Botão PRÓXIMO
    const $nextLi = $('<li>').addClass(`page-item ${currentPage === totalPages ? 'disabled' : ''}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${currentPage + 1})">
            <i class="bi bi-chevron-right"></i>
        </a>`);
    $pagination.append($nextLi);
    
    // Botão ÚLTIMA página
    const $lastLi = $('<li>').addClass(`page-item ${currentPage === totalPages ? 'disabled' : ''}`)
        .html(`<a class="page-link" href="#" onclick="changePage(${totalPages})" title="Última página">
            <i class="bi bi-chevron-double-right"></i>
        </a>`);
    $pagination.append($lastLi);
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
            'Nome da Empresa': item.nome_empresa,
            'CNPJ': item.cnpj,
            'Municipio': item.municipio,
            'UF': item.uf,
            'Situacao': item.situacao,
            'Tipo': item.tipo,
            'Porte': item.porte
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

        downloadFile(csv, 'empresas.csv', 'text/csv');
    }

    function exportToExcel(data) {
        // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
        const csv = exportToCSV(data);
        downloadFile(csv, 'empresas.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    }

    function exportToPDF(data) {
        // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
        let content = 'LISTA DE EMPRESAS\n\n';

        const headers = Object.keys(data[0]);
        content += headers.join('\t') + '\n';
        content += '='.repeat(100) + '\n';

        data.forEach(row => {
            content += headers.map(header => row[header]).join('\t') + '\n';
        });

        downloadFile(content, 'empresas.pdf', 'application/pdf');
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
            // $.get('/api/estudos').done(function(data) {
            //     // Atualizar currentData com novos dados
            //     initializeData();
            // });

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
                new bootstrap.Tooltip(this);
            });
        }
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


// Função para formatar CNPJ
function formatarCNPJ(cnpj) {
    if (!cnpj) return 'N/A';
    cnpj = cnpj.replace(/\D/g, '');
    return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5');
}

// Função para formatar CEP
function formatarCEP(cep) {
    if (!cep) return 'N/A';
    cep = cep.replace(/\D/g, '');
    return cep.replace(/^(\d{5})(\d{3})$/, '$1-$2');
}

// Função para formatar telefone
function formatarTelefone(tel) {
    if (!tel) return 'N/A';
    tel = tel.replace(/\D/g, '');
    if (tel.length === 11) {
        return tel.replace(/^(\d{2})(\d{5})(\d{4})$/, '($1) $2-$3');
    } else if (tel.length === 10) {
        return tel.replace(/^(\d{2})(\d{4})(\d{4})$/, '($1) $2-$3');
    }
    return tel;
}

// Função para formatar data
function formatarData(data) {
    if (!data) return 'N/A';
    const d = new Date(data);
    return d.toLocaleDateString('pt-BR');
}

// Função para obter badge de situação
function getBadgeSituacao(situacao) {
    const situacoes = {
        'ATIVA': 'success',
        'BAIXADA': 'danger',
        'SUSPENSA': 'warning',
        'INAPTA': 'secondary'
    };
    const cor = situacoes[situacao?.toUpperCase()] || 'secondary';
    return `<span class="badge bg-${cor}">${situacao || 'N/A'}</span>`;
}

// Função principal para ver detalhes
function verDetalhes(id) {
    const $modalBody = $('#modalDetalhesBody');
    
    // Mostra spinner de carregamento
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);
    
    // Abre o modal
    const modal = new bootstrap.Modal($('#modalDetalhes')[0]);
    modal.show();
    
    // Busca dados da empresa
    $.get(`/empresas/${id}/api`)
        .done(function(data) {
            if (data.error) {
                $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                return;
            }
            
            console.log('🔹 Dados da empresa carregados:', data);
            
            const detalhesHtml = `
                <div class="row g-3">
                    <!-- Card: Informações Básicas -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-primary text-white">
                                <i class="fas fa-building me-2"></i>Informações Básicas
                            </div>
                            <div class="card-body">
                                <p><strong>Razão Social:</strong> ${data.nome_empresa || 'N/A'}</p>
                                <p><strong>Nome Fantasia:</strong> ${data.fantasia || 'N/A'}</p>
                                <p><strong>CNPJ:</strong> ${formatarCNPJ(data.cnpj)}</p>
                                <p><strong>Situação:</strong> ${getBadgeSituacao(data.situacao)}</p>
                                <p><strong>Data de Abertura:</strong> ${formatarData(data.abertura)}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Card: Classificação -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-success text-white">
                                <i class="fas fa-tags me-2"></i>Classificação
                            </div>
                            <div class="card-body">
                                <p><strong>Tipo:</strong> ${data.tipo || 'N/A'}</p>
                                <p><strong>Porte:</strong> ${data.porte || 'N/A'}</p>
                                <p><strong>Natureza Jurídica:</strong> ${data.natureza_juridica || 'N/A'}</p>
                                <p><strong>EFR:</strong> ${data.efr || 'N/A'}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Card: Endereço -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-warning text-dark">
                                <i class="fas fa-map-marker-alt me-2"></i>Endereço
                            </div>
                            <div class="card-body">
                                <p><strong>Logradouro:</strong> ${data.logradouro || 'N/A'}, ${data.numero || 'S/N'}</p>
                                ${data.complemento ? `<p><strong>Complemento:</strong> ${data.complemento}</p>` : ''}
                                <p><strong>Bairro:</strong> ${data.bairro || 'N/A'}</p>
                                <p><strong>Município:</strong> ${data.municipio || 'N/A'} - ${data.uf || 'N/A'}</p>
                                <p><strong>CEP:</strong> ${formatarCEP(data.cep)}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Card: Contato -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-info text-white">
                                <i class="fas fa-phone me-2"></i>Contato
                            </div>
                            <div class="card-body">
                                <p><strong>Telefone:</strong> ${formatarTelefone(data.telefone)}</p>
                                <p><strong>Email:</strong> ${data.email || 'N/A'}</p>
                            </div>
                        </div>
                    </div>

                    <!-- Card: Situação Cadastral -->
                    <div class="col-12">
                        <div class="card shadow-sm">
                            <div class="card-header bg-secondary text-white">
                                <i class="fas fa-file-alt me-2"></i>Situação Cadastral
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4">
                                        <p><strong>Data da Situação:</strong> ${formatarData(data.data_situacao)}</p>
                                    </div>
                                    <div class="col-md-4">
                                        <p><strong>Motivo:</strong> ${data.motivo_situacao || 'N/A'}</p>
                                    </div>
                                    <div class="col-md-4">
                                        <p><strong>Última Atualização:</strong> ${formatarData(data.ultima_atualizacao)}</p>
                                    </div>
                                </div>
                                ${data.situacao_especial ? `
                                    <hr>
                                    <p><strong>Situação Especial:</strong> ${data.situacao_especial}</p>
                                    <p><strong>Data Situação Especial:</strong> ${formatarData(data.data_situacao_especial)}</p>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            $modalBody.html(detalhesHtml);
        })
        .fail(function(xhr, status, error) {
            console.error('Erro ao carregar detalhes:', error);
            $modalBody.html(`
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Erro ao carregar detalhes da empresa. Tente novamente.
                </div>
            `);
        });
}

// Limpa o modal quando fechado
$('#modalDetalhes').on('hidden.bs.modal', function() {
    $('#modalDetalhesBody').html('');
});





