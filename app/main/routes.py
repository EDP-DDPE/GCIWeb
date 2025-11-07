from flask import Blueprint, render_template, session, redirect, url_for, jsonify
import requests
from app.database import db_manager
from app.auth import requires_permission, get_usuario_logado
import datetime
import json
from app.auth import requires_permission
# rode no terminal para deploy: caddy run --config Caddyfile
main_bp = Blueprint("main", __name__, template_folder='templates', static_folder='static')


@main_bp.route("/debug")
def debug():
    from flask import request, current_app

    # Debug completo de todos os headers
    all_headers = dict(request.headers)

    return {
        "scheme": request.scheme,
        "url_root": request.url_root,
        "X-Forwarded-Proto": request.headers.get("X-Forwarded-Proto"),
        "X-Forwarded-Host": request.headers.get("X-Forwarded-Host"),
        "X-Forwarded-Port": request.headers.get("X-Forwarded-Port"),
        "Host": request.headers.get("Host"),
        "environ_wsgi_url_scheme": request.environ.get('wsgi.url_scheme'),
        "all_headers": all_headers,
        "has_proxy_fix": 'ProxyFix' in str(type(current_app.wsgi_app))
    }


def msg_boas_vidas(nome):
    if 12 > datetime.datetime.now().hour > 4:
        return f"Bom dia, {nome}."
    elif 18 > datetime.datetime.now().hour >= 12:
        return f"Boa tarde, {nome}."
    else:
        return f"Boa noite, {nome}."


@main_bp.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("auth.public"))
    usuario = get_usuario_logado()


    # return f"""
    #         <h2>Olá, {claims.get('name')}</h2>
    #         <p>Login: {claims.get('preferred_username')}</p>
    #         <a href="/me">Chamar Microsoft Graph /me</a> |
    #         <a href="auth/logout">Sair</a>
    #     """
    token = session.get("access_token")
    resp = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    graph = json.loads(resp.text)

    if "error" in graph:
        return redirect(url_for("auth.public"))

    nome = graph['givenName']


    return render_template("main/index.html", usuario=usuario, msg=msg_boas_vidas(nome))


@main_bp.route('/health')
def health_check():
    """Health check da aplicação"""

    db_ok = db_manager.test_connection()

    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected'
    }), 200 if db_ok else 503