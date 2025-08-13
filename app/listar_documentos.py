from web_app import *
from forms2 import *
from db import *

@app.route('/listar')
def listar_documentos():
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            query = """
                SELECT d.*, s.status, s.dt_criacao, s.dt_concl, s.dt_fim
                FROM orcamento.documentos d
                LEFT JOIN orcamento.status_documentos s ON d.protocolo = s.protocolo
                ORDER BY d.data_cadastro DESC
            """

            cursor.execute(query)
            documentos = cursor.fetchall()
            conn.close()

            return render_template('listar.html', documentos=documentos)
    except Exception as e:
        flash(f'Erro ao carregar documentos: {str(e)}', 'error')
        return render_template('listar.html', documentos=[])
