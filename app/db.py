import pyodbc
from flask import current_app, g

# Configurações do banco de dados SQL Server
DATABASE_CONFIG = {
    'server': 'edpbredb.database.windows.net',
    'database': 'ddpe',
    'username': 'usrDdpe',
    'password': '27caPt7cdkdN@t7&',
    'driver': '{ODBC Driver 17 for SQL Server}'
}


def get_db_connection():
    """Estabelece conexão com SQL Server"""

    try:
        if 'db' not in g:
            connection_string = f"DRIVER={DATABASE_CONFIG['driver']};SERVER={DATABASE_CONFIG['server']};DATABASE={DATABASE_CONFIG['database']};UID={DATABASE_CONFIG['username']};PWD={DATABASE_CONFIG['password']}"
            g.db = pyodbc.connect(connection_string)
            g.cursor = g.db.cursor()
        return g.db
    except Exception as e:
        print(f"Erro na conexão com o banco: {e}")
        return None


def dict_cursor(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_database():
    """Inicializa as tabelas no banco de dados"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Criar tabela de documentos
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='documentos' AND xtype='U')
                CREATE TABLE orcamento.documentos (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    protocolo varchar(50) NOT NULL,
                    num_doc varchar(50) NOT NULL,
                    nome_cliente varchar(255) NOT NULL,
                    cnpj varchar(18) NOT NULL,
                    instalacao varchar(255) NOT NULL,
                    tipo_viab varchar(50),
                    tipo_analise varchar(50),
                    tipo_pedido varchar(50),
                    dem_fp_ant float,
                    dem_p_ant float,
                    dem_fp_dep float,
                    dem_p_dep float,
                    municipio varchar(100) NOT NULL,
                    latitude_x float,
                    longitude_y float,
                    area_resp varchar(50),
                    elaborador_doc varchar(100) NOT NULL,
                    eng_responsavel varchar(100) NOT NULL,
                    arquivo_url varchar(500),
                    arquivo_nome varchar(255),
                    data_cadastro datetime DEFAULT GETDATE()
                )
            """)

            # Criar tabela de status
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='status_documentos' AND xtype='U')
                CREATE TABLE orcamento.status_documentos (
                    id int IDENTITY(1,1) PRIMARY KEY,
                    protocolo varchar(50) NOT NULL,
                    dt_criacao date,
                    dt_concl date,
                    dt_transgressao date,
                    status varchar(50),
                    dt_fim date,
                    data_atualizacao datetime DEFAULT GETDATE()
                )
            """)

            conn.commit()
            print("Tabelas criadas com sucesso!")

        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()

