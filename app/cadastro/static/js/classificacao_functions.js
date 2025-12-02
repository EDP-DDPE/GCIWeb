
$(document).ready(function () {
    const $tipoViab = $('#tipo_viab');
    const $tipoAnalise = $('#tipo_analise');
    const $tipoPedido = $('#tipo_pedido');
    const $tipoGeracao = $('#tipo_geracao');

    // 🔹 Função auxiliar para mostrar o "loading" dentro do select
    function showLoading($select, text = "Carregando...") {
        $select.prop('disabled', true)
               .empty()
               .append(`<option>${text}</option>`);
    }

    // Valores previamente selecionados (vindos do Flask)
    const selectedViab = $tipoViab.data('selected');
    const selectedAnalise = $tipoAnalise.data('selected');
    const selectedPedido = $tipoPedido.data('selected');
    const selectedGeracao = $tipoGeracao.data('selected');

    if (selectedGeracao) {
        mostrarTipoGeracao();
    } else {
        $tipoGeracao.val("");
        esconderTipoGeracao();
    }

    // === 1. Atualização do tipo_analise ===
    $tipoViab.on('change', function () {
        const viabilidade = $(this).val();

                // Resetar os selects dependentes
        $tipoAnalise.prop('disabled', true).empty().append('<option>Selecione um tipo...</option>');
        $tipoPedido.prop('disabled', true).empty().append('<option>Selecione um tipo...</option>');
        $tipoGeracao.val("");
        esconderTipoGeracao();


        if (viabilidade) {
            showLoading($tipoAnalise);
            $.get('/api/tipo_analises/' + viabilidade, function (data) {

                $tipoAnalise.empty().append('<option value="">Selecione um tipo...</option>');
                $.each(data, function (index, analise) {
                    const isSelected = analise === selectedAnalise ? 'selected' : '';
                    $tipoAnalise.append('<option value="' + analise + '" ' + isSelected + '>' + analise + '</option>');
                });

                // Dispara mudança automática se for recarregamento pós-erro
                if (selectedAnalise) $tipoAnalise.trigger('change');
            }).fail(function() {
                $tipoAnalise.empty().append('<option>Erro ao carregar tipos</option>');
            }).always(function() {
                $tipoAnalise.prop('disabled', false);
                $tipoPedido.prop('disabled', true).empty().append('<option>Selecione um tipo...</option>');
            });
        } else {
            $tipoAnalise.empty().append('<option value="">Selecione um tipo...</option>');
            $tipoPedido.empty().append('<option value="">Selecione um tipo...</option>');
        }
    });

    // === 2. Atualização do tipo_pedido ===
    $tipoAnalise.on('change', function () {
        const analise = $(this).val();
        const viabilidade = $tipoViab.val();


        $tipoPedido.prop('disabled', true).empty().append('<option>Selecione um tipo..</option>');
        $tipoGeracao.val("");
        esconderTipoGeracao();



        if (analise) {
            showLoading($tipoPedido, "Carregando tipos...");
            $.get('/api/tipo_pedidos/' + viabilidade + '/' + analise, function (data) {
                $tipoPedido.empty().append('<option value="">Selecione um tipo...</option>');
                $.each(data, function (index, pedido) {
                    const isSelected = pedido.id == selectedPedido ? 'selected' : '';
                    $tipoPedido.append('<option value="' + pedido.id + '" ' + isSelected + '>' + pedido.pedido + '</option>');
                });
            }).fail(function() {
                $tipoPedido.empty().append('<option>Erro ao carregar tipos</option>');
            }).always(function() {
                $tipoPedido.prop('disabled', false);
            });

            if (analise != 'Carga') {
                mostrarTipoGeracao();
            } else
                {esconderTipoGeracao();}

        } else {
            $tipoPedido.empty().append('<option value="">Selecione um tipo...</option>');
        }
    });

    // Bloco para repopular a aba Classificação automaticamente
    let atualizou = false;

    $('#classificacao-tab, #observacoes-tab').one('shown.bs.tab', function () {
        Atualizar()
    });

    function Atualizar() {
        if (atualizou) return;
        atualizou = true;
        const $btn = $(this);
        const $icon = $btn.find('i');

        $btn.prop('disabled', true);
        $icon.addClass('fa-spin');

        $tipoViab.trigger('change');;

        setTimeout(() => {
            $btn.prop('disabled', false);
            $icon.removeClass('fa-spin');
        }, 1000);
    };
    // Fim do Bloco para repopular a aba Classificação automaticamente

    function esconderTipoGeracao() {
        $("#divTipoGeracao").hide();

        $(".campo-classificacao")
            .removeClass("col-md-3")
            .addClass("col-md-4");
    }

    function mostrarTipoGeracao() {
        $("#divTipoGeracao").show();

        $(".campo-classificacao")
            .removeClass("col-md-4")
            .addClass("col-md-3");
    }
});