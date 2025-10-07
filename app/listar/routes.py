from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, send_from_directory, \
    abort, flash
from werkzeug.utils import safe_join
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo
from app.auth import requires_permission, get_usuario_logado
import os

listar_bp = Blueprint("listar", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/listar/static')


# pasta 'uploads' dentro do projeto


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


@listar_bp.route('/listar/download/<path:filename>')
@requires_permission('visualizar')
def download_file(filename):
    try:
        # Garante que o caminho seja seguro e dentro da pasta uploads
        UPLOAD_FOLDER = os.path.join(os.path.dirname(current_app.root_path)).replace('\\', '/')
        safe_path = safe_join(UPLOAD_FOLDER, filename)

        if not safe_path or not os.path.isfile(safe_path):
            flash("⚠️ Arquivo não encontrado ou removido.", "warning")
            abort(404)

        directory = os.path.dirname(safe_path)
        file = os.path.basename(safe_path)

        return send_from_directory(directory, file, as_attachment=True)
    except Exception as e:
        print(f'Erro em listar/routes: def download_file() - {str(e)} ')
        flash('Não foi possível encontrar o arquivo no servidor.')
        abort(404)
