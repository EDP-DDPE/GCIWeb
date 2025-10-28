from flask import Blueprint, render_template, jsonify
from app.models import Empresa
from app.auth import requires_permission, get_usuario_logado

empresas_bp = Blueprint("empresas", __name__, template_folder="templates", static_folder="static", static_url_path='/empresas/static')

@empresas_bp.route("/empresas", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():

    registros = Empresa.query.all()
    
    usuario = get_usuario_logado()
    
    return render_template("listar_empresas.html",documentos=registros,usuario=usuario)

@empresas_bp.route('/empresas/<int:id>/api', methods=['GET'])
def api_empresa(id):
    emp = Empresa.query.get_or_404(id)
    return jsonify({
        "id": emp.id_empresa,
        "nome_empresa": emp.nome_empresa,
        "cnpj": emp.cnpj,
        "abertura": emp.abertura,
        "situacao": emp.situacao,
        "tipo": emp.tipo,
        "porte": emp.porte,
        "natureza_juridica": emp.natureza_juridica,
        "logradouro": emp.logradouro,
        "numero": emp.numero,
        "complemento": emp.complemento,
        "municipio": emp.municipio,
        "bairro": emp.bairro,
        "uf": emp.uf,
        "cep": emp.cep,
        "email": emp.email,
        "telefone": emp.telefone,
        "data_situacao": emp.data_situacao,
        "ultima_atualizacao": emp.ultima_atualizacao,
        "status": emp.status,
        "fantasia": emp.fantasia,
        "efr": emp.efr,
        "motivo_situacao": emp.motivo_situacao,
        "situacao_especial": emp.situacao_especial,
        "data_situacao_especial": emp.data_situacao_especial,
    })
