from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import listar_estudos, obter_estudo, Estudo
from app.auth import requires_permission, get_usuario_logado

listar_bp = Blueprint("listar", __name__, template_folder="templates")


@listar_bp.route("/listar", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    dados = listar_estudos(page, per_page)
    usuario = get_usuario_logado()
    print(dados)

    return render_template("listar/listar.html", documentos=dados["estudos"], pagination=dados["pagination"], usuario=usuario)

