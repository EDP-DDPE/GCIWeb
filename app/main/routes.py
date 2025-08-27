from flask import Blueprint, render_template, session, redirect, url_for, jsonify
import requests
from app.database import db_manager
import datetime
import json

main_bp = Blueprint("main", __name__, template_folder='templates', static_folder='static')

def msg_boas_vidas(nome):
    if 12 > datetime.datetime.now().hour > 4:
        return f"Bom dia, {nome}."
    elif 18 > datetime.datetime.now().hour > 12:
        return f"Boa tarde, {nome}."
    else:
        return f"Bom noite, {nome}."

@main_bp.route("/")
def home():
    if "user" not in session:
        return redirect(url_for("auth.public"))
    usuario = session["user"]
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
    nome = json.loads(resp.text)['givenName']
    return render_template("main/index.html", usuario=usuario, msg=msg_boas_vidas(nome))


@main_bp.route('/health')
def health_check():
    """Health check da aplicação"""

    db_ok = db_manager.test_connection()

    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected'
    }), 200 if db_ok else 503