from web_app import *
from forms2 import *
from db import *


@app.route('/status', methods=['GET', 'POST'])
def gerenciar_status():
    form = StatusForm()

    if form.validate_on_submit():
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()

                # Verificar se já existe registro para este protocolo
                cursor.execute("SELECT id FROM orcamento.status_documentos WHERE protocolo = ?",
                               (form.protocolo.data,))
                existing = cursor.fetchone()

                if existing:
                    # Atualizar registro existente
                    update_query = """
                        UPDATE orcamento.status_documentos 
                        SET dt_criacao = ?, dt_concl = ?, dt_transgressao = ?, 
                            status = ?, dt_fim = ?, data_atualizacao = GETDATE()
                        WHERE protocolo = ?
                    """
                    cursor.execute(update_query, (
                        form.dt_criacao.data, form.dt_concl.data, form.dt_transgressao.data,
                        form.status.data, form.dt_fim.data, form.protocolo.data
                    ))
                else:
                    # Inserir novo registro
                    insert_query = """
                        INSERT INTO orcamento.status_documentos 
                        (protocolo, dt_criacao, dt_concl, dt_transgressao, status, dt_fim)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(insert_query, (
                        form.protocolo.data, form.dt_criacao.data, form.dt_concl.data,
                        form.dt_transgressao.data, form.status.data, form.dt_fim.data
                    ))

                conn.commit()
                conn.close()

                flash('Status atualizado com sucesso!', 'success')
                return redirect(url_for('listar_documentos'))

        except Exception as e:
            flash(f'Erro ao atualizar status: {str(e)}', 'error')

    return render_template('status.html', form=form)
