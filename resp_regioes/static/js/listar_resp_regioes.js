// ======== Estado global ========
let currentData = [];
let filteredData = [];
let currentPage = 1;
let pageSize = 25;
let sortColumn = '';
let sortDirection = 'asc';
let columnFilters = {};

// ======== Inicialização ========
$(document).ready(function () {
  initializeData();
  setupEventListeners();
  setupColumnResizing();
  initializeTooltips();
  loadTableSettings();
});

// ======== Carrega dados da tabela (DOM -> memória) ========
function initializeData() {
  const $rows = $('#tableBody tr');

  currentData = $rows.map(function () {
    const $t = $(this);
    return {
      id_resp_regiao: $t.find('td[data-column="id_resp_regiao"]').text().trim().replace(/^#/, ''),
      regional: $t.find('td[data-column="regional"]').text().trim(),
      usuario: $t.find('td[data-column="usuario"]').text().trim(),
      ano_ref: $t.find('td[data-column="ano_ref"]').text().trim(),
      acoes: $t.find('td[data-column="acoes"]').html(),
      element: this
    };
  }).get();

  filteredData = [...currentData];
  updatePagination();
  renderTable();
}

// ======== Listeners de UI ========
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

  // Dropdowns
  $(document).on('click', closeDropdowns);

  // Form modal: criar/editar
  $('#respForm').on('submit', submitRespForm);

  // Confirmar exclusão
  $('#btnConfirmExcluir').on('click', executarExclusao);

  // Atalhos
  $(document).on('keydown', handleShortcuts);
}

// ======== Util: debounce ========
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// ======== Busca global ========
function applyGlobalSearch() {
  const q = $('#globalSearch').val().toLowerCase().trim();

  filteredData = !q
    ? [...currentData]
    : currentData.filter(item =>
        ['id_resp_regiao','regional','usuario','ano_ref'].some(k =>
          String(item[k]).toLowerCase().includes(q)
        )
      );

  currentPage = 1;
  updatePagination();
  renderTable();
}

// ======== Filtros por coluna ========
function applyColumnFilter(event) {
  const col = $(event.target).data('filter');
  const val = $(event.target).val().toLowerCase().trim();

  if (!val) delete columnFilters[col];
  else columnFilters[col] = val;

  filteredData = currentData.filter(item => {
    for (const [c, v] of Object.entries(columnFilters)) {
      if (!String(item[c]).toLowerCase().includes(v)) return false;
    }
    return true;
  });

  currentPage = 1;
  updatePagination();
  renderTable();
}

