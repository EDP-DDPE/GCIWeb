from app.main import create_app
from werkzeug.middleware.proxy_fix import ProxyFix


# Cria a aplicação Flask
app = create_app()

if __name__ == "__main__":
    app.run()