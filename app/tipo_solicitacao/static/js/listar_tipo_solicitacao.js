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
            viabilidade: cells.eq(1).text().trim(),
            viabilidade_abrev: cells.eq(2).text().trim(),
            analise: cells.eq(3).text().trim(),
            analise_abrev: cells.eq(4).text().trim(),
            pedido: cells.eq(5).text().trim(),
            pedido_abrev: cells.eq(6).text().trim(),
            status_doc: cells.eq(7).text().trim(),
            acoes: cells.eq(8).clone(), // era: acoes: cells.eq(4).html(),
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
            const $row = $('<tr>');

            $('<td>').attr('data-column', 'id').text(item.id).appendTo($row);
            $('<td>').attr('data-column', 'viabilidade').text(item.viabilidade).appendTo($row);
            $('<td>').attr('data-column', 'viabilidade_abrev').text(item.viabilidade_abrev).appendTo($row);
            $('<td>').attr('data-column', 'analise').text(item.analise).appendTo($row);
            $('<td>').attr('data-column', 'analise_abrev').text(item.analise_abrev).appendTo($row);
            $('<td>').attr('data-column', 'pedido').text(item.pedido).appendTo($row);
            $('<td>').attr('data-column', 'pedido_abrev').text(item.pedido_abrev).appendTo($row);

            // status_doc: clona o TD original para preservar o badge colorido
            const $tdStatus = currentData.find(d => d.id === item.id);
            if ($tdStatus) {
                const $originalRow = $($tdStatus.element);
                const $statusCell = $originalRow.find('[data-column="status_doc"]').clone(true);
                $row.append($statusCell);
            } else {
                $('<td>').attr('data-column', 'status_doc').text(item.status_doc).appendTo($row);
            }

            const $tdAcoes = $('<td>').attr('data-column', 'acoes');
            $tdAcoes.append(item.acoes.clone(true));
            $row.append($tdAcoes);

            $tbody.append($row);
        });

        applyColumnVisibility();
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
            'Viabilidade': item.viabilidade,
            'Viabilidade Abrev.': item.viabilidade_abrev,
            'Analise': item.analise,
            'Analise Abrev.': item.analise_abrev,
            'Pedido': item.pedido,
            'Pedido Abrev.': item.pedido_abrev
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

        downloadFile(csv, 'tipo_solicitacao.csv', 'text/csv');
    }

    function exportToExcel(data) {
        // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
        const csv = exportToCSV(data);
        downloadFile(csv, 'tipo_solicitacao.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    }

    function exportToPDF(data) {
        // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
        let content = 'LISTA DE TIPOS DE SOLICITACAO\n\n';

        const headers = Object.keys(data[0]);
        content += headers.join('\t') + '\n';
        content += '='.repeat(100) + '\n';

        data.forEach(row => {
            content += headers.map(header => row[header]).join('\t') + '\n';
        });

        downloadFile(content, 'tipo_solicitacao.pdf', 'application/pdf');
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


    function editarDetalhes(tipo_solicitacaoId) {
        const $modalBody = $('#modalEditarBody');
    

        // Loading spinner
        $modalBody.html(`
            <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
                <div class="spinner-border text-warning" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `);
    
        const modal = new bootstrap.Modal($('#modalEditar')[0]);
        modal.show();

        // Requisição AJAX para pegar os dados
        console.log('ID tipo_solicitacaoId:', tipo_solicitacaoId);
        $.get(`/tipo_solicitacao/${tipo_solicitacaoId}/api`)
            
            .done(function(data) {
                console.log('ID passado:', data);
                console.log('Objeto retornado do Flask:', data);
                if (data.error) {
                    $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                    return;
                }
                console.log('ID HTML:', data.id);
    
                const editarHtml = `
                    <form id="formEdicao" data-tipo_solicitacao-id="${tipo_solicitacaoId}">
                        <div class="row g-3">
                            <div class="col-12">
                                <div class="card shadow-sm">
                                    <div class="card-header bg-secondary text-white">
                                        <i class="fas fa-info-circle me-2"></i>Detalhes do Circuito
                                    </div>
                                    <div class="card-body">
                                        <div class="mb-3">
                                            <label class="form-label"><strong>ID:</strong></label>
                                            <input type="text" class="form-control" value="${data.id}" readonly>
                                        </div>
                                        <div class="mb-3 row g-2">
                                            <div class="col-md-8">
                                                <label class="form-label"><strong>Viabilidade:</strong></label>
                                                <input type="text" name="viabilidade" class="form-control" value="${data.viabilidade || ''}" required>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label"><strong>Viabilidade Abrev:</strong></label>
                                                <input type="text" name="viabilidade_abrev" class="form-control" value="${data.viabilidade_abrev || ''}" required>
                                            </div>
                                        </div>
                                        <div class="mb-3 row g-2">
                                            <div class="col-md-8">
                                                <label class="form-label"><strong>Análise:</strong></label>
                                                <input type="text" name="analise" class="form-control" value="${data.analise || ''}" required>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label"><strong>Análise Abrev:</strong></label>
                                                <input type="text" name="analise_abrev" class="form-control" value="${data.analise_abrev || ''}" required>
                                            </div>
                                        </div>
                                        <div class="mb-3 row g-2">
                                            <div class="col-md-8">
                                                <label class="form-label"><strong>Pedido:</strong></label>
                                                <input type="text" name="pedido" class="form-control" value="${data.pedido || ''}" required>
                                            </div>
                                            <div class="col-md-4">
                                                <label class="form-label"><strong>Pedido Abrev:</strong></label>
                                                <input type="text" name="pedido_abrev" class="form-control" value="${data.pedido_abrev || ''}" required>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </form>
                `;
    
                $modalBody.html(editarHtml);
                
                // Inicializa Select2 dentro do modal
                $('#tensao-select').select2({
                    theme: 'bootstrap-5',
                    placeholder: 'Selecione...',
                    allowClear: true,
                    width: '100%',
                    dropdownParent: $('#modalEditar')
                });
                
            })
            .fail(function(xhr, status, error) {
                console.error('Erro:', error);
                $modalBody.html(`<div class="alert alert-danger">Erro ao carregar dados do circuito</div>`);
            });
    }

    function salvarEdicao() {
        const form = document.getElementById('formEdicao');
        const tipo_solicitacaoId = form.getAttribute('data-tipo_solicitacao-id');
        console.log('tipoisolicitacao-Id:', tipo_solicitacaoId);
        const formData = new FormData(form);
    
        // Converter FormData para objeto
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
    
        $.ajax({
            url: `/tipo_solicitacao/${tipo_solicitacaoId}/editar`,
            method: 'POST', // ou 'PATCH' dependendo da sua API
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function(response) {
                // Fechar modal
                bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
                
                // Mostrar mensagem de sucesso
                alert('Tipo de solicitação atualizado com sucesso!');
                
                // Recarregar a página ou tabela
                location.reload();
            },
            error: function(xhr, status, error) {
                console.error('Erro ao salvar:', error);
                alert('Erro ao salvar as alterações. Tente novamente.');
            }
        });
    }
    
    
function confirmarExclusao() {
    const form = document.getElementById('formEdicao');
    const tipo_solicitacaoId = form.getAttribute('data-tipo_solicitacao-id');
    
    // Primeira confirmação
    if (!confirm('Tem certeza que deseja excluir este tipo de solicitação? Esta operação não pode ser desfeita.')) {
        return;
    }
    
    // Segunda verificação: digitar "EXCLUIR"
    const confirmacao = prompt('Para confirmar, digite a palavra: EXCLUIR');
    if (confirmacao !== 'EXCLUIR') {
        alert('❌ Confirmação incorreta. Exclusão cancelada.');
        return;
    }
    
    $.ajax({
        url: `/tipo_solicitacao/${tipo_solicitacaoId}/excluir`,
        method: 'POST',
        success: function(response) {
            bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
            alert('✅ Tipo de solicitação excluído com sucesso!');
            location.reload();
        },
        error: function(xhr, status, error) {
            let mensagemErro = '❌ Erro ao excluir o tipo de solicitação!';
            
            // Tenta pegar a mensagem do servidor
            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensagemErro = xhr.responseJSON.message;
            } else if (xhr.status === 409) {
                mensagemErro = '❌ Não é possível excluir este circuito!\n\n' +
                               'Existem registros relacionados na tabela de Estudos.\n\n';
            }
            
            alert(mensagemErro);
            console.error('Erro detalhado:', xhr.responseText);
        }
    });
}

    
function abrirModalAdicionar() {
    const $modalBody = $('#modalAdicionarBody');
    
    // Spinner enquanto carrega
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);
    
    const modal = new bootstrap.Modal($('#modalAdicionar')[0]);
    modal.show();
    
    // HTML simples - apenas campos de texto obrigatórios
    const addHtml = `
        <form id="formAdicionar" novalidate>
            <div class="card shadow-sm">
                <div class="card-header bg-secondary text-white">
                    <i class="fas fa-plus-circle me-2"></i>Novo Tipo de Solicitação
                </div>
                <div class="card-body">

                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Viabilidade:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="viabilidade" 
                                id="campo-viabilidade"
                                class="form-control" 
                                placeholder="Digite a viabilidade"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Viabilidade.
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Viabilidade Abrev:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="viabilidade_abrev" 
                                id="campo-viabilidade-abrev"
                                class="form-control" 
                                placeholder="Digite a Viabilidade abrev"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Viabilidade Abrev.
                            </div>
                        </div>
                    </div>

                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Análise:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="analise" 
                                id="campo-analise"
                                class="form-control" 
                                placeholder="Digite a análise"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Análise.
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Análise Abrev:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="analise_abrev" 
                                id="campo-analise-abrev"
                                class="form-control" 
                                placeholder="Digite a Análise abrev"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Análise Abrev.
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3 row g-2">
                        <div class="col-md-8">
                            <label class="form-label"><strong>Pedido:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="pedido" 
                                id="campo-pedido"
                                class="form-control" 
                                placeholder="Digite o pedido"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Pedido.
                            </div>
                        </div>
                        <div class="col-md-4">
                            <label class="form-label"><strong>Pedido Abrev:</strong> <span class="text-danger">*</span></label>
                            <input 
                                type="text" 
                                name="pedido_abrev" 
                                id="campo-pedido-abrev"
                                class="form-control" 
                                placeholder="Digite o Pedido abrev"
                                required
                            >
                            <div class="invalid-feedback">
                                Por favor, preencha o campo Pedido Abrev.
                            </div>
                        </div>
                    </div>
                    
                </div>
            </div>
        </form>
    `;
    
    $modalBody.html(addHtml);
}

function salvarNovoTipoSolicitacao() {
    const form = document.getElementById('formAdicionar');
    
    // Remove classes de validação anteriores
    form.classList.remove('was-validated');
    
    // Validação manual com mensagens personalizadas
    const viabilidade = document.getElementById('campo-viabilidade');
    const analise = document.getElementById('campo-analise');
    const pedido = document.getElementById('campo-pedido');
    
    let camposVazios = [];
    
    if (!viabilidade.value.trim()) {
        camposVazios.push('Viabilidade');
        viabilidade.classList.add('is-invalid');
    } else {
        viabilidade.classList.remove('is-invalid');
    }
    
    if (!analise.value.trim()) {
        camposVazios.push('Análise');
        analise.classList.add('is-invalid');
    } else {
        analise.classList.remove('is-invalid');
    }
    
    if (!pedido.value.trim()) {
        camposVazios.push('Pedido');
        pedido.classList.add('is-invalid');
    } else {
        pedido.classList.remove('is-invalid');
    }
    
    // Se houver campos vazios, mostra alerta
    if (camposVazios.length > 0) {
        alert(`⚠️ Por favor, preencha o(s) seguinte(s) campo(s) obrigatório(s):\n\n• ${camposVazios.join('\n• ')}`);
        
        // Foca no primeiro campo vazio
        if (!viabilidade.value.trim()) {
            viabilidade.focus();
        } else if (!analise.value.trim()) {
            analise.focus();
        } else if (!pedido.value.trim()) {
            pedido.focus();
        }
        
        return;
    }
    
    // Coleta os dados
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value.trim(); // Remove espaços extras
    });
    
    console.log('Dados a enviar:', data);
    
    // Envia para o backend
    $.ajax({
        url: `/tipo_solicitacao/adicionar`,
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            console.log('Resposta:', response);
            
            // Fecha o modal
            bootstrap.Modal.getInstance(document.getElementById('modalAdicionar')).hide();
            
            // Mensagem de sucesso
            alert('✅ Tipo de solicitação adicionado com sucesso!');
            
            // Recarrega a página
            location.reload();
        },
        error: function(xhr, status, error) {
            console.error('Erro:', error);
            console.error('Resposta do servidor:', xhr.responseText);
            alert('❌ Erro ao adicionar. Tente novamente.');
        }
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

// Documentos Padronizados

let tipoSolicitacaoIdDocumento = null;

function getAlertaRevisao(dataAtualizacaoStr) {
    if (!dataAtualizacaoStr) return null;

    // Converte "DD/MM/YYYY HH:MM" para Date
    const partes = dataAtualizacaoStr.split(' ')[0].split('/');
    const dataAtualizacao = new Date(`${partes[2]}-${partes[1]}-${partes[0]}`);
    const hoje = new Date();

    // Data limite = atualização + 6 meses
    const dataLimite = new Date(dataAtualizacao);
    dataLimite.setMonth(dataLimite.getMonth() + 6);

    const diffMs = dataLimite - hoje;
    const diffDias = Math.ceil(diffMs / (1000 * 60 * 60 * 24));

    if (diffDias < 0) {
        return {
            tipo: 'danger',
            icone: 'bi-exclamation-triangle-fill',
            mensagem: `Documento vencido há ${Math.abs(diffDias)} dia(s). Revisão obrigatória!`
        };
    } else if (diffDias <= 30) {
        return {
            tipo: 'warning',
            icone: 'bi-clock-fill',
            mensagem: `Documento vence em ${diffDias} dia(s). Revisão recomendada!`
        };
    }
    return {
        tipo: 'success',
        icone: 'bi-check-circle-fill',
        mensagem: `Documento em dia. Próxima revisão em ${diffDias} dia(s) (${dataLimite.toLocaleDateString('pt-BR')}).`
    };
}


function abrirModalDocumento(tipoId) {
    tipoSolicitacaoIdDocumento = tipoId;

    const $modalBody = $('#modalDocumentoBody');
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 150px;">
            <div class="spinner-border text-info" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($('#modalDocumento')[0]);
    modal.show();

    $.get(`/tipo_solicitacao/${tipoId}/api`)
        .done(function(data) {
            const doc = data.doc_padronizado;

            let docHtml = '';
            if (doc) {
                const alerta = getAlertaRevisao(doc.data_atualizacao);
                const alertaHtml = alerta ? `
                    <div class="alert alert-${alerta.tipo} d-flex align-items-center py-2 mb-3">
                        <i class="bi ${alerta.icone} me-2 fs-5"></i>
                        <span>${alerta.mensagem}</span>
                    </div>
                ` : '';

                docHtml = `
                    ${alertaHtml}
                    <p><strong>Documento atual:</strong> ${doc.nome_doc || '(sem nome)'}</p>
                    <p><strong>Tipo:</strong> ${doc.tipo_doc || '-'}</p>
                    <p><strong>Criado em:</strong> ${doc.data_criacao || '-'}</p>
                    <p><strong>Última atualização:</strong> ${doc.data_atualizacao || '-'}</p>
                    <p><strong>Total de versões:</strong> ${doc.total_versoes}</p>
                    <button class="btn btn-sm btn-outline-primary mb-2" onclick="baixarDocumentoAtual()">
                        <i class="bi bi-download"></i> Baixar atual
                    </button>
                `;
            } else {
                docHtml = `
                    <div class="alert alert-warning">
                        Nenhum documento padrão cadastrado para este tipo de solicitação.
                    </div>
                `;
            }

            $modalBody.html(`
                <div class="mb-3">
                    <h6>Tipo de Solicitação ${data.id}</h6>
                    <p><strong>Viabilidade:</strong> ${data.viabilidade || '-'}</p>
                    <p><strong>Análise:</strong> ${data.analise || '-'}</p>
                    <p><strong>Pedido:</strong> ${data.pedido || '-'}</p>
                </div>
                <hr>
                <div class="mb-3">
                    ${docHtml}
                </div>
                <hr>
                <div class="mb-2">
                    <h6>Versões anteriores</h6>
                    <div id="listaVersoesDoc">
                        Carregando versões...
                    </div>
                </div>
            `);

            carregarVersoesDocumento();
        })
        .fail(function() {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar informações do documento.</div>');
        });
}

function carregarVersoesDocumento() {
    if (!tipoSolicitacaoIdDocumento) return;

    $.get(`/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/versoes`)
        .done(function(resp) {
            if (resp.status !== 'success') {
                $('#listaVersoesDoc').html('<div class="alert alert-danger">Erro ao carregar versões.</div>');
                return;
            }

            const versoes = resp.versoes || [];
            if (versoes.length === 0) {
                $('#listaVersoesDoc').html('<p class="text-muted mb-0">Nenhuma versão anterior encontrada.</p>');
                return;
            }

            let html = `
                <table class="table table-sm table-bordered mb-0">
                    <thead class="table-light">
                        <tr>
                            <th style="width: 80px;">Versão</th>
                            <th>Nome</th>
                            <th style="width: 180px;">Data atualização</th>
                            <th style="width: 80px;">Ações</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            versoes.forEach(v => {
                html += `
                    <tr>
                        <td class="text-center">${v.versao}</td>
                        <td>${v.nome_doc}</td>
                        <td>${v.data_atualizaocao || '-'}</td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-outline-secondary" onclick="baixarVersaoDocumento(${v.id})">
                                <i class="bi bi-download"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            html += '</tbody></table>';
            $('#listaVersoesDoc').html(html);
        })
        .fail(function() {
            $('#listaVersoesDoc').html('<div class="alert alert-danger">Erro ao carregar versões.</div>');
        });
}

function enviarDocumentoPadrao() {
    if (!tipoSolicitacaoIdDocumento) return;

    const arquivo = $('#arquivoDocumento')[0].files[0];
    if (!arquivo) {
        alert('Selecione um arquivo para enviar.');
        return;
    }

    const formData = new FormData();
    formData.append('arquivo', arquivo);

    $.ajax({
        url: `/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/upload`,
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(resp) {
            if (resp.status === 'success') {
                alert('Documento enviado/atualizado com sucesso.');
            } else {
                alert(resp.message || 'Erro ao enviar documento.');
            }
        },
        error: function() {
            alert('Erro ao enviar documento. Tente novamente.');
        }
    });
}

function baixarDocumentoAtual() {
    if (!tipoSolicitacaoIdDocumento) return;
    window.location.href = `/tipo_solicitacao/${tipoSolicitacaoIdDocumento}/documento/download`;
}

function baixarVersaoDocumento(idVersao) {
    window.location.href = `/tipo_solicitacao/documento/versao/${idVersao}/download`;
}



