from flask import Blueprint, render_template, session, redirect, url_for, jsonify
import requests
from app.database import db_manager

main_bp = Blueprint("main", __name__, template_folder='templates', static_folder='static')


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

    return render_template("main/index.html", usuario=usuario)


@main_bp.route('/health')
def health_check():
    """Health check da aplicação"""

    db_ok = db_manager.test_connection()

    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': 'connected' if db_ok else 'disconnected'
    }), 200 if db_ok else 503