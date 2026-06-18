import json
import datetime as dt
from io import BytesIO, StringIO

from flask import Blueprint, render_template, request, jsonify, Response, g
from sqlalchemy import or_, String
from sqlalchemy.orm import load_only
from app.models import db, Estudo, StatusTipo, StatusEstudo, ViewEstudos
from app.auth import requires_permission, get_usuario_logado
# Reaproveita o mesmo mapa de colunas do listar (ambos consultam a view
# vw_estudos_completos), para oferecer as mesmas colunas/filtros.
from app.listar.routes import COLUMN_MAP


gestao_bp = Blueprint("gestao", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/gestao/static')

# Análises aceitas na esteira de aprovação do gestor.
ANALISES_ACEITAS = ['MMGD', 'Carga', 'DAL', 'Carga e MMGD', 'Carga e Autoprodutor',
                    'Autoprodutor', 'Produtor Independente']

VALOR_MINIMO_PADRAO = 1_000_000.00


def _base_query_aprovacao(valor_minimo):
    """Estudos elegíveis para aprovação: a alternativa escolhida tem custo
    modular acima do mínimo e a análise está na lista aceita.

    Usa a view plana (1 linha por alternativa); ao filtrar a alternativa
    escolhida, resulta em 1 linha por estudo — rápido e sem N+1.
    """
    return db.session.query(ViewEstudos).filter(
        ViewEstudos.flag_alternativa_escolhida == 1,
        ViewEstudos.custo_modular >= valor_minimo,
        ViewEstudos.analise.in_(ANALISES_ACEITAS),
    )


def _classificar_status(status):
    s = (status or "").strip()
    if s in ("Aprovado", "Aprovado Gestor"):
        return "Aprovado"
    if s in ("Reprovado", "Reprovado Gestor", "Rejeitado Gestor"):
        return "Reprovado"
    return "Pendente"


@gestao_bp.route("/gestao/aprovacao", methods=["GET"])
@requires_permission('aprovar')
def gestao_aprovacao():
    """Shell leve da página. Os dados vêm via /gestao/api/aprovacao (paginado)."""
    valor_minimo = request.args.get("min_valor", VALOR_MINIMO_PADRAO, type=float)
    usuario = get_usuario_logado()
    status_tipos = StatusTipo.query.all()
    return render_template(
        "gestao/aprov.html",
        usuario=usuario,
        status_tipos=status_tipos,
        valor_minimo=valor_minimo,
    )


@gestao_bp.get("/gestao/api/aprovacao")
@requires_permission('aprovar')
def api_aprovacao():
    """Lista paginada dos estudos para aprovação (mesma mecânica do listar):
    busca global, filtro por coluna, ordenação, seleção de colunas e export."""
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=25, type=int)
    search = request.args.get("search", default="", type=str)
    sort_column = request.args.get("sort", default="custo_modular", type=str)
    sort_dir = request.args.get("direction", default="desc", type=str)
    valor_minimo = request.args.get("min_valor", VALOR_MINIMO_PADRAO, type=float)
    export_format = request.args.get("export")

    raw_cols = request.args.get("columns")
    columns_requested = []
    if raw_cols:
        columns_requested = [c.strip() for c in raw_cols.split(",")
                             if c.strip() in COLUMN_MAP]
    columns_requested = [c for c in columns_requested if c != "acoes"]
    selected_keys = columns_requested if columns_requested else list(COLUMN_MAP.keys())

    column_filters = json.loads(request.args.get("filters", "{}"))

    db_columns = [COLUMN_MAP[k] for k in selected_keys if k in COLUMN_MAP and k != "acoes"]
    # garante colunas necessárias para ações/status mesmo se não selecionadas
    for obrig in ("id_estudo", "ultimo_status", COLUMN_MAP.get(sort_column, "id_estudo")):
        if obrig not in db_columns:
            db_columns.append(obrig)

    query = _base_query_aprovacao(valor_minimo).options(
        load_only(*[getattr(ViewEstudos, c) for c in db_columns])
    )

    # Busca global
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            ViewEstudos.num_doc.ilike(like),
            ViewEstudos.nome_projeto.ilike(like),
            ViewEstudos.empresa.ilike(like),
            ViewEstudos.municipio.ilike(like),
            ViewEstudos.nome_responsavel.ilike(like),
            ViewEstudos.id_estudo.cast(String).ilike(like),
        ))

    # Filtro por coluna
    for col, value in column_filters.items():
        if not value:
            continue
        column_name = COLUMN_MAP.get(col)
        if not column_name:
            continue
        column_obj = getattr(ViewEstudos, column_name)
        if isinstance(column_obj.type, String):
            query = query.filter(column_obj.ilike(f"%{value}%"))
        else:
            query = query.filter(column_obj == value)

    # Ordenação
    sort_obj = getattr(ViewEstudos, COLUMN_MAP.get(sort_column, "custo_modular"))
    query = query.order_by(sort_obj.desc() if sort_dir == "desc" else sort_obj.asc())

    if export_format:
        rows = query.all()
        has_next = False
    else:
        offset = (page - 1) * per_page
        rows = query.offset(offset).limit(per_page + 1).all()
        has_next = len(rows) > per_page
        rows = rows[:per_page]

    if "acoes" not in selected_keys:
        selected_keys.append("acoes")

    permissoes = {
        "aprovar": bool(g.user.aprovar or g.user.admin),
        "visualizar": bool(g.user.visualizar or g.user.admin),
    }

    items = []
    for e in rows:
        record = {}
        for key in selected_keys:
            column = COLUMN_MAP[key]
            value = getattr(e, column, None)
            if hasattr(value, "strftime"):
                value = value.strftime("%d/%m/%Y")
            record[key] = value
        record["id_estudo"] = getattr(e, "id_estudo", None)
        record["ultimo_status"] = getattr(e, "ultimo_status", None)
        record["_permissoes"] = permissoes
        items.append(record)

    if export_format:
        return _exportar(export_format, items, columns_requested or selected_keys)

    return jsonify({
        "page": page,
        "per_page": per_page,
        "has_next": has_next,
        "items": items,
    })


