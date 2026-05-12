from flask import Blueprint, render_template, request, jsonify
from models import Subestacao, Municipio, EDP
from database import db
from sqlalchemy.orm import joinedload
from auth import requires_permission, get_usuario_logado
from sqlalchemy.exc import IntegrityError

subestacao_bp = Blueprint("subestacoes", __name__, template_folder="templates", static_folder="static", static_url_path='/subestacoes/static')

@subestacao_bp.route("/subestacoes", methods=["GET", "POST"])
#@requires_permission('visualizar')
def listar_subestacoes():

    registros = Subestacao.query.options(
        joinedload(Subestacao.municipio),
        joinedload(Subestacao.circuitos)
    ).all()
    
    usuario = get_usuario_logado()
    
    return render_template("listar_subestacoes.html",documentos=registros,usuario=usuario)

@subestacao_bp.route('/subestacoes/<int:id>/api', methods=['GET'])
def api_subestacao(id):
    sub = Subestacao.query.get_or_404(id)
    return jsonify({
        "id": sub.id_subestacao,
        "nome": sub.nome,
        "sigla": sub.sigla,
        "id_municipio": sub.id_municipio,
        "id_edp": sub.id_edp,
        "lat": sub.lat,
        # Caso o campo correto seja 'long' e não 'longitude':
        "longitude": getattr(sub, 'long', None),
        "municipio": sub.municipio.municipio if hasattr(sub, 'municipio') else None,
        "edp": sub.edp.empresa if hasattr(sub, 'edp') else None
    })


@subestacao_bp.route('/subestacoes/<int:id>/editar', methods=['POST'])
#@requires_permission('editar')
def editar_subestacao(id):
    sub = Subestacao.query.get_or_404(id)
    
    # ✅ Verifica tipo de requisição (JSON ou Form)
    if request.is_json:
        data = request.get_json()
        print("📨 Dados recebidos (JSON):", data)
    else:
        data = request.form.to_dict()
        print("📨 Dados recebidos (FormData):", data)
    
    # ✅ Mapeamento de campos (frontend -> banco)
    mapeamento_campos = {
        'nome': 'nome',
        'sigla': 'sigla',
        'id_municipio': 'id_municipio',
        'id_edp': 'id_edp',
        'lat': 'lat',
        'longitude': 'long'  # ← MAPEAMENTO AQUI
    }
    
    for campo_frontend, campo_banco in mapeamento_campos.items():
        if campo_frontend in data:
            valor = data[campo_frontend]
            if hasattr(sub, campo_banco):
                print(f"✏️ Atualizando {campo_banco}: {getattr(sub, campo_banco)} -> {valor}")
                setattr(sub, campo_banco, valor)
    
    try:
        db.session.commit()
        print("✅ Commit bem-sucedido")
        return jsonify({'status': 'success', 'message': 'Subestação atualizada com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print("❌ Erro no commit:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 🔹 1. Página/modal de novo cadastro
@subestacao_bp.route("/subestacoes/nova", methods=["GET", "POST"])
def nova_subestacao():
    municipios = Municipio.query.all()
    edps = EDP.query.all()

    if request.method == "POST":
        data = request.get_json() or request.form

        nome = data.get("nome")
        sigla = data.get("sigla")
        id_municipio = data.get("id_municipio")
        id_edp = data.get("id_edp")
        lat = data.get("lat")
        longitude = data.get("longitude")

        if not all([nome, sigla, id_municipio, id_edp]):
            return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

        nova = Subestacao(
            nome=nome.strip(),
            sigla=sigla.strip(),
            id_municipio=int(id_municipio),
            id_edp=int(id_edp),
            lat=lat.strip(),
            long=longitude.strip()
        )
        db.session.add(nova)
        db.session.commit()

        return jsonify({"msg": "Subestação cadastrada com sucesso!"}), 201

    return render_template("nova_subestacao.html", municipios=municipios, edps=edps)


# 🔹 2. Endpoint para listar EDPs
@subestacao_bp.route("/subestacoes/edps/api", methods=["GET"])
def listar_edps():
    edps = EDP.query.all()
    return jsonify([
        {"id": e.id_edp, "empresa": e.empresa}
        for e in edps
    ])


# 🔹 3. Endpoint para listar municípios por EDP
@subestacao_bp.route("/subestacoes/municipios/api/<int:edp_id>", methods=["GET"])
def listar_municipios_por_edp(edp_id):
    municipios = Municipio.query.filter_by(id_edp=edp_id).all()
    return jsonify([
        {"id": m.id_municipio, "municipio": m.municipio}
        for m in municipios
    ])

@subestacao_bp.route('/subestacoes/<int:id>/excluir', methods=['POST'])
#@requires_permission('excluir')
def excluir_circuito_status_tipos(id):
    subestacao = Subestacao.query.get_or_404(id)
    
    # Verifica se NÃO há estudos associados
    if not subestacao.circuitos:
        try:
            db.session.delete(subestacao)
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
            'message': 'Não foi possível apagar, pois há um circuito nessa subestação.'
        }), 400