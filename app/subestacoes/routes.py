from flask import Blueprint, render_template, request
from app.models import Subestacao, Municipio, EDP
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc

subestacao_bp = Blueprint("subestacoes", __name__, template_folder="templates")

@subestacao_bp.route("/subestacoes", methods=["GET", "POST"])
def listar_subestacoes():

    sort = request.args.get("sort", "id_subestacao") # campo padrão
    direction = request.args.get("direction", "asc") # asc ou desc

    # valores de filtro
    nome_filtro = request.args.get("nome", "")
    sigla_filtro = request.args.get("sigla", "")
    municipio_filtro = request.args.get("municipio", "")
    edp_filtro = request.args.get("edp", "")

    query = (
        Subestacao.query.options(
            joinedload(Subestacao.municipio),
            joinedload(Subestacao.edp),
            joinedload(Subestacao.circuitos)
        )
    )

    # filtros
    if nome_filtro:
        query = query.filter(Subestacao.nome.ilike(f"%{nome_filtro}%"))
    if sigla_filtro:
        query = query.filter(Subestacao.sigla.ilike(f"%{sigla_filtro}%"))
    if municipio_filtro:
        query = query.join(Subestacao.municipio).filter(Municipio.municipio.ilike(f"%{municipio_filtro}%"))
    if edp_filtro:
        query = query.join(Subestacao.edp).filter(EDP.empresa.ilike(f"%{edp_filtro}%"))

    #Mapeia colunas válidas
    sort_columns = {
        "id": Subestacao.id_subestacao,
        "nome": Subestacao.nome,
        "sigla": Subestacao.sigla
    }

        # colunas de relacionamento exigem join
    if sort == "municipio":
        query = query.join(Subestacao.municipio)
        col = Municipio.municipio
    elif sort == "edp":
        query = query.join(Subestacao.edp)
        col = EDP.empresa
    else:
        col = sort_columns.get(sort, Subestacao.id_subestacao)

    if sort in sort_columns:
        col = sort_columns[sort]
        if direction == "desc":
            query = query.order_by(desc(col))
        else:
            query = query.order_by(asc(col))

    dados = query.all()

    return render_template(
        "subestacoes.html",
        documentos = dados,
        sort = sort,
        direction = direction
    )

@subestacao_bp.route("/subestacoes/<int:id>/editar", methods=["GET", "POST"])
def editar_subestacao(id):
    sub = Subestacao.query.get_or_404(id)

    if request.method == "POST":
        sub.nome = request.form["nome"]
        sub.sigla = request.form["sigla"]
        # se quiser permitir mudar município ou edp:
        # sub.id_municipio = request.form["id_municipio"]
        # sub.id_edp = request.form["id_edp"]

        db.session.commit()
        flash("Subestação atualizada com sucesso!", "success")
        return redirect(url_for("subestacoes.listar_subestacoes"))

    return render_template("editar_subestacao.html", sub=sub)

@subestacao_bp.route("/subestacoes/nova", methods=["GET", "POST"])
def nova_subestacao():
    municipios = Municipio.query.all()
    edps = EDP.query.all()

    if request.method == "POST":
        nome = request.form["nome"]
        sigla = request.form["sigla"]
        id_municipio = request.form["id_municipio"]
        id_edp = request.form["id_edp"]

        nova = Subestacao(
            nome=nome,
            sigla=sigla,
            id_municipio=id_municipio,
            id_edp=id_edp
        )
        db.session.add(nova)
        db.session.commit()
        flash("Subestação cadastrada com sucesso!", "success")
        return redirect(url_for("subestacoes.listar_subestacoes"))

    return render_template("nova_subestacao.html", municipios=municipios, edps=edps)
