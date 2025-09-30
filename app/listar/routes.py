from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo
from app.auth import requires_permission, get_usuario_logado

listar_bp = Blueprint("listar", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/listar/static')


@listar_bp.route("/listar", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    dados = listar_estudos(page, per_page)
    status_tipos = StatusTipo.query.all()
    print(status_tipos)
    usuario = get_usuario_logado()

    return render_template("listar/listar.html", documentos=dados["estudos"],
                           pagination=dados["pagination"], usuario=usuario, status_tipos=status_tipos)

