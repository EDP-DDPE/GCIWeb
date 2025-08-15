from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify

listar_bp = Blueprint("listar", __name__, template_folder="templates")


@listar_bp.route("/listar", methods=["GET", "POST"])
def listar():
    documentos=[]
    return render_template('listar/listar.html', documentos=documentos)

