from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import db,Subestacao, Municipio, EDP
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc

subestacao_bp = Blueprint("subestacoes", __name__, template_folder="templates")

@subestacao_bp.route("/subestacoes", methods=["GET", "POST"])
def listar_subestacoes():
    query = (
        Subestacao.query.options(
            joinedload(Subestacao.municipio),
            joinedload(Subestacao.edp),
            joinedload(Subestacao.circuitos)
        )
    )
 
    total_subestacoes = Subestacao.query.count()
    lista = query.order_by(Subestacao.id_subestacao.asc()).all()
    
    return render_template(
        "subestacoes.html",
        subestacoes=lista,
        total_subestacoes=total_subestacoes
    )

@subestacao_bp.route("/subestacoes/<int:id>/editar", methods=["GET", "POST"])
def editar_subestacao(id):
    sub = Subestacao.query.get_or_404(id)
    municipios = Municipio.query.all()
    edps = EDP.query.all()

    if request.method == "POST":
        if "delete" in request.form:
            try:
                db.session.delete(sub)
                db.session.commit()
                flash("Subestação apagada com sucesso!", "success")
                return redirect(url_for("subestacoes.listar_subestacoes"))
            except Exception as e:
                db.session.rollback()
                flash("Não foi possível apagar a suestação", "danger")

        # Atualizar subestação
        sub.nome = request.form["nome"]
        sub.sigla = request.form["sigla"]
        sub.id_municipio = request.form["id_municipio"]
        sub.id_edp = request.form["id_edp"]
        sub.lat = request.form["lat"]
        sub.long = request.form["long"]
        db.session.commit()
        flash("Subestação atualizada com sucesso!", "success")
        return redirect(url_for("subestacoes.listar_subestacoes"))

    return render_template(
        "editar_subestacao.html",
        sub=sub,
        municipios=municipios,
        edps=edps
    )

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