// ======== Ordenação ========
function handleSort(event) {
  const column = $(event.target).data('sort');

  if (sortColumn === column) {
    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
  } else {
    sortColumn = column;
    sortDirection = 'asc';
  }

  // Ícones
  $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');
  $(event.target)
    .removeClass('fa-sort')
    .addClass(`fa-sort-${sortDirection === 'asc' ? 'up' : 'down'}`);

  // Conversões para tipo correto
  filteredData.sort((a, b) => {
    let av = a[column];
    let bv = b[column];

    if (['id_resp_regiao','ano_ref'].includes(column)) {
      av = parseInt(av || '0', 10);
      bv = parseInt(bv || '0', 10);
    } else {
      av = String(av).toLowerCase();
      bv = String(bv).toLowerCase();
    }

    if (av < bv) return sortDirection === 'asc' ? -1 : 1;
    if (av > bv) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  renderTable();
}

// ======== Tamanho da página ========
function changePageSize() {
  pageSize = parseInt($('#pageSize').val(), 10);
  currentPage = 1;
  updatePagination();
  renderTable();
}

// ======== Renderização ========
function renderTable() {
  showLoading();

  setTimeout(() => {
    const $tbody = $('#tableBody');
    const start = (currentPage - 1) * pageSize;
    const end = start + pageSize;
    const pageData = filteredData.slice(start, end);

    $tbody.empty();

    pageData.forEach(item => {
      const $row = $(`
        <tr data-id="${item.id_resp_regiao}">
          <td data-column="id_resp_regiao">#${item.id_resp_regiao}</td>
          <td data-column="regional">${escapeHtml(item.regional)}</td>
          <td data-column="usuario">${escapeHtml(item.usuario)}</td>
          <td data-column="ano_ref">${escapeHtml(item.ano_ref)}</td>
          <td data-column="acoes">${item.acoes}</td>
        </tr>
      `);
      $tbody.append($row);
    });

    applyColumnVisibility();
    initializeTooltips();
    hideLoading();
  }, 150);
}

// ======== Paginação ========
function updatePagination() {
  const total = filteredData.length;
  const pages = Math.ceil(total / pageSize) || 1;

  const start = total ? (currentPage - 1) * pageSize + 1 : 0;
  const end = Math.min(currentPage * pageSize, total);

  $('#startRecord').text(start);
  $('#endRecord').text(end);
  $('#totalRecords').text(total);

  const $filteredInfo = $('#filteredInfo');
  const $originalTotal = $('#originalTotal');
  if (total < currentData.length) {
    $originalTotal.text(currentData.length);
    $filteredInfo.show();
  } else {
    $filteredInfo.hide();
  }

  const $p = $('#pagination').empty();

  if (pages <= 1) return;

  // anterior
  $p.append(
    $(`<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
         <a class="page-link" href="#">Anterior</a>
       </li>`).on('click', (e) => { e.preventDefault(); changePage(currentPage - 1); })
  );

  // páginas
  const sp = Math.max(1, currentPage - 2);
  const ep = Math.min(pages, currentPage + 2);
  for (let i = sp; i <= ep; i++) {
    $p.append(
      $(`<li class="page-item ${i === currentPage ? 'active' : ''}">
           <a class="page-link" href="#">${i}</a>
         </li>`).on('click', (e) => { e.preventDefault(); changePage(i); })
    );
  }

  // próximo
  $p.append(
    $(`<li class="page-item ${currentPage === pages ? 'disabled' : ''}">
         <a class="page-link" href="#">Próximo</a>
       </li>`).on('click', (e) => { e.preventDefault(); changePage(currentPage + 1); })
  );
}

function changePage(p) {
  const max = Math.ceil(filteredData.length / pageSize) || 1;
  if (p < 1 || p > max) return;
  currentPage = p;
  renderTable();
  updatePagination();
}

// ======== Colunas: visibilidade / seletor ========
function toggleColumnSelector() {
  $('#columnDropdown').toggle();
}

function toggleColumn(e) {
  const col = $(e.target).val();
  const show = $(e.target).is(':checked');
  $(`[data-column="${col}"]`).toggle(show);
  saveTableSettings();
}

function selectAllColumns() {
  $('.column-toggle').each(function () {
    $(this).prop('checked', true);
    $(`[data-column="${$(this).val()}"]`).show();
  });
  saveTableSettings();
}

function deselectAllColumns() {
  $('.column-toggle').each(function () {
    if ($(this).val() !== 'acoes') {
      $(this).prop('checked', false);
      $(`[data-column="${$(this).val()}"]`).hide();
    }
  });
  saveTableSettings();
}

function applyColumnVisibility() {
  $('.column-toggle').each(function () {
    const col = $(this).val();
    $(`[data-column="${col}"]`).toggle($(this).is(':checked'));
  });
}

// ======== Redimensionamento de colunas ========
function setupColumnResizing() {
  const $table = $('#respRegioesTable');
  let isResizing = false;
  let $current;
  let startX = 0;
  let startW = 0;

  $('.resize-handle').on('mousedown', function (e) {
    e.preventDefault();
    isResizing = true;
    $current = $(this).closest('th');
    startX = e.clientX;
    startW = parseInt($current.css('width'), 10);

    $(document).on('mousemove', onResize);
    $(document).on('mouseup', stopResize);

    $('body').css('cursor', 'col-resize');
    $table.css('user-select', 'none');
  });

  function onResize(e) {
    if (!isResizing) return;
    const w = startW + (e.clientX - startX);
    if (w > 60) {
      $current.css({ width: `${w}px`, 'min-width': `${w}px` });
    }
  }

  function stopResize() {
    isResizing = false;
    $('body').css('cursor', '');
    $table.css('user-select', '');
    $(document).off('mousemove', onResize).off('mouseup', stopResize);
  }
}

// ======== Exportação ========
function toggleExportMenu() {
  $('#exportMenu').toggle();
}

function exportData(format) {
  const data = filteredData.map(x => ({
    ID: x.id_resp_regiao,
    Regional: x.regional,
    Usuário: x.usuario,
    Ano: x.ano_ref
  }));

  if (!data.length) return;

  switch (format) {
    case 'csv': exportToCSV(data); break;
    case 'excel': exportToExcel(data); break;
    case 'pdf': exportToPDF(data); break;
  }

  $('#exportMenu').hide();
}

function exportToCSV(data) {
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(r => headers.map(h => `"${String(r[h]).replace(/"/g,'""')}"`).join(','))
  ].join('\n');
  downloadFile(csv, 'resp_regioes.csv', 'text/csv');
}

function exportToExcel(data) {
  // fallback simples como CSV (para Excel)
  const headers = Object.keys(data[0]);
  const csv = [
    headers.join(','),
    ...data.map(r => headers.map(h => `"${String(r[h]).replace(/"/g,'""')}"`).join(','))
  ].join('\n');
  downloadFile(csv, 'resp_regioes.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
}

function exportToPDF(data) {
  // fallback em texto (para implementar com jsPDF depois)
  const headers = Object.keys(data[0]);
  let content = 'RESPONSÁVEIS POR REGIÃO (por ano)\n\n';
  content += headers.join('\t') + '\n';
  content += '='.repeat(80) + '\n';
  data.forEach(r => content += headers.map(h => r[h]).join('\t') + '\n');
  downloadFile(content, 'resp_regioes.pdf', 'application/pdf');
}

function downloadFile(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ======== Utilidades ========
function showLoading() { $('#loadingOverlay').show(); }
function hideLoading() { $('#loadingOverlay').hide(); }

function clearAllFilters() {
  $('#globalSearch').val('');
  $('.filter-input').val('');
  columnFilters = {};
  filteredData = [...currentData];
  currentPage = 1;

  sortColumn = '';
  sortDirection = 'asc';
  $('.sort-icon').removeClass('fa-sort-up fa-sort-down').addClass('fa-sort');

  updatePagination();
  renderTable();
}

function refreshData() {
  // Simples: recarrega a página
  location.reload();
}

function closeDropdowns(e) {
  if (!$(e.target).closest('.column-selector').length) $('#columnDropdown').hide();
  if (!$(e.target).closest('.export-dropdown').length) $('#exportMenu').hide();
}

function initializeTooltips() {
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    $('[data-bs-toggle="tooltip"]').each(function () {
      new bootstrap.Tooltip(this);
    });
  }
}

function handleShortcuts(e) {
  if (e.ctrlKey && e.key === 'f') { e.preventDefault(); $('#globalSearch').focus(); }
  if (e.key === 'Escape') { clearAllFilters(); }
  if (e.ctrlKey && e.key === 'r') { e.preventDefault(); refreshData(); }
}

// ======== Persistência de preferências ========
function saveTableSettings() {
  const settings = {
    pageSize: parseInt($('#pageSize').val(), 10) || pageSize,
    columnVisibility: {}
  };
  $('.column-toggle').each(function () {
    settings.columnVisibility[$(this).val()] = $(this).is(':checked');
  });
  try { localStorage.setItem('respRegioesTableSettings', JSON.stringify(settings)); } catch (_) {}
}

function loadTableSettings() {
  try {
    const s = JSON.parse(localStorage.getItem('respRegioesTableSettings') || '{}');
    if (s.pageSize) { pageSize = s.pageSize; $('#pageSize').val(pageSize); }
    if (s.columnVisibility) {
      $.each(s.columnVisibility, (col, vis) => {
        const $cb = $(`#col-${col}`);
        if ($cb.length) {
          $cb.prop('checked', vis);
          $(`[data-column="${col}"]`).toggle(vis);
        }
      });
    }
  } catch (_) {}
}

$('#pageSize').on('change', saveTableSettings);
$('.column-toggle').on('change', saveTableSettings);

// ======== Helpers para modal Criar/Editar/Excluir ========
function abrirModalCriar() {
  $('#respModalTitle').text('Novo vínculo');
  $('#registro_id').val('');
  $('#id_regional').val('');
  $('#id_usuario').val('');
  $('#ano_ref').val('');
  $('#respForm .btn-loading').addClass('d-none');
  $('#respForm .btn-text').removeClass('d-none');
  new bootstrap.Modal($('#respModal')[0]).show();
}

function abrirModalEditar({ id, id_regional, id_usuario, ano_ref }) {
  $('#respModalTitle').text('Editar vínculo');
  $('#registro_id').val(id);
  $('#id_regional').val(String(id_regional));
  $('#id_usuario').val(String(id_usuario));
  $('#ano_ref').val(String(ano_ref));
  $('#respForm .btn-loading').addClass('d-none');
  $('#respForm .btn-text').removeClass('d-none');
  new bootstrap.Modal($('#respModal')[0]).show();
}

let idParaExcluir = null;
function confirmarExclusao(id) {
  idParaExcluir = id;
  new bootstrap.Modal($('#confirmModal')[0]).show();
}

async function executarExclusao() {
  if (!idParaExcluir) return;

  try {
    const url = `/resp_regioes/${idParaExcluir}/excluir`;
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    });

    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.message || 'Erro ao excluir');

    // Remove linha da tabela em memória e DOM
    currentData = currentData.filter(x => String(x.id_resp_regiao) !== String(idParaExcluir));
    applyGlobalSearch(); // reaplica filtros/atualiza tela

    showToast(data.message || 'Vínculo excluído.');
  } catch (err) {
    showToast(err.message || 'Erro de comunicação.', true);
  } finally {
    idParaExcluir = null;
    bootstrap.Modal.getInstance($('#confirmModal')[0]).hide();
  }
}

