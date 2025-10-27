from flask import Blueprint, render_template, request, jsonify
from app.models import db, Regional, EDP
from sqlalchemy.orm import joinedload
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.exc import IntegrityError

regionais_bp = Blueprint("regionais", __name__, template_folder="templates", static_folder="static", static_url_path='/regionais/static')

@regionais_bp.route("/regionais", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = Regional.query.all()
    
    registros = Regional.query.options(
        joinedload(Regional.edp)
    ).all()
    print(registros[0])
    
    usuario = get_usuario_logado()

    return render_template("listar_regionais.html", documentos=registros, usuario=usuario)

@regionais_bp.route('/regionais/<int:id>/editar', methods=['POST'])
@requires_permission('editar')
def editar_regionais(id):
    
    regionais = Regional.query.options(
        joinedload(Regional.edp)
    ).get_or_404(id)
    
    # CORREÇÃO: Verificar se é JSON ou FormData
    if request.is_json:
        data = request.get_json()
        print("Dados recebidos (JSON):", data)  # Para debug
    else:
        data = request.form.to_dict()
        print("Dados recebidos (Form):", data)  # Para debug
    
    # Atualiza os campos recebidos
    for campo, valor in data.items():
        if hasattr(regionais, campo):
            
            setattr(regionais, campo, valor)
    
    try:
        db.session.commit()
        print("Commit realizado com sucesso!")  # Para debug
        return jsonify({'status': 'success', 'message': 'Tipo atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no commit: {e}")  # Para debug
        return jsonify({'status': 'error', 'message': str(e)}), 500


@regionais_bp.route('/regionais/<int:id>/api', methods=['GET'])
def get_regionais_api(id):
    
    regionais = Regional.query.options(
        joinedload(Regional.edp)
    ).get_or_404(id)

    return jsonify({
        'id': regionais.id_regional,
        'regional': regionais.regional,
        "edp": regionais.edp.empresa if hasattr(regionais, 'edp') else None
    })


@regionais_bp.route('/regionais/<int:id>/excluir', methods=['POST'])
@requires_permission('excluir')
def excluir_regionais(id):
    regional = Regional.query.options(
        joinedload(Regional.edp)
    ).get_or_404(id)
    
    # ✅ Verifica se HÁ registros associados (qualquer um deles)
    tem_resp_regioes = bool(regional.resp_regioes)
    tem_estudos = bool(regional.estudos)
    tem_obras = bool(regional.obras)
    tem_municipios = bool(regional.municipios)
    
    print(f"🔍 Verificando dependências da Regional ID {id}:")
    print(f"   - Responsáveis de Região: {tem_resp_regioes}")
    print(f"   - Estudos: {tem_estudos}")
    print(f"   - Obras: {tem_obras}")
    print(f"   - Municípios: {tem_municipios}")
    
    # Se houver QUALQUER registro associado, bloqueia a exclusão
    if tem_resp_regioes or tem_estudos or tem_obras or tem_municipios:
        dependencias = []
        if tem_resp_regioes:
            dependencias.append("Responsáveis de Região")
        if tem_estudos:
            dependencias.append("Estudos")
        if tem_obras:
            dependencias.append("Obras")
        if tem_municipios:
            dependencias.append("Municípios")
        
        mensagem = (
            f"❌ Não é possível excluir esta regional!\n\n"
            f"Existem registros associados em:\n"
            f"• {', '.join(dependencias)}\n\n"
            f"⚠️ Remova todos os registros relacionados antes de excluir a regional."
        )
        
        return jsonify({
            'status': 'error',
            'message': mensagem
        }), 409  # ← Mudei para 409 (Conflict)
    
    # Se não houver dependências, pode excluir
    try:
        db.session.delete(regional)
        db.session.commit()
        print(f"✅ Regional ID {id} excluída com sucesso")
        return jsonify({
            'status': 'success',
            'message': 'Regional excluída com sucesso!'
        })
    
    except IntegrityError as e:
        db.session.rollback()
        error_message = str(e.orig)
        print(f"❌ IntegrityError: {error_message}")
        return jsonify({
            'status': 'error',
            'message': f'Erro de integridade: {error_message}'
        }), 409
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro inesperado: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Erro inesperado ao excluir a regional.'
        }), 500

    
@regionais_bp.route('/regionais/adicionar', methods=['POST'])
@requires_permission('criar')
def adicionar_regionais():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # Validação de campos obrigatórios
    campos_obrigatorios = ['regional', 'id_edp']  # ← Corrigido: 'nome' em vez de 'regional'
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    
    if campos_faltantes:
        return jsonify({
            'status': 'error',
            'message': f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}'
        }), 400
    
    try:
        nova_regional = Regional(
            regional=data.get('regional'),  # ← Nome da regional (vem do formulário)
            id_edp=data.get('id_edp')  # ← ID do EDP (Estado)
        )
        
        db.session.add(nova_regional)
        db.session.commit()
        
        return jsonify({
            'status': 'success', 
            'message': 'Regional adicionada com sucesso!'
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro ao adicionar regional: {e}")
        return jsonify({
            'status': 'error', 
            'message': str(e)
        }), 500

@regionais_bp.route('/regionais/edps/api', methods=['GET'])
def listar_edps():
    edps = EDP.query.all()
    return jsonify([
        {'id': edp.id_edp, 'empresa': edp.empresa}
        for edp in edps
    ])
    

