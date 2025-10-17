#from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
#from app.models import db,Subestacao, Municipio, EDP, Circuito
#from sqlalchemy.orm import joinedload
#from sqlalchemy import asc, desc

#circuito_bp = Blueprint("circuitos", __name__, template_folder="templates", static_folder="static", static_url_path='/static')
#circuito_bp = Blueprint("circuitos", __name__, template_folder="templates")

#@circuito_bp.route("/circuitos")
#def listar_circuitos():
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
#    registros = Circuito.query.options(
#        joinedload(Circuito.subestacao),
#        joinedload(Circuito.edp)
#    ).all()

    # Converter usando o método to_dict()
#    itens_serializaveis = [circuito.to_dict() for circuito in registros]

#    colunas = [
#        {'value': 'id_circuito', 'nome': 'ID', 'visivel': True},
#        {'value': 'circuito', 'nome': 'Circuito', 'visivel': True},
#        {'value': 'tensao', 'nome': 'Tensão', 'visivel': True},
#        {'value': 'edp.empresa', 'nome': 'EDP', 'visivel': True},
#        {'value': 'subestacao.nome', 'nome': 'Subestação', 'visivel': True}
#    ]
    
    # Para o modal
#    labels_map = {c['value']: c['nome'] for c in colunas}

    # Definir as ações disponíveis para cada registro
#    acoes = [
#        {
#            'type': 'view',
#            'icon': 'bi bi-eye',
#            'js_function': 'verDetalhes', # Chama a função JS verDetalhes(id)
#            'tooltip': 'Ver detalhes'
#        },
#    {
#        'type': 'edit',
#        'icon': 'bi bi-pencil',
#        'js_function': 'abrirModalEditar',
#        'tooltip': 'Editar'
#    }
#    ]

#    return render_template(
#        "listar_unificado.html",
#        titulo="Lista de Circuitos",    # OBRIGATÓRIO
#        titulo_modal="Circuito",
        #botao_novo -> OPCIONAL
#        colunas = colunas,    # OBRIGATÓRIO
#        itens = itens_serializaveis,
#        acoes = acoes,
#       campo_id = 'id_circuito',
 #       labels_map=labels_map
 #   )

#@circuito_bp.route('/circuitos/<int:id>/editar', methods=['POST'])
#def editar_circuito(id):
#    circuito = Circuito.query.get_or_404(id)
#    # Atualiza os campos recebidos
#    for campo in request.form:
#        if hasattr(circuito, campo):
#            setattr(circuito, campo, request.form[campo])
#    db.session.commit()
#    return jsonify({'status': 'ok'})

# TAVA ANTES ATÉ AQUI #

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, send_from_directory, \
    abort, flash
from werkzeug.utils import safe_join
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo, Circuito
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.orm import joinedload
import os

circuito_bp = Blueprint("circuitos", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/circuitos/static')


@circuito_bp.route("/circuitos", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = Circuito.query.options(
        joinedload(Circuito.subestacao),
        joinedload(Circuito.edp)
    ).all()
    print(registros[0])
    
    usuario = get_usuario_logado()


    return render_template("circuitos/listar.html", documentos=registros, usuario=usuario)

#@listar_bp.route('/listar/download/<path:filename>')
#@requires_permission('visualizar')
#def download_file(filename):
#    try:
        # Garante que o caminho seja seguro e dentro da pasta uploads
#        UPLOAD_FOLDER = os.path.join(os.path.dirname(current_app.root_path)).replace('\\', '/')
#        safe_path = safe_join(UPLOAD_FOLDER, filename)

#        if not safe_path or not os.path.isfile(safe_path):
#            flash("⚠️ Arquivo não encontrado ou removido.", "warning")
#            abort(404)

#        directory = os.path.dirname(safe_path)
#        file = os.path.basename(safe_path)

#        return send_from_directory(directory, file, as_attachment=True)
#    except Exception as e:
#        print(f'Erro em listar/routes: def download_file() - {str(e)} ')
#        flash('Não foi possível encontrar o arquivo no servidor.')
#        abort(404)
