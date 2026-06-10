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
            nome: cells.eq(1).text().trim(),
            sigla: cells.eq(2).text().trim(),
            municipio: cells.eq(3).text().trim(),
            edp: cells.eq(4).text().trim(),
            lat: cells.eq(5).text().trim(),
            longitude: cells.eq(6).text().trim(),
            acoes: cells.eq(7).html(),
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
                <td data-column="nome">${item.nome}</td>
                <td data-column="sigla">${item.sigla}</td>
                <td data-column="municipio">${item.municipio}</td>
                <td data-column="edp">${item.edp}</td>
                <td data-column="lat">${item.lat}</td>
                <td data-column="longitude">${item.longitude}</td>
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
            'Subestacao': item.nome,
            'Sigla': item.sigla,
            'Municipio': item.municipio,
            'EDP': item.edp,
            'Latitude': item.lat,
            'Longitude': item.long
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

        downloadFile(csv, 'subestacoes.csv', 'text/csv');
    }

    function exportToExcel(data) {
        // Simulação de export Excel (seria necessário uma biblioteca como SheetJS)
        const csv = exportToCSV(data);
        downloadFile(csv, 'subestacoes.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    }

    function exportToPDF(data) {
        // Simulação de export PDF (seria necessário uma biblioteca como jsPDF)
        let content = 'LISTA DE SUBESTACOES\n\n';

        const headers = Object.keys(data[0]);
        content += headers.join('\t') + '\n';
        content += '='.repeat(100) + '\n';

        data.forEach(row => {
            content += headers.map(header => row[header]).join('\t') + '\n';
        });

        downloadFile(content, 'subestacoes.pdf', 'application/pdf');
    }

    function downloadFile(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = $('<a>').attr({
            href: url,
            download: filename,
            'data-no-loading': 'true'
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


function editarSubestacao(id) {
    const $modalBody = $('#modalEditarBody');
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200;">
            <div class="spinner-border text-warning" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($('#modalEditar')[0]);
    modal.show();

    // 🔹 1. Buscar dados da subestação
    $.get(`/subestacoes/${id}/api`)
        .done(function (data) {
            console.log('🔹 Dados carregados:', data);

            const editarHtml = `
                <form id="formEditarSubestacao" data-subestacao-id="${id}">
                    <div class="card shadow-sm">
                        <div class="card-header bg-secondary text-white">
                            <i class="fas fa-bolt me-2"></i>Editar Subestação
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>Nome:</strong></label>
                                <input type="text" name="nome" class="form-control" value="${data.nome || ''}" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Sigla:</strong></label>
                                <input type="text" name="sigla" class="form-control" value="${data.sigla || ''}" required maxlength="10">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Latitude:</strong></label>
                                <input type="text" name="lat" class="form-control" value="${data.lat || ''}">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Longitude:</strong></label>
                                <input type="text" name="longitude" class="form-control" value="${data.longitude || ''}">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Município:</strong></label>
                                <select name="id_municipio" class="form-select" id="municipio-edit-select" required></select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>EDP (Estado):</strong></label>
                                <select name="id_edp" class="form-select" id="edp-edit-select" required></select>
                            </div>

                        </div>
                    </div>
                </form>
            `;

            $modalBody.html(editarHtml);

            // 🔹 Carregar selects de EDP e Município
            carregarEdpsSelect(data.id_edp, data.id_municipio);
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar dados da subestação.</div>');
        });
}


// 🔹 2. Carregar EDPs e depois Municípios
function carregarEdpsSelect(edpSelecionado, municipioSelecionado) {
    $.get('/subestacoes/edps/api')
        .done(function (edps) {
            const $edpSelect = $('#edp-edit-select');
            const options = edps.map(e => `<option value="${e.id}" ${e.id === edpSelecionado ? 'selected' : ''}>${e.empresa}</option>`);
            $edpSelect.html('<option value="">Selecione...</option>' + options.join(''));

            $edpSelect.select2({
                theme: 'bootstrap-5',
                dropdownParent: $('#modalEditar')
            });

            // Carrega municípios correspondentes ao EDP atual
            if (edpSelecionado) {
                carregarMunicipiosSelect(edpSelecionado, municipioSelecionado);
            }

            // Sempre que mudar o EDP, atualiza os municípios
            $edpSelect.on('change', function () {
                carregarMunicipiosSelect($(this).val(), null);
            });
        });
}


function carregarMunicipiosSelect(edpId, municipioSelecionado) {
    const $municipioSelect = $('#municipio-edit-select');

    if (!edpId) {
        $municipioSelect.html('<option>Selecione o Estado primeiro...</option>').prop('disabled', true);
        return;
    }

    $.get(`/subestacoes/municipios/api/${edpId}`)
        .done(function (municipios) {
            if (!municipios.length) {
                $municipioSelect.html('<option value="">Nenhum município encontrado</option>').prop('disabled', true);
            } else {
                const options = municipios.map(m =>
                    `<option value="${m.id}" ${m.id === municipioSelecionado ? 'selected' : ''}>${m.municipio}</option>`
                ).join('');
                $municipioSelect.html('<option value="">Selecione...</option>' + options).prop('disabled', false);
            }

            $municipioSelect.select2({
                theme: 'bootstrap-5',
                dropdownParent: $('#modalEditar')
            });
        })
        .fail(() => $municipioSelect.html('<option>Erro ao carregar municípios</option>').prop('disabled', true));
}


// 🔹 3. Função para salvar a edição
function salvarEdicao() {
    const form = document.getElementById('formEditarSubestacao');
    const id = form.getAttribute('data-subestacao-id');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = Object.fromEntries(new FormData(form).entries());

    $.ajax({
        url: `/subestacoes/${id}/editar`,
        method: 'POST',
        data: JSON.stringify(formData),
        contentType: 'application/json',
        success: function (response) {
            alert(response.message || '✅ Subestação atualizada com sucesso!');
            bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
            location.reload();
        },
        error: function (xhr) {
            console.error('Erro:', xhr.responseText);
            alert('❌ Erro ao salvar alterações.');
        }
    });
}

    
    
function confirmarExclusao() {
    const form = document.getElementById('formEditarSubestacao');
    const id = form.getAttribute('data-subestacao-id');
    
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
        url: `/subestacoes/${id}/excluir`,
        method: 'POST',
        success: function(response) {
            bootstrap.Modal.getInstance(document.getElementById('modalEditar')).hide();
            alert('✅ Subestação excluída com sucesso!');
            location.reload();
        },
        error: function(xhr, status, error) {
            let mensagemErro = '❌ Erro ao excluir subestação!';
            
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
    $modalBody.html(`
        <div class="d-flex justify-content-center align-items-center" style="height: 200px;">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
        </div>
    `);

    const modal = new bootstrap.Modal($('#modalAdicionar')[0]);
    modal.show();

    // 🔹 Carregar lista de EDPs
    $.get('/subestacoes/edps/api')
        .done(function (edps) {
            let edpOptions = edps.map(edp => `<option value="${edp.id}">${edp.empresa}</option>`).join('');

            const addHtml = `
                <form id="formAdicionarSubestacao" novalidate>
                    <div class="card shadow-sm">
                        <div class="card-header bg-secondary text-white">
                            <i class="fas fa-bolt me-2"></i>Nova Subestação
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label"><strong>Nome:</strong> <span class="text-danger">*</span></label>
                                <input type="text" name="nome" class="form-control" placeholder="Digite o nome da Subestação" required>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Sigla:</strong> <span class="text-danger">*</span></label>
                                <input type="text" name="sigla" class="form-control" placeholder="Digite a sigla" required maxlength="10">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>EDP (Estado):</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_edp" id="edp-select" required>
                                    <option value="">Selecione...</option>
                                    ${edpOptions}
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Município:</strong> <span class="text-danger">*</span></label>
                                <select class="form-select" name="id_municipio" id="municipio-select" required disabled>
                                    <option value="">Selecione o Estado primeiro...</option>
                                </select>
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Latitude:</strong></label>
                                <input type="text" name="lat" class="form-control" placeholder="Ex: -20.123456">
                            </div>

                            <div class="mb-3">
                                <label class="form-label"><strong>Longitude:</strong></label>
                                <input type="text" name="longitude" class="form-control" placeholder="Ex: -40.987654">
                            </div>
                        </div>
                    </div>
                </form>
            `;
            $modalBody.html(addHtml);

            // Inicializa select2 (corrigido o fechamento do seletor que estava errado)
            $('#edp-select, #municipio-select').select2({
                theme: 'bootstrap-5',
                placeholder: 'Selecione...',
                width: '100%',
                dropdownParent: $('#modalAdicionar')
            });

            // 🔹 Quando muda o EDP → carregar municípios dinamicamente
            $('#edp-select').on('change', function () {
                const idEdp = $(this).val();
                const $municipio = $('#municipio-select');

                if (!idEdp) {
                    $municipio.html('<option value="">Selecione o Estado primeiro...</option>').prop('disabled', true);
                    return;
                }

                $municipio.html('<option>Carregando...</option>').prop('disabled', true);

                $.get(`/subestacoes/municipios/api/${idEdp}`)
                    .done(function (municipios) {
                        if (municipios.length === 0) {
                            $municipio.html('<option value="">Nenhum município encontrado</option>').prop('disabled', true);
                        } else {
                            const options = municipios.map(m => `<option value="${m.id}">${m.municipio}</option>`).join('');
                            $municipio.html('<option value="">Selecione...</option>' + options).prop('disabled', false);
                        }
                    })
                    .fail(function () {
                        $municipio.html('<option>Erro ao carregar municípios</option>').prop('disabled', true);
                    });
            });
        })
        .fail(function () {
            $modalBody.html('<div class="alert alert-danger">Erro ao carregar EDPs!</div>');
        });
}


// 🔹 Salvar Subestação (Ajax)
function salvarNova() {
    const form = document.getElementById('formAdicionarSubestacao');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const formData = Object.fromEntries(new FormData(form).entries());

    $.ajax({
        url: '/subestacoes/nova',
        method: 'POST',
        data: JSON.stringify(formData),
        contentType: 'application/json',
        success: function (response) {
            bootstrap.Modal.getInstance(document.getElementById('modalAdicionar')).hide();
            alert('✅ ' + response.msg);
            location.reload();
        },
        error: function (xhr) {
            alert('❌ Falha ao salvar. ' + (xhr.responseJSON?.erro || 'Verifique os dados e tente novamente.'));
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
    
    // Busca dados da subestação
    $.get(`/subestacoes/${id}/api`)
        .done(function(data) {
            if (data.error) {
                $modalBody.html(`<div class="alert alert-danger">${data.error}</div>`);
                return;
            }
            
            console.log('🔹 Dados carregados:', data);
            
            const detalhesHtml = `
                <div class="row g-3">
                    <!-- Card: Informações Básicas -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-secondary text-white">
                                <i class="fas fa-bolt me-2"></i>Informações Básicas
                            </div>
                            <div class="card-body">
                                <p><strong>Nome:</strong> ${data.nome || 'N/A'}</p>
                                <p><strong>Sigla:</strong> ${data.sigla || 'N/A'}</p>
                                <p><strong>Município:</strong> ${data.municipio || 'N/A'}</p>
                                <p><strong>Estado (EDP):</strong> ${data.edp || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Card: Coordenadas -->
                    <div class="col-md-6">
                        <div class="card shadow-sm h-100">
                            <div class="card-header bg-secondary text-white">
                                <i class="fas fa-map-marker-alt me-2"></i>Localização
                            </div>
                            <div class="card-body">
                                <p><strong>Latitude:</strong> ${data.longitude || 'N/A'}</p>
                                <p><strong>Longitude:</strong> ${data.lat || 'N/A'}</p>
                                ${data.longitude && data.lat ? `
                                    <a href="https://www.google.com/maps?q=${data.longitude},${data.lat}" 
                                       target="_blank" 
                                       class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-external-link-alt me-1"></i>Ver no Google Maps
                                    </a>
                                ` : '<p class="text-muted">Coordenadas não disponíveis</p>'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Mapa -->
                ${data.longitude && data.lat ? `
                    <div class="row g-3 mt-3">
                        <div class="col-12">
                            <div class="card shadow-sm">
                                <div class="card-header bg-secondary text-white">
                                    <i class="fas fa-map me-2"></i>Mapa
                                </div>
                                <div class="card-body p-0">
                                    <div id="mapaDetalhes" style="height: 400px; width: 100%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : ''}
            `;
            
            $modalBody.html(detalhesHtml);
            
            // Inicializa o mapa se houver coordenadas
            if (data.longitude && data.lat) {
                inicializarMapaDetalhes(data.longitude, data.lat, data.nome);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('Erro:', error);
            $modalBody.html(`<div class="alert alert-danger">Erro ao carregar detalhes da subestação</div>`);
        });
}

// Função para inicializar o mapa no modal de detalhes
function inicializarMapaDetalhes(lat, lng, nome) {
    // Aguarda um pouco para garantir que o elemento está renderizado
    setTimeout(() => {
        const mapaDiv = document.getElementById('mapaDetalhes');
        
        if (!mapaDiv) {
            console.error('Elemento do mapa não encontrado');
            return;
        }
        
        // Remove mapa existente se houver
        if (mapaDiv._leaflet_id) {
            const mapInstance = mapaDiv._map;
            if (mapInstance) {
                mapInstance.remove();
            }
        }
        
        // Cria novo mapa
        const map = L.map('mapaDetalhes').setView([lat, lng], 13);
        
        // Adiciona camada de tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Adiciona marcador
        L.marker([lat, lng]).addTo(map)
            .bindPopup(`<strong>${nome}</strong><br>Lat: ${lat}<br>Lng: ${lng}`)
            .openPopup();
        
        // Força redimensionamento
        setTimeout(() => {
            map.invalidateSize();
        }, 100);
        
        // Armazena referência
        mapaDiv._map = map;
    }, 200);
}

// Limpa o mapa quando o modal é fechado
$('#modalDetalhes').on('hidden.bs.modal', function() {
    const mapaDiv = document.getElementById('mapaDetalhes');
    if (mapaDiv && mapaDiv._map) {
        mapaDiv._map.remove();
        mapaDiv._map = null;
    }
});






