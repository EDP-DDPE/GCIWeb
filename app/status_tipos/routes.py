from flask import Blueprint, render_template, request, jsonify
from app.models import db, StatusTipo
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.exc import IntegrityError

status_tipos_bp = Blueprint("status_tipos", __name__, template_folder="templates", static_folder="static", static_url_path='/status_tipos/static')

@status_tipos_bp.route("/status_tipos", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    
    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = StatusTipo.query.all()
    print(registros[0])
    
    usuario = get_usuario_logado()

    return render_template("listar_status_tipos.html", documentos=registros, usuario=usuario)

@status_tipos_bp.route('/status_tipos/<int:id>/editar', methods=['POST'])
@requires_permission('editar')
def editar_status_tipos(id):
    tipo_status = StatusTipo.query.get_or_404(id) 
    # CORREÇÃO: Verificar se é JSON ou FormData
    if request.is_json:
        data = request.get_json()
        print("Dados recebidos (JSON):", data)  # Para debug
    else:
        data = request.form.to_dict()
        print("Dados recebidos (Form):", data)  # Para debug
    
    # Atualiza os campos recebidos
    for campo, valor in data.items():
        if hasattr(tipo_status, campo):
            print(f"Atualizando {campo}: {getattr(tipo_status, campo)} -> {valor}")  # Para debug
            
            # CONVERSÃO ESPECIAL PARA O CAMPO ATIVO
            if campo == 'ativo':
                valor = bool(int(valor))  # Converte '1' -> True, '0' -> False
            
            setattr(tipo_status, campo, valor)
    
    try:
        db.session.commit()
        print("Commit realizado com sucesso!")  # Para debug
        return jsonify({'status': 'success', 'message': 'Tipo atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no commit: {e}")  # Para debug
        return jsonify({'status': 'error', 'message': str(e)}), 500


@status_tipos_bp.route('/status_tipos/<int:id>/api', methods=['GET'])
def get_status_tipos_api(id):
    tipo_status = StatusTipo.query.get_or_404(id)

    return jsonify({
        'id': tipo_status.id_status_tipo,
        'status': tipo_status.status,
        'descricao': tipo_status.descricao,
        'ativo': tipo_status.ativo
    })


@status_tipos_bp.route('/status_tipos/<int:id>/excluir', methods=['POST'])
@requires_permission('excluir')
def excluir_circuito_status_tipos(id):
    tipo_status = StatusTipo.query.get_or_404(id)
    
    # Verifica se NÃO há estudos associados
    if not tipo_status.status_estudos:
        try:
            db.session.delete(tipo_status)
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
            'message': 'Não foi possível apagar, pois há um status de estudo com esse tipo de status.'
        }), 400
    
@status_tipos_bp.route('/status_tipos/adicionar', methods=['POST'])
@requires_permission('criar')
def adicionar_circuito_status_tipos():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    # Validação de campos obrigatórios
    campos_obrigatorios = ['status', 'descricao', 'ativo']
    campos_faltantes = [campo for campo in campos_obrigatorios if not data.get(campo)]
    
    if campos_faltantes:
        return jsonify({
            'status': 'error',
            'message': f'Campos obrigatórios faltando: {", ".join(campos_faltantes)}'
        }), 400
    
    try:
        ativo = request.form.get('ativo')
        
        # Converte string '1' ou '0' para boolean True ou False
        ativo_bool = bool(int(ativo)) if ativo else False
        novo_tipo_status = StatusTipo(
            status=data.get('status'),
            descricao=data.get('descricao'),
            ativo=ativo_bool
        )
        db.session.add(novo_tipo_status)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Tipo de status adicionado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao adicionar tipo de status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

