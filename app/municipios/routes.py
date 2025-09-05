from app.models import Municipio, EDP, Regional, Subestacao
from flask import Blueprint, render_template, request
from sqlalchemy.orm import joinedload
from sqlalchemy import asc, desc

municipio_bp = Blueprint("municipios", __name__, template_folder="templates")

@municipio_bp.route("/municipios", methods=["GET"])
def listar_municipios():

    query = (
        Municipio.query.options(
            joinedload(Municipio.edp),
            joinedload(Municipio.regional),
            joinedload(Municipio.subestacoes)
        )
    )
    
    total_municipios = Municipio.query.count()

    lista = query.order_by(Municipio.id_municipio.asc()).all()
    
    return render_template(
        "municipios.html",
        municipios=lista,
        total_municipios=total_municipios
    )