async function submitRespForm(e) {
  e.preventDefault();

  // Validação simples
  const id_regional = $('#id_regional').val();
  const id_usuario = $('#id_usuario').val();
  const ano_ref = $('#ano_ref').val();
  if (!id_regional || !id_usuario || !ano_ref) {
    $('#id_regional, #id_usuario, #ano_ref').each(function () {
      this.classList.toggle('is-invalid', !this.value);
    });
    return;
  }
  $('#id_regional, #id_usuario, #ano_ref').removeClass('is-invalid');

  // UI loading
  $('#respForm .btn-text').addClass('d-none');
  $('#respForm .btn-loading').removeClass('d-none');

  const id = $('#registro_id').val().trim();
  const url = id ? `/resp_regioes/${id}/editar` : `/resp_regioes/criar`;

  try {
    const fd = new FormData(document.getElementById('respForm'));
    const resp = await fetch(url, {
      method: 'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body: fd
    });
    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.message || 'Erro ao salvar');

    // Recarrega a página para consistência de server-state
    location.reload();
  } catch (err) {
    showToast(err.message || 'Erro de comunicação.', true);
  } finally {
    $('#respForm .btn-loading').addClass('d-none');
    $('#respForm .btn-text').removeClass('d-none');
  }
}

// ======== Toast ========
function showToast(msg, isError = false) {
  const $toast = $('#mainToast');
  $('#toastBody').text(msg);
  $toast.removeClass('text-bg-dark text-bg-danger')
        .addClass(isError ? 'text-bg-danger' : 'text-bg-dark');
  new bootstrap.Toast($toast[0]).show();
}

// ======== Helpers ========
function escapeHtml(s) {
  return String(s)
    .replaceAll('&','&amp;')
    .replaceAll('<','&lt;')
    .replaceAll('>','&gt;')
    .replaceAll('"','&quot;')
    .replaceAll("'",'&#039;');
}
