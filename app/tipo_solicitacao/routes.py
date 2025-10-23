from flask import Blueprint, render_template, request, jsonify
from app.models import Circuito, db, EDP, Subestacao, TipoSolicitacao
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.orm import joinedload
import re
from sqlalchemy.exc import IntegrityError

tipo_solicitacao_bp = Blueprint("tipo_solicitacao", __name__, template_folder="templates", static_folder="static", static_url_path='/tipo_solicitacao/static')

@tipo_solicitacao_bp.route("/tipo_solicitacao", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = TipoSolicitacao.query.all()
    print(registros[0])
    
    usuario = get_usuario_logado()

    return render_template("listar_tipo_solicitacao.html", documentos=registros, usuario=usuario)

@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/editar', methods=['POST'])
def editar_circuito(id):
    circuito = Circuito.query.get_or_404(id)
    
    # CORREÇÃO: Verificar se é JSON ou FormData
    if request.is_json:
        data = request.get_json()
        print("Dados recebidos (JSON):", data)  # Para debug
    else:
        data = request.form.to_dict()
        print("Dados recebidos (Form):", data)  # Para debug
    
    # Atualiza os campos recebidos
    for campo in data:
        if hasattr(circuito, campo):
            print(f"Atualizando {campo}: {getattr(circuito, campo)} -> {data[campo]}")  # Para debug
            setattr(circuito, campo, data[campo])
    
    try:
        db.session.commit()
        print("Commit realizado com sucesso!")  # Para debug
        return jsonify({'status': 'success', 'message': 'Circuito atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no commit: {e}")  # Para debug
        return jsonify({'status': 'error', 'message': str(e)}), 500


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/api', methods=['GET'])
def get_tipo_solicitacao_api(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)

    return jsonify({
        'id': tipo_solicitacao.id_tipo_solicitacao,
        'viabilidade': tipo_solicitacao.viabilidade,
        'analise': tipo_solicitacao.analise,
        'pedido': tipo_solicitacao.pedido
    })


@tipo_solicitacao_bp.route('/circuitos/<int:id>/excluir', methods=['POST'])
def excluir_circuito(id):
    circuito = Circuito.query.get_or_404(id)
    try:
        db.session.delete(circuito)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Circuito excluído com sucesso!'})
    
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e.orig)
        
        # Extrai o nome da tabela do erro
        tabela_match = re.search(r'table "([^"]+)"', error_message)
        if tabela_match:
            tabela = tabela_match.group(1)
            tabela_nome = tabela.split('.')[-1] if '.' in tabela else tabela
            mensagem = f'Não é possível excluir este circuito! Existem registros relacionados na tabela "{tabela_nome}". Remova os registros relacionados antes de excluir o circuito.'
        else:
            mensagem = 'Não é possível excluir este circuito! Existem registros relacionados a ele em outras tabelas. Remova os registros relacionados primeiro.'
        
        return jsonify({'status': 'error', 'message': mensagem}), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Erro inesperado ao excluir o circuito.'}), 500

    
@tipo_solicitacao_bp.route('/circuitos/adicionar', methods=['POST'])
def adicionar_circuito():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # Validação de campos obrigatórios
    campos_obrigatorios = ['circuito', 'tensao', 'id_subestacao', 'id_edp']
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    
    if campos_faltantes:
        return jsonify({
            'status': 'error',
            'message': f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}'
        }), 400
    
    try:
        novo_circuito = Circuito(
            circuito=data.get('circuito'),
            tensao=data.get('tensao'),
            id_subestacao=data.get('id_subestacao'),
            id_edp=data.get('id_edp')
        )
        db.session.add(novo_circuito)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Circuito adicionado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar circuito: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

