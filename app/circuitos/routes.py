from flask import Blueprint, render_template, request, jsonify
from app.models import Circuito, db, EDP, Subestacao
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.orm import joinedload

circuito_bp = Blueprint("circuitos", __name__, template_folder="templates", static_folder="static", static_url_path='/circuitos/static')

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


    return render_template("listar_circuitos.html", documentos=registros, usuario=usuario)

@circuito_bp.route('/circuitos/<int:id>/editar', methods=['POST'])
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

@circuito_bp.route('/circuitos/<int:id>/api', methods=['GET'])
def get_circuito_api(id):
    circuito = Circuito.query.options(
        joinedload(Circuito.subestacao),
        joinedload(Circuito.edp)
    ).get_or_404(id)

    return jsonify({
        'id': circuito.id_circuito,
        'circuito': circuito.circuito,
        'tensao': circuito.tensao,
        'subestacao': {
            'nome': circuito.subestacao.nome if circuito.subestacao else None
        } if circuito.subestacao else None,
        'edp': {
            'empresa': circuito.edp.empresa if circuito.edp else None
        } if circuito.edp else None
    })

@circuito_bp.route('/circuitos/<int:id>/excluir', methods=['POST'])
def excluir_circuito(id):
    circuito = Circuito.query.get_or_404(id)
    try:
        db.session.delete(circuito)
        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@circuito_bp.route('/circuitos/adicionar', methods=['POST'])
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
    
@circuito_bp.route('/circuitos/edps/api', methods=['GET'])
def listar_edps():
    edps = EDP.query.all()
    return jsonify([
        {'id': edp.id_edp, 'empresa': edp.empresa}
        for edp in edps
    ])

@circuito_bp.route('/circuitos/subestacoes/api', methods=['GET'])
def listar_subestacoes():
    subestacoes = Subestacao.query.all()
    return jsonify([
        {'id': subestacao.id_subestacao, 'nome': subestacao.nome, 'sigla': subestacao.sigla}
        for subestacao in subestacoes
    ])

@circuito_bp.route('/circuitos/subestacoes/api/<int:edp_id>', methods=['GET'])
def listar_subestacoes_por_edp(edp_id):
    subestacoes = Subestacao.query.filter_by(id_edp=edp_id).all()
    return jsonify([
        {
            'id': subestacao.id_subestacao,
            'nome': subestacao.nome,
            'sigla': subestacao.sigla
        }
        for subestacao in subestacoes
    ])

