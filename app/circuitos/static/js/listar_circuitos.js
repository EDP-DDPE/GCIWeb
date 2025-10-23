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
            circuito: cells.eq(1).text().trim(),
            subestacao: cells.eq(2).text().trim(),
            edp: cells.eq(3).text().trim(),
            tensao: cells.eq(4).text().trim(),
            acoes: cells.eq(5).html(),
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
                <td data-column="circuito">${item.circuito}</td>
                <td data-column="subestacao">${item.subestacao}</td>
                <td data-column="edp">${item.edp}</td>
                <td data-column="tensao">${item.tensao}</td>
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
            'Circuito': item.circuito,
            'Subestação': item.subestacao,
            'Estado': item.edp,
            'Tensão': item.tensao
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

        downloadFile(csv, 'circuitos.csv', 'text/csv');
    }

    function exportToExcel(data) {
        // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
        const csv = exportToCSV(data);
        downloadFile(csv, 'circuitos.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    }

    function exportToPDF(data) {
        // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
        let content = 'LISTA DE CIRCUITOS\n\n';

        const headers = Object.keys(data[0]);
        content += headers.join('\t') + '\n';
        content += '='.repeat(100) + '\n';

        data.forEach(row => {
            content += headers.map(header => row[header]).join('\t') + '\n';
        });

        downloadFile(content, 'circuitos.pdf', 'application/pdf');
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


    function editarDetalhes(circuitoId) {
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
        $.get(`/circuitos/${circuitoId}/api`)
            
            .done(function(data) {
                console.log('ID passado:', data);
                console.log('Objeto retornado do Flask:', data);
                if (data.error) {
                    $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                    return;
                }
    
                // HTML do modal com apenas tensao editável
                const editarHtml = `
                    <form id="formEdicao" data-circuito-id="${circuitoId}">
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
                                        <div class="mb-3">
                                            <label class="form-label"><strong>Circuito:</strong></label>
                                            <input type="text" class="form-control" value="${data.circuito}" readonly>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label"><strong>Subestação:</strong></label>
                                            <input type="text" class="form-control" value="${data.subestacao?.nome}" readonly>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label"><strong>Estado:</strong></label>
                                            <input type="text" class="form-control" value="${data.edp?.empresa}" readonly>
                                        </div>
                                        <div class="mb-3">
                                            <label class="form-label"><strong>Tensão:</strong></label>
                                            <select class="form-select" name="tensao" id="tensao-select" required>
                                                <option value="">Selecione...</option>
                                                <option value="11.4" ${data.tensao == 11.4 ? 'selected' : ''}>11.4 kV</option>
                                                <option value="13.2" ${data.tensao == 13.2 ? 'selected' : ''}>13.2 kV</option>
                                                <option value="13.8" ${data.tensao == 13.8 ? 'selected' : ''}>13.8 kV</option>
                                                <option value="34.5" ${data.tensao == 34.5 ? 'selected' : ''}>34.5 kV</option>
                                                <option value="69" ${data.tensao == 69 ? 'selected' : ''}>69 kV</option>
                                                <option value="88" ${data.tensao == 88 ? 'selected' : ''}>88 kV</option>
                                                <option value="138" ${data.tensao == 138 ? 'selected' : ''}>138 kV</option>
                                            </select>
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
        const circuitoId = form.getAttribute('data-circuito-id');
        console.log('circuitoId:', circuitoId);
        const formData = new FormData(form);
    
        // Converter FormData para objeto
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });
    
        $.ajax({
            url: `/circuitos/${circuitoId}/editar`,
            method: 'POST', // ou 'PATCH' dependendo da sua API
            data: JSON.stringify(data),
            contentType: 'application/json',
            success: function(response) {
                // Fechar modal
                bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
                
                // Mostrar mensagem de sucesso
                alert('Documento atualizado com sucesso!');
                
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
    const circuitoId = form.getAttribute('data-circuito-id');
    
    // Primeira confirmação
    if (!confirm('Tem certeza que deseja excluir este circuito? Esta operação não pode ser desfeita.')) {
        return;
    }
    
    // Segunda verificação: digitar "EXCLUIR"
    const confirmacao = prompt('Para confirmar, digite a palavra: EXCLUIR');
    if (confirmacao !== 'EXCLUIR') {
        alert('❌ Confirmação incorreta. Exclusão cancelada.');
        return;
    }
    
    $.ajax({
        url: `/circuitos/${circuitoId}/excluir`,
        method: 'POST',
        success: function(response) {
            bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
            alert('✅ Circuito excluído com sucesso!');
            location.reload();
        },
        error: function(xhr, status, error) {
            let mensagemErro = '❌ Erro ao excluir o circuito!';
            
            // Tenta pegar a mensagem do servidor
            if (xhr.responseJSON && xhr.responseJSON.message) {
                mensagemErro = xhr.responseJSON.message;
            } else if (xhr.status === 409) {
                mensagemErro = '❌ Não é possível excluir este circuito!\n\n' +
                               'Existem registros relacionados na tabela de Alternativas.\n\n' +
                               '⚠️ Remova todos os registros relacionados antes de excluir o circuito.';
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
    // Busca lista de ESTADOS (EDPs)
    $.get('/circuitos/edps/api')
        .done(function (edps) {
            let edpOptions = edps.map(edp =>
                `<option value="${edp.id}">${edp.empresa}</option>`
            ).join('');
            // HTML dinâmico do formulário
            const addHtml = `
                <form id="formAdicionar" novalidate>
                    <div class="card shadow-sm">
                        <div class="card-header bg-secondary text-white">
                            <i class="fas fa-info-circle me-2"></i>Novo Circuito
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>Estado (EDP):</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_edp" id="edp-select" required>
                                    <option value="">Selecione...</option>
                                    ${edpOptions}
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><strong>Subestação:</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_subestacao" id="subestacao-select" disabled required>
                                    <option value="">Selecione o Estado primeiro...</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><strong>Tensão:</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="tensao" id="tensao-select" required>
                                    <option value="">Selecione...</option>
                                    <option value="11.4">11.4 kV</option>
                                    <option value="13.2">13.2 kV</option>
                                    <option value="13.8">13.8 kV</option>
                                    <option value="34.5">34.5 kV</option>
                                    <option value="69">69 kV</option>
                                    <option value="88">88 kV</option>
                                    <option value="138">138 kV</option>
                                </select>
                            </div>
                            <div class="mb-3">
                                <label class="form-label"><strong>Circuito:</strong> <span class="text-danger">*</span></label>
                                <input
                                    type="text"
                                    class="form-control"
                                    name="circuito"
                                    id="campo-circuito"
                                    disabled
                                    placeholder="Selecione Estado e Subestação"
                                    required
                                >
                                <span class="form-text text-muted" id="dica-circuito"></span>
                            </div>
                        </div>
                    </div>
                </form>
            `;
            $modalBody.html(addHtml);
            // Inicializa Select2 dentro do modal
            $('#edp-select, #subestacao-select, #tensao-select').select2({
                theme: 'bootstrap-5',
                placeholder: 'Selecione...',
                allowClear: true,
                width: '100%',
                dropdownParent: $('#modalAdicionar')
            });
            // Quando muda o Estado (EDP), carregar Subestações
            $('#edp-select').on('change', function () {
                const edpId = $(this).val();
                const $sub = $('#subestacao-select');
                const $circuito = $('#campo-circuito');
                const $dica = $('#dica-circuito');
                $sub
                    .prop('disabled', true)
                    .html('<option>Carregando...</option>')
                    .trigger('change');
                if (!edpId) {
                    $sub.html('<option value="">Selecione o Estado primeiro...</option>').prop('disabled', true);
                    $circuito.prop('disabled', true).val('');
                    $dica.text('');
                    return;
                }
                // Buscar subestações válidas
                $.get(`/circuitos/subestacoes/api/${edpId}`)
                    .done(function (subs) {
                        if (!subs.length) {
                            $sub.html('<option value="">Nenhuma subestação disponível</option>').prop('disabled', true);
                        } else {
                            const options = '<option value="">Selecione...</option>' + subs.map(s =>
                                `<option value="${s.id}" data-sigla="${s.sigla}">${s.nome}</option>`
                            ).join('');
                            $sub.html(options).prop('disabled', false);
                        }
                        $sub.trigger('change.select2');
                    })
                    .fail(function () {
                        $sub.html('<option value="">Erro ao carregar subestações</option>').prop('disabled', true);
                    });
            });
            // Quando muda Subestação → habilitar campo Circuito
            $modalBody.on('change', '#subestacao-select', prepararCampoCircuito);
            // Valida formato dinamicamente conforme a digitação
            $modalBody.on('input', '#campo-circuito', function () {
                let edp = $("#edp-select option:selected").text().trim();
                let $sub = $("#subestacao-select option:selected");
                let sigla = $sub.data('sigla');
                let valor = $(this).val().replace(/\s+/g, ' ');
                const $dica = $('#dica-circuito');
                if (!sigla) return;
                if (edp === 'ES') {
                    // Exemplo: ABC01 (2 números obrigatórios)
                    const regex = new RegExp(`^${sigla}\\d{0,2}$`);
                    if (!regex.test(valor)) {
                        if (!valor.startsWith(sigla))
                            $(this).val(sigla);
                    }
                    $dica.text(`Formato: ${sigla}NN (2 números obrigatórios, ex: ${sigla}03)`);
                } else if (edp === 'SP') {
                    // Exemplo: RABC 0001 (4 números obrigatórios)
                    const prefixo = `R${sigla} `;
                    const regex = new RegExp(`^${prefixo}\\d{0,4}$`);
                    if (!regex.test(valor)) {
                        if (!valor.startsWith(prefixo))
                            $(this).val(prefixo);
                    }
                    $dica.text(`Formato: ${prefixo}NNNN (4 números obrigatórios, ex: ${prefixo}0001)`);
                }
            });
            // Controla habilitação e prefixo do campo Circuito
            function prepararCampoCircuito() {
                let edp = $("#edp-select option:selected").text().trim();
                let $subOpt = $("#subestacao-select option:selected");
                let sigla = $subOpt.data('sigla');
                let $campo = $('#campo-circuito');
                let $dica = $('#dica-circuito');
                if (!$("#edp-select").val() || !$("#subestacao-select").val() || !sigla) {
                    $campo.prop('disabled', true).val('');
                    $dica.text('Selecione primeiro o Estado e depois a Subestação.');
                    return;
                }
                if (edp === 'ES') {
                    $campo.prop('disabled', false)
                        .val(sigla)
                        .attr('maxlength', sigla.length + 2);
                    $dica.text(`Formato: ${sigla}NN (2 números obrigatórios)`);
                } else if (edp === 'SP') {
                    let prefixo = `R${sigla} `;
                    $campo.prop('disabled', false)
                        .val(prefixo)
                        .attr('maxlength', prefixo.length + 4);
                    $dica.text(`Formato: ${prefixo}NNNN (4 números obrigatórios)`);
                } else {
                    $campo.prop('disabled', true).val('');
                    $dica.text('Selecione um Estado válido (ES ou SP).');
                }
            }
            // 🔹 Removeu o botão de salvar — o submit será tratado externamente
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar EDPs!</div>');
        });
}
function salvarNovoCircuito() {
    const form = document.getElementById('formAdicionar');
    // Validação HTML5
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    // 🔹 VALIDAÇÃO CUSTOMIZADA: Quantidade de dígitos
    const edp = $("#edp-select option:selected").text().trim();
    const sigla = $("#subestacao-select option:selected").data('sigla');
    const circuito = $('#campo-circuito').val().trim();
    if (edp === 'ES') {
        // Deve ter exatamente 2 números após a sigla
        const regex = new RegExp(`^${sigla}\\d{2}$`);
        if (!regex.test(circuito)) {
            alert(`❌ Para ES, o circuito deve ter exatamente 2 números.\nExemplo: ${sigla}01`);
            $('#campo-circuito').focus();
            return;
        }
    } else if (edp === 'SP') {
        // Deve ter exatamente 4 números após "R[SIGLA] "
        const prefixo = `R${sigla} `;
        const regex = new RegExp(`^${prefixo}\\d{4}$`);
        if (!regex.test(circuito)) {
            alert(`❌ Para SP, o circuito deve ter exatamente 4 números.\nExemplo: ${prefixo}0001`);
            $('#campo-circuito').focus();
            return;
        }
    } else {
        alert('❌ Estado inválido. Selecione ES ou SP.');
        return;
    }
    // Se passou na validação, envia os dados
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    $.ajax({
        url: `/circuitos/adicionar`,
        method: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            bootstrap.Modal.getInstance(document.getElementById('modalAdicionar')).hide();
            alert('✅ Circuito adicionado com sucesso!');
            location.reload();
        },
        error: function(xhr, status, error) {
            alert('❌ Erro ao adicionar o circuito. Tente novamente.');
            console.log(xhr.responseText);
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






