from app.main import create_app
from werkzeug.middleware.proxy_fix import ProxyFix

import logging
from logging.handlers import RotatingFileHandler
import os

# === Diretório para armazenar logs ===
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'atlas.log')

# === Formato padronizado ===
LOG_FORMAT = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'

# === Configuração global do Flask ===
logging.basicConfig(
    level=logging.INFO,               # níveis: DEBUG / INFO / WARNING / ERROR / CRITICAL
    format=LOG_FORMAT,
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()       # mantém saída no console (opcional)
    ]
)

# === Silenciar logs detalhados do SQLAlchemy ===
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

# === Silenciar logs do servidor Werkzeug ===
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# === Caso use outros frameworks ===
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Exemplo de log manual
logger = logging.getLogger(__name__)
logger.info("✅ Logging configurado com sucesso!")


# Cria a aplicação Flask
app = create_app()

app.config.update(
    SQLALCHEMY_ECHO=False,   # evita log de SQL
    DEBUG=False              # desativa debug do Flask
)

if __name__ == "__main__":
    app.run()