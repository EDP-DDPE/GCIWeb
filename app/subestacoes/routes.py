from flask import Blueprint, render_template, request
from app.models import Subestacao, Municipio, EDP

subestacao_bp = Blueprint("subestacoes", __name__, template_folder="templates")

@subestacao_bp.route("/subestacoes", methods=["GET", "POST"])
def listar_subestacoes():
    dados = Subestacao.query.all()
    return render_template("subestacoes.html", documentos=dados)

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
