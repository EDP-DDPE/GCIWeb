(function waitForJQuery() {
    if (typeof window.jQuery === 'undefined') {
        return setTimeout(waitForJQuery, 50);
    }
    $(document).ready(function() {

        // Inicializa Select2 apenas uma vez, com configurações corretas
        function initSelect2(selector) {
            const $select = $(selector);

            // Marca como inicialização manual
            $select.addClass('select2-manual-init');

            // Destroi instância anterior se existir
            if ($select.data('select2')) {
                $select.select2('destroy');
            }

            // Inicializa com configurações adequadas
            $select.select2({
                dropdownParent: $('#alternativaModal'),
                width: '100%',
                theme: 'bootstrap-5',
                placeholder: 'Selecione uma opção',
                allowClear: true,
                dropdownAutoWidth: false,
                dropdownCssClass: 'select2-dropdown-below' // força dropdown abaixo
            });
        }

        // Inicializa os selects
        initSelect2('#circuito_select');
        initSelect2('#letra_select');

        // Comportamento ao abrir o dropdown - ajusta scroll do modal
        $('#letra_select, #circuito_select').on('select2:opening', function (e) {
          const $el = $(this);
          const $modalBody = $('#alternativaModal .modal-body');

          // Pequeno delay para garantir que o DOM está pronto
          setTimeout(function() {
              const elTop = $el.offset().top - $modalBody.offset().top + $modalBody.scrollTop();
              const targetScroll = Math.max(elTop - 120, 0);

              // Scroll suave do modal body
              $modalBody.stop(true).animate({
                  scrollTop: targetScroll
              }, 150);
          }, 10);
        });

        // Libera scroll quando fechar o dropdown
        $('#letra_select, #circuito_select').on('select2:close', function () {
            $('body').css('overflow', '');
            $('#alternativaModal').css('overflow-y', 'auto');
        });



        $(document).on('mousedown', '.select2-container--open .select2-results__option', function (e) {
            e.stopPropagation();
        });

        $(document).on('mousedown', '.btn-alternativa-edit', function() {
            $(this).addClass('active'); // efeito visual Bootstrap
        });
        $(document).on('mouseup mouseleave', '.btn-alternativa-edit', function() {
            $(this).removeClass('active');
        });

        $('#subgrupo_select').change(function() {
            atualiza_circuitos()
            atualiza_ERD()
        });

        $('#flag_carga').change(function() {
            atualiza_ERD()
        });

        $('#flag_geracao').change(function() {
            atualiza_ERD()
        });

        var dropZone = $('#drop_zone');
        var fileInput = $('#imagem_alternativa');
        var preview = $('#preview_imagem');
        var uploadedFile = null;

        // Clique na área abre o file input
        dropZone.on('click', function() {
            fileInput.click();
        });

        // Seleção via file input
        fileInput.on('change', function(e) {
            handleFiles(this.files);
        });

        // Drag & Drop
        dropZone.on('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.css('background-color', '#e9ecef');
        });

        dropZone.on('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.css('background-color', '');
        });

        dropZone.on('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            dropZone.css('background-color', '');
            var files = e.originalEvent.dataTransfer.files;
            handleFiles(files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                var file = files[0];
                if (!file.type.startsWith('image/')) {
                    alert('Apenas imagens são permitidas!');
                    return;
                }

                // define o arquivo no input file do WTForms
                var fileInput = document.getElementById('imagem_alternativa');
                var dataTransfer = new DataTransfer(); // necessário para setar arquivos
                dataTransfer.items.add(file);
                fileInput.files = dataTransfer.files;

                // pré-visualização
                var reader = new FileReader();
                reader.onload = function(e) {
                    $('#preview_imagem').attr('src', e.target.result).show();
                }
                reader.readAsDataURL(file);
            }
        }

        $(document).on('click', '.btn-alternativa-edit', function() {

            var modo = $(this).data('mode');
            var id = $(this).data('id');
            var id_estudo = $('#id_estudo').val();

            // sempre esconde antes de abrir
            $('#btnExcluirAlternativa').hide();

            // Mostra loading
            $('#loadingOverlay').fadeIn(150);

             if (modo === 'editar') {
                $('#btnExcluirAlternativa').show().data('id', id);
             }

            // Limpa o formulário antes de usar
            $('#formAlternativa')[0].reset();
            $('#preview_imagem').hide().attr('src', '');
            $('#imagem_alternativa').val('');

            // Define o título e comportamento
            console.log(modo)
            if (modo != 'editar' & modo !='visualizar') {
            }
            else {
                // Busca os dados no servidor
                $.get('/alternativas/' + id, function(data) {
                    // Preenche os campos (use os IDs ou names conforme o seu form)
                    const circuitoSelect = $('#circuito_select');

                    const etapaSelect = $('#etapa_select')

                    const circuitoValue = data.id_circuito ? data.id_circuito.toString() : '';



                    if (circuitoValue) {
                        circuitoSelect.val(circuitoValue).trigger('change.select2');
                        if (circuitoSelect.val() !== circuitoValue) {
                            // força seleção mesmo se WTForms renderizou como int
                            circuitoSelect.find('option').each(function() {
                                if (parseInt($(this).val()) === parseInt(circuitoValue)) {
                                    $(this).prop('selected', true);
                                }
                            });
                        }
                    }

                    const letraSelect = $('#letra_select');
                    const letraValue = (data.letra_alternativa || '').toString().trim();
                    if (letraValue && letraSelect.find(`option[value="${letraValue}"]`).length) {
                        letraSelect.val(letraValue).trigger('change.select2');
                    } else {
                        letraSelect.prop('selectedIndex', 0).trigger('change.select2');
                    }

                    const subgrupoSelect = $('#subgrupo_select');
                    const subgrupoValue = (data.subrupo_tarifario || '').toString().trim();
                    if (subgrupoValue && subgrupoSelect.find(`option[value="${subgrupoValue}"]`).length) {
                        subgrupoSelect.val(subgrupoValue).trigger('change.select2');
                    } else {
                        subgrupoSelect.prop('selectedIndex', 0).trigger('change.select2');
                    }

                    $('#ERD').val(data.ERD ? data.ERD : 0);
                    $('#dem_p_antes').val(data.dem_p_ant ? data.dem_p_ant : 0.00);
                    $('#dem_p_depois').val(data.dem_p_dep ? data.dem_p_dep : 0.00);
                    $('#dem_fp_antes').val(data.dem_fp_ant ? data.dem_fp_ant : 0.00);
                    $('#dem_fp_depois').val(data.dem_fp_dep ? data.dem_fp_dep : 0.00);
                    $('#dem_disponivel').val(data.demanda_disponivel_ponto ? data.demanda_disponivel_ponto : 0.00);
                    $('#descricao').val(data.descricao);
                    $('#observacao').val(data.observacao);
                    $('#flag_carga').prop('checked', data.flag_carga);
                    $('#flag_geracao').prop('checked', data.flag_geracao);
                    $('#flag_fluxo_reverso').prop('checked', data.flag_fluxo_reverso);
                    $('#flag_menor_custo_global').prop('checked', data.flag_menor_custo_global);
                    $('#flag_alternativa_escolhida').prop('checked', data.flag_alternativa_escolhida);
                    $('#custo_modular').val(data.custo_modular ? data.custo_modular : 0.00);

                    $('#id_estudo').val(data.id_estudo);

                    // Imagem
                    if (data.imagem_base64) {
                        $('#preview_imagem').attr('src', 'data:image/jpeg;base64,' + data.imagem_base64).show();
                    } else {
                        $('#preview_imagem').hide();
                    }

                    // Modo editar ou visualizar
                    if (modo === 'editar') {
                        $('#alternativaModalLabel').text('Editar Alternativa');
                        $('#formAlternativa').attr('action', '/alternativas/' + id);
                        $('#formAlternativa input, #formAlternativa textarea, #formAlternativa select').prop('disabled', false);
                        $('.btn-primary', '#alternativaModal').show();
                    } else {
                        $('#alternativaModalLabel').text('Visualizar Alternativa');
                        $('#salvar_alternativa', '#alternativaModal').hide();
                        $('#formAlternativa input, #formAlternativa textarea, #formAlternativa select').prop('disabled', true);
                    }

                    $('#loadingOverlay').fadeOut(200, function() {
                            $('#alternativaModal').modal('show');
                    });
                })
                .fail(function(xhr) {
                        $('#loadingOverlay').fadeOut(200);
                        alert('Erro ao carregar dados: ' + xhr.responseText);
                    });
            }
        });

        $('#alternativaModal').on('hide.bs.modal', function () {
            // Remove foco de qualquer elemento dentro do modal
            document.activeElement?.blur();
        });

        // === Evento de exclusão ===
        $('#btnExcluirAlternativa').on('click', function() {
            var id = $(this).data('id');

            if (!id) {
                alert('Nenhuma alternativa selecionada.');
                return;
            }

            // Confirmação
            if (!confirm('Tem certeza que deseja excluir esta alternativa? Essa ação não poderá ser desfeita.')) {
                return;
            }

            // Requisição AJAX
            $.ajax({
                url: '/alternativas/excluir/' + id,
                type: 'DELETE',
                success: function(resp) {
                    alert('Alternativa excluída com sucesso!');
                    $('#alternativaModal').modal('hide');
                    location.reload();
                },
                error: function(xhr) {
                    console.error(xhr.responseText);
                    alert('Erro ao excluir alternativa: ' + xhr.responseText);
                }
            });
        });

        const cleaveERD = new Cleave('#ERD', {
          numeral: true,
          numeralThousandsGroupStyle: 'thousand',
          prefix: 'R$ ',
          numeralDecimalMark: ',',
          delimiter: '.'
        });

        function atualiza_circuitos() {
            const subgrupo = $('#subgrupo_select').val();
            const id_edp = $('#id_edp').val(); // ou pegue via $('#id_edp').val() se o JS for externo
            const circuitoSelect = $('#circuito_select');
            const circuitoValue = circuitoSelect.val()

            if (!subgrupo) {
                console.warn("Nenhum subgrupo selecionado.");
                return;
            }

            // Exibe o loading no select
            circuitoSelect
                .empty()
                .append('<option disabled selected>Carregando circuitos...</option>')
                .prop('disabled', true);

            // Cria ou mostra o spinner ao lado (opcional)
            const spinner = $('<div class="spinner-border text-primary ms-2" role="status" style="width: 1.2rem; height: 1.2rem;"><span class="visually-hidden">Carregando...</span></div>');
            circuitoSelect.parent().append(spinner);

            $.get(`/api/circuitos/${id_edp}/${subgrupo}`)
                .done(function(response) {
                    circuitoSelect.empty().append('<option value="">Selecione um circuito...</option>');

                    if (!response.circuitos || response.circuitos.length === 0) {
                        circuitoSelect.append('<option disabled>Nenhum circuito encontrado</option>');
                    } else {
                        response.circuitos.forEach(c => {
                            circuitoSelect.append(`<option value="${c.id}">${c.nome}</option>`);
                        });
                        circuitoSelect.val(circuitoValue).trigger('change');
                    }
                })
                .fail(function(xhr, status, error) {
                    console.error("Erro ao carregar circuitos:", error);
                    circuitoSelect.empty().append('<option disabled>Erro ao carregar circuitos</option>');
                })
                .always(function() {
                    // Remove o spinner e reabilita o select
                    spinner.remove();
                    circuitoSelect.prop('disabled', false);
                });
        }

        function atualiza_ERD() {

            var subgrupo = $('#subgrupo_select').val();
            var dem_p_antes = parseFloat($('#dem_p_antes').val().replace(',', '.'));
            var dem_fp_antes = parseFloat($('#dem_fp_antes').val().replace(',', '.'));
            var dem_p_depois = parseFloat($('#dem_p_depois').val().replace(',', '.'));
            var dem_fp_depois = parseFloat($('#dem_fp_depois').val().replace(',', '.'));
            var carga_flegada = $('#flag_carga').is(':checked');
            var geracao_flegada = $('#flag_geracao').is(':checked');
            var tipo;

            const estudoIdEdp = document.getElementById('estudo_dados').dataset.idEdp;
            const dataAbertura = document.getElementById('estudo_dados').dataset.dataAbertura;


            if (!carga_flegada && !geracao_flegada){
                cleaveERD.setRawValue(0);
                return;
            }

            tipo = carga_flegada ? 1 : 0;

            var dif_p = dem_p_depois - dem_p_antes;
            var dif_fp = dem_fp_depois - dem_fp_antes;
            var maior_demanda = Math.max(dif_p, dif_fp);

            try {
                $.get(`/api/fator_k/${estudoIdEdp}/${subgrupo}/${dataAbertura}/${tipo}`, function(data) {
                    var valor = data.k * maior_demanda;
                    cleaveERD.setRawValue(valor);  // número puro, Cleave vai formatar
                });
            } catch (err) {
                console.error("Erro ao calcular ERD:", err);
            }
        }
    }); // fecha document.ready
})(); // fecha função de espera