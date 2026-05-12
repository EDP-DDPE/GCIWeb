from flask import Flask
import os
from config import Config
from database import db
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')

    app = Flask(__name__, template_folder=template_folder)

    app.config.from_object(Config)
    db.init_app(app)

    # ===== Registro de blueprints =====
    # Importação tardia para evitar ciclos
    from .routes import main_bp
    from cadastro.routes import cadastro_bp
    from listar.routes import listar_bp
    from api.routes import api_bp
    from subestacoes.routes import subestacao_bp
    from user.routes import user_bp
    from municipios.routes import municipio_bp
    from alternativa.routes import alternativa_bp
    from circuitos.routes import circuito_bp
    from status.routes import status_bp
    from deploy.routes import deploy_bp
    from gerencial.routes import gestao_bp
    from tipo_solicitacao.routes import tipo_solicitacao_bp
    from status_tipos.routes import status_tipos_bp
    from regionais.routes import regionais_bp
    from resp_regioes.routes import resp_regioes_bp
    from empresas.routes import empresas_bp
    from bot.routes import bot_bp

    app.register_blueprint(cadastro_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(listar_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(subestacao_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(municipio_bp)
    app.register_blueprint(alternativa_bp)
    app.register_blueprint(circuito_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(deploy_bp)
    app.register_blueprint(gestao_bp)
    app.register_blueprint(tipo_solicitacao_bp)
    app.register_blueprint(status_tipos_bp)
    app.register_blueprint(regionais_bp)
    app.register_blueprint(resp_regioes_bp)
    app.register_blueprint(empresas_bp)
    app.register_blueprint(bot_bp)

    return app