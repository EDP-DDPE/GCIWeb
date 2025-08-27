from flask import Blueprint, render_template, session, redirect, url_for
import requests
import json

user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/user", methods=["GET", "POST"])
def user():
    if "user" not in session:
        return redirect(url_for("auth.public"))
    else:
        user_data = session['user']
        token = session.get("access_token")

    if not token:
        return redirect(url_for("main.home"))

    resp = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )

    graph = json.loads(resp.text)
    #return (resp.text, resp.status_code, {"Content-Type": "application/json"})
    return render_template('user/user.html', user=user_data, graph=graph)

@user_bp.route("/me")
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