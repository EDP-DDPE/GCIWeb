from flask import Blueprint, render_template, request
from app.models import Subestacao

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