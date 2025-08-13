from web_app import *
from forms2 import *
from db import *

@app.route('/api/protocolo/<protocolo>')
def get_documento_by_protocolo(protocolo):
    """API endpoint para buscar documento por protocolo"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()

            query = """
                SELECT d.*, s.status, s.dt_criacao, s.dt_concl, s.dt_transgressao, s.dt_fim
                FROM orcamento.documentos d
                LEFT JOIN orcamento.status_documentos s ON d.protocolo = s.protocolo
                WHERE d.protocolo = ?
            """

            cursor.execute(query, (protocolo,))
            result = cursor.fetchone()
            conn.close()

            if result:
                columns = [column[0] for column in cursor.description]
                documento = dict(zip(columns, result))
                return jsonify(documento)
            else:
                return jsonify({'error': 'Documento não encontrado'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500