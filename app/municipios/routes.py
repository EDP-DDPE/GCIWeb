from app.models import Municipio, Regional
from flask import Blueprint, render_template, jsonify
from sqlalchemy.orm import joinedload
from app.auth import requires_permission, get_usuario_logado


municipio_bp = Blueprint("municipios", __name__, template_folder="templates", static_folder="static", static_url_path='/municipios/static')

@municipio_bp.route("/municipios", methods=["GET"])
@requires_permission('visualizar')
def listar_municipios():

    # Buscar todos os circuitos COM relacionamentos (evita N+1 queries)
    registros = Municipio.query.options(
            joinedload(Municipio.edp),
            joinedload(Municipio.regional)
    ).all()
    
    usuario = get_usuario_logado()

    return render_template("listar_municipios.html", documentos=registros, usuario=usuario)

@municipio_bp.route('/municipios/<int:id>/editar', methods=['POST'])
def editar_municipio(id):
    municipio = Municipio.query.get_or_404(id)
    
    # CORREÇÃO: Verificar se é JSON ou FormData
    if request.is_json:
        data = request.get_json()
        print("Dados recebidos (JSON):", data)  # Para debug
    else:
        data = request.form.to_dict()
        print("Dados recebidos (Form):", data)  # Para debug
    
    # Atualiza os campos recebidos
    for campo in data:
        if hasattr(municipio, campo):
            print(f"Atualizando {campo}: {getattr(municipio, campo)} -> {data[campo]}")  # Para debug
            setattr(municipio, campo, data[campo])
    
    try:
        db.session.commit()
        print("Commit realizado com sucesso!")  # Para debug
        return jsonify({'status': 'success', 'message': 'Circuito atualizado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro no commit: {e}")  # Para debug
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@municipio_bp.route('/municipios/<int:id>/api', methods=['GET'])
def get_municipio_api(id):
    municipio = Municipio.query.options(
        joinedload(Municipio.edp),
        joinedload(Municipio.regional)
    ).get_or_404(id)

    return jsonify({
        'id': municipio.id_municipio,
        'municipio': municipio.municipio,
        'edp': {
            'empresa': municipio.edp.empresa if municipio.edp else None
        } if municipio.edp else None,
        'regional': {
            'regional': municipio.regional.regional if municipio.regional else None
        } if municipio.regional else None
    })

@municipio_bp.route('/municipios/<int:id_estado>/api', methods=['GET'])
def listar_regionais_por_estado(id_estado):
    # Busca todas as regionais deste estado
    regionais = Regional.query.filter_by(id_edp=id_estado).all()
    
    return jsonify([
        {"id": r.id_regional, "": r.regional}
        for r in regionais
    ])