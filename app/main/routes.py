from flask import Blueprint, render_template, session, redirect, url_for
import requests

main_bp = Blueprint("main", __name__, template_folder='templates')


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

@main_bp.route("/me")
def me():
    """
    Exemplo de chamada ao Microsoft Graph /me (exige escopo User.Read).
    """
    token = session.get("access_token")
    if not token:
        return redirect(url_for("main.home"))

    resp = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    return (resp.text, resp.status_code, {"Content-Type": "application/json"})
