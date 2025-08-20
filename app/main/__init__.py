
from flask import Flask, render_template, session, redirect, url_for, request
import os

import msal
import requests
from dotenv import load_dotenv
from urllib.parse import quote_plus
from flask_session import Session
from app.auth.routes import create_auth_blueprint
from app.database import init_database, db_manager


def create_app(test_config=None):

    load_dotenv()

    app = Flask(__name__, instance_relative_config=True, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET"),
        SESSION_TYPE="filesystem",
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=True,
        SESSION_FILE_THRESHOLD=100,
        UPLOAD_FOLDER='uploads',  # ou caminho desejado
        DATABASE=os.path.join(app.instance_path, 'SQLSERVER'),
        JSON_AS_ASCII=False
    )

    # if test_config is None:
    #     # load the instance config, if it exists, when not testing
    #     app.config.from_pyfile('config.py', silent=True)
    # else:
    #     # load the test config if passed in
    #     app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    Session(app)

    # ===== Configs de Autenticação (Microsoft Entra ID) =====
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")  # PROD: prefira certificado/credencial federada
    tenant_id = os.getenv("TENANT_ID")

    # Caminho/URI de redirecionamento (PRECISAM bater com o App Registration)
    redirect_path = os.getenv("REDIRECT_PATH", "auth/callback")
    redirect_uri = os.getenv("REDIRECT_URI", f"http://localhost:5000/auth{redirect_path}")

    # Authority (single-tenant). Para multi-tenant, avalie 'organizations' ou 'common'
    authority = f"https://login.microsoftonline.com/{tenant_id}"

    # Scopes OIDC + Graph (delegado)
    scopes = ["User.Read"]

    if not isinstance(scopes, list):
        scopes = list(scopes)

    app.config.update(
        AUTH_CLIENT_ID=client_id,
        AUTH_CLIENT_SECRET=client_secret,
        AUTH_TENANT_ID=tenant_id,
        AUTH_AUTHORITY=authority,
        AUTH_REDIRECT_PATH=redirect_path,
        AUTH_REDIRECT_URI=redirect_uri,
        AUTH_SCOPES=scopes,
    )

    init_database(app)

    # ===== Registro de blueprints =====
    # Importação tardia para evitar ciclos
    from .routes import main_bp
    from app.cadastro.routes import cadastro_bp
    from app.listar.routes import listar_bp
    from app.api.routes import api_bp

    app.register_blueprint(create_auth_blueprint(redirect_path="/callback"), url_prefix="/auth")
    # REDIRECT_URI deve ser http://localhost:5000/auth/callback

    app.register_blueprint(cadastro_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(listar_bp)
    app.register_blueprint(api_bp)

    # with app.app_context():
    #     print("\n[DEBUG] Rotas registradas:")
    #     for rule in app.url_map.iter_rules():
    #         print(f"- {rule.rule} -> {rule.endpoint}")

    return app