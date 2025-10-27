from flask import Blueprint, render_template, request, jsonify, current_app
from app.models import db, RespRegiao, Regional, Usuario
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from datetime import date

resp_regioes_bp = Blueprint("resp_regioes", __name__, template_folder="templates", static_folder="static",
                           static_url_path='/resp_regioes/static')


# ---------- Helpers ----------
def _is_ajax():
    # considerar fetch com header 'X-Requested-With'
    return request.headers.get("X-Requested-With") == "XMLHttpRequest" or \
        "application/json" in request.headers.get("Accept", "")


def _json_ok(message="OK", **extra):
    payload = {"success": True, "message": message}
    payload.update(extra)
    return jsonify(payload), 200


def _json_err(message="Erro", status=400, **extra):
    payload = {"success": False, "message": message}
    payload.update(extra)
    return jsonify(payload), status


def _validate_payload(form_or_json):
    # aceita JSON (`get_json`) ou FormData (`request.form`)
    data = form_or_json or {}
    # normaliza para dict
    if hasattr(data, "to_dict"):
        data = data.to_dict()

    id_regional = data.get("id_regional")
    id_usuario = data.get("id_usuario")
    ano_ref = data.get("ano_ref")

    # cast
    try:
        id_regional = int(id_regional) if id_regional not in (None, "",) else None
        id_usuario = int(id_usuario) if id_usuario not in (None, "",) else None
        ano_ref = int(ano_ref) if ano_ref not in (None, "",) else None
    except ValueError:
        return None, "Campos numéricos inválidos."

    if not id_regional:
        return None, "Selecione uma regional."
    if not id_usuario:
        return None, "Selecione um usuário."
    if not ano_ref:
        return None, "Selecione o ano."

    return {"id_regional": id_regional, "id_usuario": id_usuario, "ano_ref": ano_ref}, None


# ---------- LISTAR ----------
@resp_regioes_bp.route("/responsavel", methods=["GET"])
@requires_permission("visualizar")
def listar():
    """
    Renderiza a tabela com todos os vínculos RespRegiao.
    O front (JS) faz busca/ordenação/paginação no cliente.
    """
    usuario = get_usuario_logado()

    if not usuario.admin:
        # Carrega tudo com eager loading
        registros = (
            db.session.query(RespRegiao)
            .join(RespRegiao.regional)
            .join(RespRegiao.usuario)
            .options(
                # lazy='joined' já está no model, mas garantimos:
                # Carrega dados relacionados na mesma query
            )
            .filter_by(id_usuario=usuario.id_usuario)
            .order_by(RespRegiao.id_resp_regiao.desc())
            .all()
        )

        # Listas para os selects do modal/filtros
        regionais = Regional.query.filter_by(id_edp=usuario.id_edp).order_by(Regional.regional.asc()).all()
        usuarios = Usuario.query.filter_by(id_usuario=usuario.id_usuario).order_by(Usuario.nome.asc()).all()
    else:

        # Carrega tudo com eager loading
        registros = (
            db.session.query(RespRegiao)
            .join(RespRegiao.regional)
            .join(RespRegiao.usuario)
            .options(
                # lazy='joined' já está no model, mas garantimos:
                # Carrega dados relacionados na mesma query
            )
            .order_by(RespRegiao.id_resp_regiao.desc())
            .all()
        )

        # Listas para os selects do modal/filtros
        regionais = Regional.query.order_by(Regional.regional.asc()).all()
        usuarios = Usuario.query.order_by(Usuario.nome.asc()).all()

    y = date.today().year
    anos = [y - 2, y - 1, y, y + 1, y + 2]

    return render_template(
        "resp_regioes/resp_regiao.html",
        documentos=registros,  # o HTML usa 'documentos' no tbody
        regionais=regionais,
        usuarios=usuarios,
        anos=anos,
        usuario=usuario
    )


# ---------- CRIAR ----------
@resp_regioes_bp.route("/resp_regioes/criar", methods=["POST"])
@requires_permission("criar")
def criar():
    # aceita FormData (fetch + FormData) e JSON
    payload, err = _validate_payload(request.get_json(silent=True) or request.form)
    if err:
        return _json_err(err, status=400)

    # Prevenir duplicidade do mesmo trio (id_regional, id_usuario, ano_ref)
    existe = db.session.query(RespRegiao).filter(
        and_(
            RespRegiao.id_regional == payload["id_regional"],
            RespRegiao.id_usuario == payload["id_usuario"],
            RespRegiao.ano_ref == payload["ano_ref"],
        )
    ).first()

    if existe:
        return _json_err("Já existe um vínculo para este Usuário/Regional/Ano.", status=409)

    try:
        novo = RespRegiao(
            id_regional=payload["id_regional"],
            id_usuario=payload["id_usuario"],
            ano_ref=payload["ano_ref"]
        )
        db.session.add(novo)
        db.session.commit()
        return _json_ok("Vínculo criado com sucesso.", id=novo.id_resp_regiao)
    except IntegrityError:
        db.session.rollback()
        return _json_err("Erro de integridade ao criar o vínculo.", status=400)
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception("Erro ao criar RespRegiao")
        return _json_err("Erro interno ao criar o vínculo.", status=500)


# ---------- EDITAR ----------
@resp_regioes_bp.route("/resp_regioes/<int:id>/editar", methods=["POST"])
@requires_permission("editar")
def editar(id):
    registro = db.session.get(RespRegiao, id)
    if not registro:
        return _json_err("Vínculo não encontrado.", status=404)

    payload, err = _validate_payload(request.get_json(silent=True) or request.form)
    if err:
        return _json_err(err, status=400)

    # Prevenir duplicidade (exclui o próprio id)
    existe = db.session.query(RespRegiao).filter(
        and_(
            RespRegiao.id_regional == payload["id_regional"],
            RespRegiao.id_usuario == payload["id_usuario"],
            RespRegiao.ano_ref == payload["ano_ref"],
            RespRegiao.id_resp_regiao != id
        )
    ).first()
    if existe:
        return _json_err("Já existe um vínculo para este Usuário/Regional/Ano.", status=409)

    try:
        registro.id_regional = payload["id_regional"]
        registro.id_usuario = payload["id_usuario"]
        registro.ano_ref = payload["ano_ref"]
        db.session.commit()
        return _json_ok("Vínculo atualizado com sucesso.")
    except IntegrityError:
        db.session.rollback()
        return _json_err("Erro de integridade ao atualizar o vínculo.", status=400)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao editar RespRegiao")
        return _json_err("Erro interno ao atualizar o vínculo.", status=500)


# ---------- EXCLUIR ----------
@resp_regioes_bp.route("/resp_regioes/<int:id>/excluir", methods=["POST"])
@requires_permission("editar")
def excluir(id):
    registro = db.session.get(RespRegiao, id)

    if registro.estudos:
        return _json_err("Não foi possível excluir. Já existe um Estudo com este responsável.", status=400)

    if not registro:
        return _json_err("Vínculo não encontrado.", status=404)

    try:
        db.session.delete(registro)
        db.session.commit()
        return _json_ok("Vínculo excluído com sucesso.")
    except IntegrityError:
        db.session.rollback()
        return _json_err("Não foi possível excluir (restrição de integridade).", status=400)
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Erro ao excluir RespRegiao")
        return _json_err("Erro interno ao excluir o vínculo.", status=500)
