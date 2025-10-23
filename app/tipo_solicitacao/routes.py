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
@requires_permission('editar')
def editar_circuito(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)
    
    # CORREÇÃO: Verificar se é JSON ou FormData
    if request.is_json:
        data = request.get_json()
        print("Dados recebidos (JSON):", data)  # Para debug
    else:
        data = request.form.to_dict()
        print("Dados recebidos (Form):", data)  # Para debug
    
    # Atualiza os campos recebidos
    for campo in data:
        if hasattr(tipo_solicitacao, campo):
            print(f"Atualizando {campo}: {getattr(tipo_solicitacao, campo)} -> {data[campo]}")  # Para debug
            setattr(tipo_solicitacao, campo, data[campo])
    
    try:
        db.session.commit()
        print("Commit realizado com sucesso!")  # Para debug
        return jsonify({'status': 'success', 'message': 'Tipo atualizado com sucesso!'})
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


@tipo_solicitacao_bp.route('/tipo_solicitacao/<int:id>/excluir', methods=['POST'])
@requires_permission('excluir')
def excluir_circuito(id):
    tipo_solicitacao = TipoSolicitacao.query.get_or_404(id)
    
    # Verifica se NÃO há estudos associados
    if not tipo_solicitacao.estudos:
        try:
            db.session.delete(tipo_solicitacao)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Tipo excluído com sucesso!'})
        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig)
            return jsonify({'status': 'error', 'message': error_message}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'Erro inesperado ao excluir o circuito.'}), 500
    else:
        # Se houver estudos associados, retorna erro
        return jsonify({
            'status': 'error', 
            'message': 'Não foi possível apagar, pois há um estudo com esse tipo de solicitação.'
        }), 400
    
@tipo_solicitacao_bp.route('/tipo_solicitacao/adicionar', methods=['POST'])
@requires_permission('criar')
def adicionar_circuito():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # Validação de campos obrigatórios
    campos_obrigatorios = ['viabilidade', 'analise', 'pedido']
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    
    if campos_faltantes:
        return jsonify({
            'status': 'error',
            'message': f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}'
        }), 400
    
    try:
        novo_tipo_solicitacao = TipoSolicitacao(
            viabilidade=data.get('viabilidade'),
            analise=data.get('analise'),
            pedido=data.get('pedido')
        )
        db.session.add(novo_tipo_solicitacao)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Tipo de solicitação adicionado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar tipo de solicitação: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

