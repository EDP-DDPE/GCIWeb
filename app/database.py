import os
import urllib.parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
import logging
from contextlib import contextmanager

# Configuração de logging para SQL Server
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class DatabaseConfig:
    """Configurações do banco de dados SQL Server"""
    
    # Configurações padrão - podem ser sobrescritas por variáveis de ambiente
    SERVER = os.getenv('SQLSERVER_HOST', '')
    PORT = os.getenv('SQLSERVER_PORT', '')
    DATABASE = os.getenv('SQLSERVER_DATABASE', '')
    USERNAME = os.getenv('SQLSERVER_USERNAME', '')
    PASSWORD = os.getenv('SQLSERVER_PASSWORD', '')
    DRIVER = os.getenv('SQLSERVER_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Configurações de conexão
    TRUST_SERVER_CERTIFICATE = os.getenv('TRUST_SERVER_CERTIFICATE', 'yes')
    ENCRYPT = os.getenv('SQLSERVER_ENCRYPT', 'no')
    CONNECTION_TIMEOUT = int(os.getenv('CONNECTION_TIMEOUT', '30'))
    COMMAND_TIMEOUT = int(os.getenv('COMMAND_TIMEOUT', '30'))
    
    # Pool de conexões
    POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', '20'))
    POOL_TIMEOUT = int(os.getenv('SQLALCHEMY_POOL_TIMEOUT', '30'))
    POOL_RECYCLE = int(os.getenv('SQLALCHEMY_POOL_RECYCLE', '3600'))  # 1 hora
    
    @classmethod
    def get_connection_string(cls):
        """Gera a string de conexão para SQL Server com pyodbc"""
        
        # Parâmetros da conexão
        params = {
            'driver': cls.DRIVER,
            'server': f'{cls.SERVER},{cls.PORT}',
            'database': cls.DATABASE,
            'uid': cls.USERNAME,
            'pwd': cls.PASSWORD,
            'TrustServerCertificate': cls.TRUST_SERVER_CERTIFICATE,
            'Encrypt': cls.ENCRYPT,
            'Connection Timeout': cls.CONNECTION_TIMEOUT,
            'Command Timeout': cls.COMMAND_TIMEOUT,
            'MARS_Connection': 'yes',  # Multiple Active Result Sets
            'ApplicationIntent': 'ReadWrite',
            'MultipleActiveResultSets': 'true'
        }
        
        # Monta a string de parâmetros
        conn_str = ';'.join([f'{k}={v}' for k, v in params.items()])
        
        # URL encode da string de conexão
        encoded_conn_str = urllib.parse.quote_plus(conn_str)
        
        # Retorna a URL SQLAlchemy
        return f'mssql+pyodbc:///?odbc_connect={encoded_conn_str}'
    
    @classmethod
    def get_sqlalchemy_config(cls):
        """Retorna configurações do SQLAlchemy otimizadas para SQL Server"""
        return {
            'SQLALCHEMY_DATABASE_URI': cls.get_connection_string(),
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SQLALCHEMY_ECHO': os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true',
            'SQLALCHEMY_RECORD_QUERIES': os.getenv('SQLALCHEMY_RECORD_QUERIES', 'False').lower() == 'true',
            'SQLALCHEMY_ENGINE_OPTIONS': {
                'poolclass': QueuePool,
                'pool_size': cls.POOL_SIZE,
                'max_overflow': cls.MAX_OVERFLOW,
                'pool_timeout': cls.POOL_TIMEOUT,
                'pool_recycle': cls.POOL_RECYCLE,
                'pool_pre_ping': True,  # Testa conexão antes de usar
                'connect_args': {
                    'check_same_thread': False,
                    'timeout': cls.CONNECTION_TIMEOUT
                },
                'execution_options': {
                    'autocommit': False,
                    'isolation_level': 'READ_COMMITTED'
                }
            }
        }

class DatabaseManager:
    """Gerenciador de conexão com SQL Server"""
    
    def __init__(self, app=None):
        self.app = app
        self.db = None
        self.engine = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Inicializa a aplicação Flask com as configurações do banco"""
        
        # Aplicar configurações do SQLAlchemy
        config = DatabaseConfig.get_sqlalchemy_config()
        for key, value in config.items():
            app.config[key] = value
        
        # Inicializar SQLAlchemy
        from app.models import db
        self.db = db
        self.db.init_app(app)
        
        # Configurar eventos do SQLAlchemy
        self._setup_engine_events()
        
        # Armazenar referência no app
        app.db_manager = self
        
        # Registrar comandos CLI
        self._register_cli_commands(app)
    
    def _setup_engine_events(self):
        """Configura eventos do engine para otimizações específicas do SQL Server"""
        
        from sqlalchemy import event
        
        @event.listens_for(Engine, "connect")
        def set_sql_server_settings(dbapi_connection, connection_record):
            """Configurações específicas do SQL Server aplicadas a cada conexão"""
            
            with dbapi_connection.cursor() as cursor:
                # Configurações de performance
                cursor.execute("SET ARITHABORT ON")
                cursor.execute("SET ANSI_NULLS ON")
                cursor.execute("SET ANSI_PADDING ON")
                cursor.execute("SET ANSI_WARNINGS ON")
                cursor.execute("SET CONCAT_NULL_YIELDS_NULL ON")
                cursor.execute("SET QUOTED_IDENTIFIER ON")
                
                # Configurações de isolamento e lock
                cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                cursor.execute("SET LOCK_TIMEOUT 30000")  # 30 segundos
                
                # Configurações de data/hora
                cursor.execute("SET DATEFORMAT ymd")
                cursor.execute("SET DATEFIRST 1")  # Segunda-feira como primeiro dia da semana
                
            dbapi_connection.commit()
    
    def test_connection(self):
        """Testa a conexão com o banco de dados"""
        
        try:
            with self.db.engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test"))
                return result.fetchone()[0] == 1
        except Exception as e:
            print(f"Erro ao testar conexão: {e}")
            return False
    
    def create_tables(self):
        """Cria todas as tabelas definidas nos models"""
        
        try:
            self.db.create_all()
            print("Tabelas criadas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
    
    def drop_tables(self):
        """Remove todas as tabelas (cuidado!)"""
        
        try:
            self.db.drop_all()
            print("Tabelas removidas com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao remover tabelas: {e}")
            return False
    
    @contextmanager
    def get_session(self):
        """Context manager para sessões manuais do SQLAlchemy"""
        
        session = self.db.session
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def execute_raw_sql(self, sql_query, params=None):
        """Executa SQL bruto de forma segura"""
        
        try:
            with self.db.engine.connect() as connection:
                if params:
                    result = connection.execute(text(sql_query), params)
                else:
                    result = connection.execute(text(sql_query))
                
                connection.commit()
                return result
        except Exception as e:
            print(f"Erro ao executar SQL: {e}")
            raise
    
    def get_database_info(self):
        """Retorna informações sobre o banco de dados"""
        
        try:
            with self.db.engine.connect() as connection:
                # Versão do SQL Server
                version_result = connection.execute(text("SELECT @@VERSION as version"))
                version = version_result.fetchone()[0]
                
                # Nome do banco
                db_name_result = connection.execute(text("SELECT DB_NAME() as db_name"))
                db_name = db_name_result.fetchone()[0]
                
                # Informações do servidor
                server_result = connection.execute(text("SELECT @@SERVERNAME as server_name"))
                server_name = server_result.fetchone()[0]
                
                return {
                    'version': version,
                    'database_name': db_name,
                    'server_name': server_name,
                    'connection_string': DatabaseConfig.get_connection_string()
                }
        except Exception as e:
            return {'error': str(e)}
    
    def _register_cli_commands(self, app: Flask):
        """Registra comandos CLI para gerenciamento do banco"""
        
        @app.cli.command('init-db')
        def init_db_command():
            """Cria o banco de dados."""
            if self.create_tables():
                print('Banco de dados inicializado.')
            else:
                print('Erro ao inicializar banco de dados.')
        
        @app.cli.command('test-db')
        def test_db_command():
            """Testa conexão com o banco de dados."""
            if self.test_connection():
                print('✅ Conexão com banco OK!')
                info = self.get_database_info()
                print(f"Servidor: {info.get('server_name', 'N/A')}")
                print(f"Banco: {info.get('database_name', 'N/A')}")
            else:
                print('❌ Falha na conexão com banco!')
        
        @app.cli.command('db-info')
        def db_info_command():
            """Mostra informações do banco de dados."""
            info = self.get_database_info()
            for key, value in info.items():
                print(f"{key}: {value}")

# Instância global do gerenciador de banco
db_manager = DatabaseManager()

def init_database(app: Flask):
    """Função auxiliar para inicializar o banco de dados"""
    db_manager.init_app(app)
    return db_manager

# Função para criar engine standalone (útil para scripts)
def create_standalone_engine():
    """Cria um engine SQLAlchemy standalone para uso fora do Flask"""
    
    connection_string = DatabaseConfig.get_connection_string()
    
    engine = create_engine(
        connection_string,
        poolclass=QueuePool,
        pool_size=DatabaseConfig.POOL_SIZE,
        max_overflow=DatabaseConfig.MAX_OVERFLOW,
        pool_timeout=DatabaseConfig.POOL_TIMEOUT,
        pool_recycle=DatabaseConfig.POOL_RECYCLE,
        pool_pre_ping=True,
        echo=False
    )
    
    return engine

def create_standalone_session():
    """Cria uma sessão standalone para uso fora do Flask"""
    
    engine = create_standalone_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Exemplo de uso em scripts
if __name__ == "__main__":
    # Teste de conexão standalone
    print("Testando conexão standalone...")
    
    try:
        engine = create_standalone_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            print(f"✅ Conexão OK! Resultado: {result.fetchone()[0]}")
            
            # Informações do banco
            info_result = conn.execute(text("SELECT DB_NAME() as db, @@SERVERNAME as server"))
            info = info_result.fetchone()
            print(f"Banco: {info[0]}, Servidor: {info[1]}")
            
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        print("\n🔧 Verifique:")
        print("1. Se o SQL Server está rodando")
        print("2. Se as credenciais estão corretas")
        print("3. Se o driver ODBC está instalado")
        print("4. Se o banco de dados existe")
        print("5. Se as variáveis de ambiente estão configuradas")