@gestao_bp.get("/gestao/api/resumo")
@requires_permission('aprovar')
def api_resumo():
    """Resumo (aprovado/reprovado/pendente) sobre TODOS os estudos que batem
    no filtro — calculado no servidor por agregação barata."""
    valor_minimo = request.args.get("min_valor", VALOR_MINIMO_PADRAO, type=float)
    rows = _base_query_aprovacao(valor_minimo).with_entities(ViewEstudos.ultimo_status).all()
    resumo = {"Aprovado": 0, "Reprovado": 0, "Pendente": 0}
    for (status,) in rows:
        resumo[_classificar_status(status)] += 1
    resumo["total"] = sum(v for k, v in resumo.items())
    return jsonify(resumo)


def _exportar(export_format, items, colunas):
    colunas = [c for c in colunas if c != "acoes"]
    if export_format == "csv":
        import csv
        output = StringIO()
        writer = csv.writer(output, delimiter=";")
        writer.writerow(colunas)
        for e in items:
            writer.writerow([e.get(col, "") for col in colunas])
        return Response(output.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=aprovacao_export.csv"})

    if export_format == "xlsx":
        import pandas as pd
        df = pd.DataFrame([{c: e.get(c, "") for c in colunas} for e in items])
        output = BytesIO()
        df.to_excel(output, index=False)
        return Response(output.getvalue(),
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": "attachment;filename=aprovacao_export.xlsx"})

    if export_format == "pdf":
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("DejaVu", "", "app/main/static/fonts/NotoSans-Regular.ttf", uni=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.set_fill_color(230, 230, 230)
        for col in colunas:
            pdf.cell(60, 8, col.replace("_", " ").title(), 1, 0, "L", True)
        pdf.ln()
        for e in items:
            for col in colunas:
                pdf.cell(60, 8, str(e.get(col, ""))[:60], 1)
            pdf.ln()
        pdf_bytes = pdf.output(dest="S").encode("latin-1", "replace")
        return Response(pdf_bytes, mimetype="application/pdf",
                        headers={"Content-Disposition": "attachment; filename=aprovacao_export.pdf"})

    return Response("Formato inválido", status=400)

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
    if not tipo:
        return jsonify({"success": False,
                        "message": f"Tipo de status '{status}' não cadastrado."}), 400

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