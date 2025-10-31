
$(document).ready(function () {
    const $tipoViab = $('#tipo_viab');
    const $tipoAnalise = $('#tipo_analise');
    const $tipoPedido = $('#tipo_pedido');

    // Valores previamente selecionados (vindos do Flask)
    const selectedViab = $tipoViab.data('selected');
    const selectedAnalise = $tipoAnalise.data('selected');
    const selectedPedido = $tipoPedido.data('selected');

    // === 1. Atualização do tipo_analise ===
    $tipoViab.on('change', function () {
        const viabilidade = $(this).val();
        if (viabilidade) {
            $.get('/api/tipo_analises/' + viabilidade, function (data) {
                $tipoAnalise.empty().append('<option value="">Selecione um tipo...</option>');
                $.each(data, function (index, analise) {
                    const isSelected = analise === selectedAnalise ? 'selected' : '';
                    $tipoAnalise.append('<option value="' + analise + '" ' + isSelected + '>' + analise + '</option>');
                });

                // Dispara mudança automática se for recarregamento pós-erro
                if (selectedAnalise) $tipoAnalise.trigger('change');
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
        if (analise) {
            $.get('/api/tipo_pedidos/' + viabilidade + '/' + analise, function (data) {
                $tipoPedido.empty().append('<option value="">Selecione um tipo...</option>');
                $.each(data, function (index, pedido) {
                    const isSelected = pedido.id == selectedPedido ? 'selected' : '';
                    $tipoPedido.append('<option value="' + pedido.id + '" ' + isSelected + '>' + pedido.pedido + '</option>');
                });
            });
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
});