from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.models import StatusEstudo, StatusTipo, Usuario, db
from app.auth import requires_permission, get_usuario_logado


status_bp = Blueprint("status", __name__, template_folder="templates", static_folder="static", static_url_path='/status/static')


@status_bp.route("/estudos/<int:id_estudo>/status/", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar_status(id_estudo):
    status = (
        db.session.query(StatusEstudo)
        .filter_by(id_estudo=id_estudo)
        .join(StatusTipo)
        .join(Usuario)
        .order_by(StatusEstudo.data.desc())
        .all()
    )

    print(status)

    return jsonify([
        {
            "id_status": s.id_status,
            "data": s.data.strftime("%d/%m/%Y %H:%M"),
            "status_tipo": s.status_tipo.status,
            "id_status_tipo": s.id_status_tipo,
            "observacao": s.observacao,
            "criado_por": s.criado_por.nome
        }
        for s in status
    ])


@status_bp.route("/estudos/<int:id_estudo>/status/save", methods=["POST"])
def salvar_status(id_estudo):
    id_status = request.form.get("id_status")
    id_status_tipo = request.form["id_status_tipo"]
    observacao = request.form.get("observacao")
    usuario = get_usuario_logado()

    if id_status:  # edição
        status = StatusEstudo.query.get(id_status)
        status.id_status_tipo = id_status_tipo
        status.observacao = observacao
    else:  # novo
        status = StatusEstudo(
            id_estudo=id_estudo,
            id_status_tipo=id_status_tipo,
            observacao=observacao,
            id_criado_por=usuario.id_usuario,
        )
        db.session.add(status)

    db.session.commit()
    return jsonify({"success": True})


@status_bp.route("/status/excluir/<int:id_status>", methods=["DELETE"])
def excluir_status(id_status):
    try:
        user = get_usuario_logado()
        status = StatusEstudo.query.get_or_404(id_status)
        if user.admin or user.id_usuario == status.id_criado_por:
            db.session.delete(status)
            db.session.commit()
        else:
            raise NameError
    except NameError:
        return jsonify({
            'success': False,
            'message': f'Você não tem permissão para deletar esse status.'
        }), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir status: {str(e)}'
        }), 500