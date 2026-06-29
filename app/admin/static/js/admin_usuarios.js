// Administração de usuários + histórico de atividades
(function () {
    "use strict";

    const PERMISSOES = ['admin', 'visualizar', 'criar', 'editar', 'deletar', 'aprovar', 'bloqueado'];

    const ACOES_LABEL = {
        login: 'Login',
        logout: 'Logout',
        criar_estudo: 'Cadastrou estudo',
        editar_estudo: 'Editou estudo',
        excluir_estudo: 'Excluiu estudo',
        anexar_arquivo: 'Anexou arquivo',
        baixar_arquivo: 'Baixou arquivo',
        ia_cadastro: 'Cadastro via IA',
        criar_usuario: 'Criou usuário',
        editar_usuario: 'Editou usuário',
    };

    const ACOES_COR = {
        login: 'success', logout: 'secondary',
        criar_estudo: 'primary', editar_estudo: 'warning', excluir_estudo: 'danger',
        anexar_arquivo: 'info', baixar_arquivo: 'info', ia_cadastro: 'primary',
        criar_usuario: 'primary', editar_usuario: 'warning',
    };

    let modalUsuario;

    $(document).ready(function () {
        modalUsuario = new bootstrap.Modal(document.getElementById('modalUsuario'));

        // ---------- Usuários ----------
        $('#buscaUsuario').on('input', function () {
            const termo = $(this).val().toLowerCase().trim();
            $('#tabelaUsuarios tr').each(function () {
                const alvo = $(this).data('busca') || '';
                $(this).toggle(String(alvo).indexOf(termo) !== -1);
            });
        });

        $('#btnNovoUsuario').on('click', abrirModalNovo);
        $('.btn-editar-usuario').on('click', function () {
            abrirModalEditar($(this).data('id'));
        });

        $('#formUsuario').on('submit', salvarUsuario);

        // ---------- Histórico ----------
        $('#btnFiltrarLogs').on('click', function () { carregarLogs(1); });
        $('#filtroBusca').on('keypress', function (e) {
            if (e.which === 13) carregarLogs(1);
        });
        $('#tab-historico-btn').on('shown.bs.tab', function () {
            if (!$('#tabelaLogs').data('carregado')) carregarLogs(1);
        });

        // ---------- Circuitos ----------
        $('#btnAtualizarCircuitos').on('click', atualizarCircuitos);
    });

    // ======================= CIRCUITOS =======================
    function atualizarCircuitos() {
        const $btn = $('#btnAtualizarCircuitos');
        const htmlOriginal = $btn.html();
        $btn.prop('disabled', true)
            .html('<span class="spinner-border spinner-border-sm me-1"></span> Sincronizando...');
        $('#circuitosResultado').addClass('d-none');

        $.ajax({
            url: '/admin/circuitos/atualizar',
            method: 'POST',
            timeout: 11 * 60 * 1000,   // > timeout do azcopy no servidor (10 min)
            success: function (resp) {
                const msg = (resp.circuitos != null)
                    ? resp.message + ' (' + resp.circuitos + ' circuitos)'
                    : resp.message;
                showToast(msg, 'success');
                mostrarResultadoCircuitos('success', msg, resp.saida);
            },
            error: function (xhr) {
                const r = xhr.responseJSON || {};
                const msg = r.message || 'Erro ao atualizar circuitos.';
                showToast(msg, 'error');
                mostrarResultadoCircuitos('danger', msg, r.saida);
            },
            complete: function () {
                $btn.prop('disabled', false).html(htmlOriginal);
            }
        });
    }

    function mostrarResultadoCircuitos(tipo, msg, saida) {
        $('#circuitosAlerta')
            .attr('class', 'alert mb-2 alert-' + tipo)
            .text(msg);
        $('#circuitosSaida').text(saida || '(sem saída do azcopy)');
        $('#circuitosResultado').removeClass('d-none');
    }

    // ======================= USUÁRIOS =======================
    function abrirModalNovo() {
        $('#formUsuario')[0].reset();
        $('#usuarioId').val('');
        $('#modalUsuarioTitulo').html('<i class="fas fa-user-plus me-2"></i>Novo Usuário');
        $('#campoMatricula').prop('disabled', false);
        modalUsuario.show();
    }

    function abrirModalEditar(id) {
        $.getJSON('/admin/usuarios/' + id + '/api', function (u) {
            $('#formUsuario')[0].reset();
            $('#usuarioId').val(u.id_usuario);
            $('#campoNome').val(u.nome);
            $('#campoMatricula').val(u.matricula);
            $('#campoEmail').val(u.email || '');
            $('#campoEdp').val(u.id_edp);
            PERMISSOES.forEach(function (p) {
                $('#perm_' + p).prop('checked', !!u[p]);
            });
            $('#modalUsuarioTitulo').html('<i class="fas fa-user-edit me-2"></i>Editar Usuário');
            modalUsuario.show();
        }).fail(function () {
            showToast('Erro ao carregar dados do usuário.', 'error');
        });
    }

    function salvarUsuario(e) {
        e.preventDefault();
        const id = $('#usuarioId').val();
        const payload = {
            nome: $('#campoNome').val().trim(),
            matricula: $('#campoMatricula').val().trim(),
            email: $('#campoEmail').val().trim(),
            id_edp: $('#campoEdp').val(),
        };
        PERMISSOES.forEach(function (p) {
            payload[p] = $('#perm_' + p).is(':checked');
        });

        const url = id ? '/admin/usuarios/' + id + '/editar' : '/admin/usuarios/adicionar';

        $.ajax({
            url: url,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function (resp) {
                showToast(resp.message, 'success');
                modalUsuario.hide();
                setTimeout(function () { window.location.reload(); }, 700);
            },
            error: function (xhr) {
                const msg = (xhr.responseJSON && xhr.responseJSON.message) || 'Erro ao salvar usuário.';
                showToast(msg, 'error');
            }
        });
    }

    // ======================= HISTÓRICO =======================
    function carregarLogs(page) {
        const params = {
            page: page || 1,
            per_page: 50,
            dias: $('#filtroDias').val(),
            matricula: $('#filtroUsuario').val(),
            acao: $('#filtroAcao').val(),
            q: $('#filtroBusca').val().trim(),
        };

        $('#tabelaLogs').html('<tr><td colspan="5" class="text-center text-muted py-4">Carregando...</td></tr>');

        $.getJSON('/admin/logs/api', params, function (data) {
            $('#tabelaLogs').data('carregado', true);
            renderLogs(data);
        }).fail(function () {
            $('#tabelaLogs').html('<tr><td colspan="5" class="text-center text-danger py-4">Erro ao carregar histórico.</td></tr>');
        });
    }

    function renderLogs(data) {
        const tbody = $('#tabelaLogs');
        tbody.empty();

        if (!data.logs || data.logs.length === 0) {
            tbody.html('<tr><td colspan="5" class="text-center text-muted py-4">Nenhuma atividade encontrada.</td></tr>');
            $('#logsInfo').text('0 registros');
            $('#logsPagination').empty();
            return;
        }

        data.logs.forEach(function (log) {
            const label = ACOES_LABEL[log.acao] || log.acao;
            const cor = ACOES_COR[log.acao] || 'secondary';
            const tr = $('<tr>');
            tr.append($('<td>').css('white-space', 'nowrap').text(formatarData(log.data)));
            tr.append($('<td>').text(log.nome || log.matricula || '—'));
            tr.append($('<td>').html('<span class="badge bg-' + cor + '">' + escapeHtml(label) + '</span>'));
            tr.append($('<td>').text(log.descricao || '—'));
            tr.append($('<td>').addClass('text-muted small').text(log.ip || '—'));
            tbody.append(tr);
        });

        const inicio = (data.page - 1) * data.per_page + 1;
        const fim = Math.min(data.page * data.per_page, data.total);
        $('#logsInfo').text('Exibindo ' + inicio + '–' + fim + ' de ' + data.total + ' registros');

        renderPaginacao(data);
    }

    function renderPaginacao(data) {
        const ul = $('#logsPagination');
        ul.empty();
        if (data.pages <= 1) return;

        function item(label, page, disabled, active) {
            const li = $('<li>').addClass('page-item');
            if (disabled) li.addClass('disabled');
            if (active) li.addClass('active');
            const a = $('<a>').addClass('page-link').attr('href', '#').html(label);
            if (!disabled && !active) {
                a.on('click', function (e) { e.preventDefault(); carregarLogs(page); });
            }
            li.append(a);
            return li;
        }

        ul.append(item('&laquo;', data.page - 1, data.page <= 1, false));

        const max = data.pages;
        let ini = Math.max(1, data.page - 2);
        let f = Math.min(max, ini + 4);
        ini = Math.max(1, f - 4);
        for (let p = ini; p <= f; p++) {
            ul.append(item(String(p), p, false, p === data.page));
        }

        ul.append(item('&raquo;', data.page + 1, data.page >= max, false));
    }

    // ======================= UTIL =======================
    function formatarData(iso) {
        if (!iso) return '—';
        const d = new Date(iso);
        if (isNaN(d.getTime())) return iso;
        const pad = function (n) { return String(n).padStart(2, '0'); };
        return pad(d.getDate()) + '/' + pad(d.getMonth() + 1) + '/' + d.getFullYear() +
            ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
    }

    function escapeHtml(s) {
        return String(s).replace(/[&<>"']/g, function (c) {
            return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
        });
    }
})();
