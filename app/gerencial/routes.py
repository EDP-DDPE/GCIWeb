import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, send_from_directory, \
    abort, flash
from werkzeug.utils import safe_join
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo, Alternativa, TipoSolicitacao
from app.auth import requires_permission, get_usuario_logado
from sqlalchemy.orm import joinedload
import os
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_, not_
from app.models import db, Estudo, Alternativa, StatusTipo, StatusEstudo
import datetime as dt
from flask import jsonify
from sqlalchemy import func, and_, not_, select, literal_column, exists
from sqlalchemy.orm import aliased


gestao_bp = Blueprint("gestao", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/gestao/static')


@gestao_bp.route("/gestao/aprovacao", methods=["GET"])
@requires_permission('aprovar')
def gestao_aprovacao():
    valor_minimo = request.args.get("min_valor", 1_000_000.00, type=float)

    # Subfiltros de status
    nomes_bloqueados = ["Aprovado", "Reprovado"]  # já decididos
    analises_aceitas = ['MMGD','Carga']
    nome_reenvio = "Reenviado para aprovação"

    rn = func.row_number().over(
        partition_by=StatusEstudo.id_estudo,
        order_by=StatusEstudo.data.desc()
    ).label("rn")

    st_win = (
        select(
            StatusEstudo.id_estudo.label("id_estudo"),
            StatusEstudo.id_status_tipo.label("id_status_tipo"),
            rn
        )
        .subquery()
    )

    st_ult = aliased(st_win)
    st_tipo = aliased(StatusTipo)

    ultimo_status_bloqueado_exists = exists(
        select(1)
        .select_from(st_ult)
        .join(st_tipo, st_tipo.id_status_tipo == st_ult.c.id_status_tipo)
        .where(
            and_(
                st_ult.c.id_estudo == Estudo.id_estudo,
                st_ult.c.rn == 1,  # último
                st_tipo.status.in_(nomes_bloqueados),
            )
        )
    )




    estudos = (
        Estudo.query
        .join(Estudo.alternativas)
        .join(Estudo.tipo_solicitacao)
        .filter(
            Alternativa.flag_alternativa_escolhida == 1,          # alternativa escolhida
            Alternativa.custo_modular >= valor_minimo,            # custo mínimo
            # NÃO pode já ter status final de gestor:
            #not_(ultimo_status_bloqueado_exists),
            # # NÃO pode estar marcado como Reenvio para aprovação:
            TipoSolicitacao.analise.in_(analises_aceitas)

        )
        .options(
            joinedload(Estudo.alternativas),
            joinedload(Estudo.status_estudos).joinedload(StatusEstudo.status_tipo)
        )
        .all()
    )

    usuario = get_usuario_logado()
    status_tipos = StatusTipo.query.all()

    # Pré-calcular contagem para o gráfico (evita lógica no Jinja)
    def status_do_estudo(e: Estudo):
        # regra simples: se tem Aprovado/Rejeitado Gestor no histórico (em tese não terá aqui),
        # senão considerar "Pendente"
        nomes = [se.status_tipo.status for se in e.status_estudos if se.status_tipo and se.status_tipo.status]
        if "Aprovado" in nomes:
            return "Aprovado"
        if "Reprovado" in nomes:
            return "Reprovado"
        return "Pendente"

    resumo = {"Aprovado": 0, "Reprovado": 0, "Pendente": 0}
    for e in estudos:
        resumo[status_do_estudo(e)] += 1

    return render_template(
        "gestao/aprov.html",
        documentos=estudos,
        usuario=usuario,
        status_tipos=status_tipos,
        valor_minimo=valor_minimo,
        resumo=resumo,
    )

@gestao_bp.route("/gestao/aprovacao/<int:id_estudo>/status", methods=["POST"])
@requires_permission('aprovar')
def gestao_aprovacao_status(id_estudo):
    user = get_usuario_logado()
    estudo = Estudo.query.get_or_404(id_estudo)
    payload = request.get_json(force=True) or {}
    status = payload.get("status", "").strip()
    comentario = payload.get("comentario", "").strip() or None

    if not status:
        return jsonify({"success": False, "message": "Status inválido."}), 400

    tipo = StatusTipo.query.filter_by(status=status).first()

    # Evitar duplicidade de decisão final
    # if status in ("Aprovado", "Reprovado"):
    #     ja_finalizado = any(
    #         (se.status_tipo and se.status_tipo.status in ("Aprovado", "Reprovado"))
    #         for se in estudo.status_estudos
    #     )
    #     if ja_finalizado:
    #         return jsonify({"success": False, "message": "Este estudo já foi decidido pelo Gestor."}), 400

    novo = StatusEstudo(
        id_estudo=estudo.id_estudo,
        data=dt.datetime.utcnow(),
        id_status_tipo=tipo.id_status_tipo,
        observacao=comentario,
        id_criado_por=user.id_usuario
    )
    db.session.add(novo)
    db.session.commit()

    return jsonify({"success": True, "message": f"Status '{status}' registrado."})