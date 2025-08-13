from web_app import *
from forms2 import *
from db import *


@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_documento():
    form = DocumentoForm()

    if form.validate_on_submit():
        try:
            # Processar upload do arquivo
            file = form.arquivo.data
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Upload para OneDrive
            onedrive_url = upload_to_onedrive(file_path, filename)

            # Salvar no banco de dados
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()

                insert_query = """
                    INSERT INTO orcamento.documentos 
                    (protocolo, num_doc, nome_cliente, cnpj, instalacao, tipo_viab, tipo_analise, 
                     tipo_pedido, dem_fp_ant, dem_p_ant, dem_fp_dep, dem_p_dep, municipio, 
                     latitude_x, longitude_y, area_resp, elaborador_doc, eng_responsavel, 
                     arquivo_url, arquivo_nome)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                cursor.execute(insert_query, (
                    form.protocolo.data, form.num_doc.data, form.nome_cliente.data,
                    form.cnpj.data, form.instalacao.data, form.tipo_viab.data,
                    form.tipo_analise.data, form.tipo_pedido.data, form.dem_fp_ant.data,
                    form.dem_p_ant.data, form.dem_fp_dep.data, form.dem_p_dep.data,
                    form.municipio.data, form.latitude_x.data, form.longitude_y.data,
                    form.area_resp.data, form.elaborador_doc.data, form.eng_responsavel.data,
                    onedrive_url, filename
                ))

                conn.commit()
                conn.close()

            # Remover arquivo temporário
            os.remove(file_path)

            flash('Documento cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_documentos'))

        except Exception as e:
            flash(f'Erro ao cadastrar documento: {str(e)}', 'error')

    return render_template('cadastrar.html', form=form)