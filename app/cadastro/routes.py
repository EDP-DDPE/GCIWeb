from flask import Blueprint, render_template, request, redirect, url_for, session
from .forms import DocumentoForm

cadastro_bp = Blueprint("cadastro", __name__, template_folder="templates")

@cadastro_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    form = DocumentoForm()
    if request.method == 'POST':
        print('teste2')


    return render_template('cadastro/cadastrar.html', form=form)
