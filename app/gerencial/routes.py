from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, send_from_directory, \
    abort, flash
from werkzeug.utils import safe_join
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo, Alternativa
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.orm import joinedload
import os

gestao_bp = Blueprint("gestao", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/gestao/static')


@gestao_bp.route("/gestao/estudos", methods=["GET", "POST"])
@requires_permission('visualizar')
def aprovacao():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    dados = listar_estudos(page, per_page)
    status_tipos = StatusTipo.query.all()
    print(status_tipos)
    usuario = get_usuario_logado()

    return render_template("gestao/aprovacao.html", documentos=dados["estudos"],
                           pagination=dados["pagination"], usuario=usuario, status_tipos=status_tipos)


@gestao_bp.route("/gestao/aprovacao", methods=["GET"])
@requires_permission('visualizar')
def gestao_aprovacao():
    valor_minimo = request.args.get("min_valor", 1_000_000.00, type=float)

    estudos = (
        Estudo.query
        .join(Estudo.alternativas)  # relacionamento ORM
        .filter(
            Alternativa.flag_alternativa_escolhida == 0,
            Alternativa.custo_modular >= valor_minimo
        )
        .options(joinedload(Estudo.alternativas))  # carrega todas as alternativas do estudo
        .all()
    )

    usuario = get_usuario_logado()
    status_tipos = StatusTipo.query.all()

    return render_template("gestao/aprov.html",
                           documentos=estudos,
                           usuario=usuario,
                           status_tipos=status_tipos,
                           valor_minimo=valor_minimo)
