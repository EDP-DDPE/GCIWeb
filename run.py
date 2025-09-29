from app.models import db
from app.main import create_app
from app.database import db_manager

# from waitress import serve

app = create_app()


def run():

    # Context da aplicação para comandos
    with app.app_context():
        print("🚀 Iniciando aplicação GCI Web...")
        # Testar conexão
        if db_manager.test_connection():
            print("✅ Conexão com SQL Server OK!")

            # Mostrar informações do banco
            db_info = db_manager.get_database_info()
            print(f"📊 Servidor: {db_info.get('server_name', 'N/A')}")
            print(f"🗄️  Banco: {db_info.get('database_name', 'N/A')}")

            # Criar tabelas se necessário (cuidado em produção!)
            try:
                # db.create_all()
                print("📋 Tabelas verificadas/criadas!")
            except Exception as e:
                print(f"⚠️  Aviso ao verificar tabelas: {e}")

        else:
            print("❌ Falha na conexão com SQL Server!")
            print("🔧 Verifique as configurações no arquivo database.py")

    # Executar aplicação
    print("🌐 Iniciando servidor Flask...")

    app.run(debug=True)


if __name__ == "__main__":
    # app = create_app()
    # app.run()
    run()

    # serve(
    #     app,
    #     host='0.0.0.0',
    #     port=443,  # Porta HTTPS padrão
    #     url_scheme='https'
    #     # Certificados SSL
    # )
