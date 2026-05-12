import os
from sqlalchemy.sql import text
from flask import Blueprint, render_template, send_file, request, g, session
from models.usuario import Usuario
from dotenv import load_dotenv
from types import SimpleNamespace
from auth import get_usuario_logado
import requests
#from database import db_manager
#from auth import requires_permission, get_usuario_logado
import datetime

from database import db
import json
#from auth import requires_permission

# rode no terminal para deploy: caddy run --config Caddyfile
main_bp = Blueprint("main", __name__, template_folder='templates', static_folder='static')

BGI_PATH = r"\\edpbr393\SourceFiles$\EDP_Settings\Wallpaper\BG_info\NewBGI\BGInfo"

load_dotenv()

def msg_boas_vidas(nome):
    if 12-3 > datetime.datetime.now().hour > 4:
        return f"Bom dia, {nome}."
    elif 18-3 > datetime.datetime.now().hour >= 12:
        return f"Boa tarde, {nome}."
    else:
        return f"Boa noite, {nome}."

@main_bp.route('/bginfo_latest')
def bginfo_latest():
    bg = get_latest_bg()
    if bg:
        return send_file(bg)
    return "", 404

from flask import g, request

@main_bp.before_app_request
def carregar_usuario():

    g.user = None
    try:

        # DESENVOLVIMENTO LOCAL
        if os.getenv('DEVELOP'):

            g.user = SimpleNamespace(
                nome='Jader',
                matricula='7034',
                admin=True,
                editar=True,
                deletar=True
            )

        else:

            email = request.headers.get("X-Forwarded-Email")

            if not email:
                return

            prefix_email = email.split('@')[0]

            usuario = (
                Usuario.query
                .filter(Usuario.nome.like(f'{prefix_email}%'))
                .first()
            )

        if usuario:
            g.user = usuario

            session['matricula'] = usuario.matricula

    except Exception as e:

        print(f'Erro ao carregar usuário: {e}')


@main_bp.route("/")
def home():
    print(f'g.user: {g.user}')
    if not g.user:
        return render_template(
            "main/index.html",
            usuario=None,
            msg="Usuário não autenticado."
        )

    return render_template(
        "main/index.html",
        usuario=g.user,
        msg=msg_boas_vidas('teste')
    )


def get_latest_bg():
    """Retorna o caminho completo do arquivo .jpg mais recente da pasta."""
    try:
        files = [
            os.path.join(BGI_PATH, f)
            for f in os.listdir(BGI_PATH)
            if f.lower().endswith(".jpg")
        ]

        if not files:
            return None

        # arquivo com data de modificação mais recente
        latest = max(files, key=os.path.getmtime)

        # URL amigável para enviar ao HTML (Windows UNC → URL)
        return latest.replace("\\", "/")

    except Exception as e:
        print("Erro ao acessar BGInfo:", e)
        return None


@main_bp.route("/health/db/<sql>")
def health_db(sql):

    try:

        result = db.session.execute(
            text(sql)
        )

        version = result.fetchone()[0]

        return {
            "status": "success",
            "database": version
        }, 200

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }, 500

