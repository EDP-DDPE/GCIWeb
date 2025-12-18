import json

from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, send_from_directory, \
    abort, flash, jsonify, g, Response, send_file
from sqlalchemy import or_, String
from werkzeug.utils import safe_join
from app.models import listar_estudos, obter_estudo, Estudo, StatusTipo, ViewEstudos, db, Alternativa, Anexo, StatusEstudo
from app.auth import requires_permission, get_usuario_logado
import os
from io import BytesIO
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import pytz

listar_bp = Blueprint("listar", __name__, template_folder="templates",
                      static_folder="static", static_url_path='/listar/static')

COLUMN_MAP = {
    "id_estudo": "id_estudo",
    "num_doc": "num_doc",
    "protocolo": "protocolo",
    "nome_projeto": "nome_projeto",
    "descricao": "descricao",
    "instalacao": "instalacao",
    "n_alternativas": "n_alternativas",
    "latitude_cliente": "latitude_cliente",
    "longitude_cliente": "longitude_cliente",
    "observacao": "observacao",
    "empresa": "empresa",
    "regional": "regional",
    "nome_criador": "nome_criador",
    "nome_responsavel": "nome_responsavel",
    "nome_empresa": "nome_empresa",
    "municipio": "municipio",
    "data_registro": "data_registro",
    "viabilidade": "viabilidade",
    "analise": "analise",
    "pedido": "pedido",
    "data_abertura_cliente": "data_abertura_cliente",
    "data_desejada_cliente": "data_desejada_cliente",
    "data_vencimento_cliente": "data_vencimento_cliente",
    "data_prevista_conexao": "data_prevista_conexao",
    "data_vencimento_ddpe": "data_vencimento_ddpe",
    "dem_carga_atual_fp": "dem_carga_atual_fp",
    "dem_carga_atual_p": "dem_carga_atual_p",
    "dem_carga_solicit_fp": "dem_carga_solicit_fp",
    "dem_carga_solicit_p": "dem_carga_solicit_p",
    "dem_ger_atual_fp": "dem_ger_atual_fp",
    "dem_ger_atual_p": "dem_ger_atual_p",
    "dem_ger_solicit_fp": "dem_ger_solicit_fp",
    "dem_ger_solicit_p": "dem_ger_solicit_p",
    "tensao": "tensao",
    "data_alteracao": "data_alteracao",
    "qtd_anexos": "qtd_anexos",
    "ultimo_status": "ultimo_status",
    "id_alternativa": "id_alternativa",
    "alternativa_descricao": "alternativa_descricao",
    "alternativa_dem_fp_ant": "alternativa_dem_fp_ant",
    "alternativa_dem_p_ant": "alternativa_dem_p_ant",
    "alternativa_dem_fp_dep": "alternativa_dem_fp_dep",
    "alternativa_dem_p_dep": "alternativa_dem_p_dep",
    "alternativa_circuito": "alternativa_circuito",
    "subestacao": "subestacao",
    "sigla_subestacao": "sigla_subestacao",
    "fronteira": "fronteira",
    "custo_modular": "custo_modular",
    "subgrupo_tarifario": "subgrupo_tarifario",
    "etapa": "etapa",
    "ERD": "ERD",
    "demanda_disponivel_ponto": "demanda_disponivel_ponto",
    "proporcionalidade": "proporcionalidade",
    "flag_alternativa_escolhida": "flag_alternativa_escolhida",
    "flag_menor_custo_global": "flag_menor_custo_global",
    "flag_carga": "flag_carga",
    "flag_geracao": "flag_geracao",
    "alternativa_observacao": "alternativa_observacao",

    # ações não tem coluna física, mas precisa existir no map
    "acoes": "id_estudo"
}

@listar_bp.get("/listar/api/estudos")
def api_estudos():

    # parâmetros recebidos via JS
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=25, type=int)
    search = request.args.get("search", default="", type=str)
    sort_column = request.args.get("sort", default="id_estudo", type=str)
    sort_dir = request.args.get("direction", default="desc", type=str)
    export_format = request.args.get("export")
    raw_cols = request.args.get("columns")
    columns_requested = []
    if raw_cols:
        columns_requested = [
            c.strip() for c in raw_cols.split(",")
            if c.strip() in COLUMN_MAP
        ]
        columns_requested = [c for c in columns_requested if c != "acoes"]

    filters_json = request.args.get("filters", "{}")
    column_filters = json.loads(filters_json)

    query = db.session.query(ViewEstudos)


    # Busca global
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                ViewEstudos.num_doc.ilike(search_pattern),
                ViewEstudos.nome_projeto.ilike(search_pattern),
                ViewEstudos.empresa.ilike(search_pattern),
                ViewEstudos.municipio.ilike(search_pattern),
                ViewEstudos.nome_responsavel.ilike(search_pattern),
                ViewEstudos.id_estudo.cast(String).ilike(search_pattern)
            )
        )

    # --- FILTRO POR COLUNA ---
    for col, value in column_filters.items():
        if not value:
            continue

        column_name = COLUMN_MAP.get(col)
        if not column_name:
            continue

        column_obj = getattr(ViewEstudos, column_name)

        # para strings, usar ILIKE
        if isinstance(column_obj.type, String):
            query = query.filter(column_obj.ilike(f"%{value}%"))
        else:
            query = query.filter(column_obj == value)


    # Ordenação
    column_name = COLUMN_MAP.get(sort_column, "id_estudo")
    sort_obj = getattr(ViewEstudos, column_name)
    if sort_dir == "desc":
        sort_obj = sort_obj.desc()

    print(sort_obj)
    query = query.order_by(sort_obj)

    print(query)

    # Paginação real
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # SERIALIZAÇÃO DOS CAMPOS
    items = []

    for e in pagination.items:
        record = {}

        for key, column in COLUMN_MAP.items():
            try:
                value = getattr(e, column)
            except AttributeError:
                value = None

            # Formatação de datas
            if hasattr(value, "strftime"):
                value = value.strftime("%d/%m/%Y")

            if isinstance(value, db.Column):
                print(">>> ERRO: Coluna retornou um Column em vez de valor:", key, column)

            record[key] = value

        # Ações vêm separadas
        record["acoes"] = render_template(
            "listar/partials/acoes.html",
            id_estudo=e.id_estudo,
            usuario=g.user
        )

        items.append(record)

    # === EXPORTAÇÃO ===
    if export_format:

        # monta dataframe ou texto
        if export_format == "csv":
            import csv
            from io import StringIO

            output = StringIO()
            writer = csv.writer(output, delimiter=";")

            writer.writerow(columns_requested)
            for e in items:
                writer.writerow([e[col] for col in columns_requested])

            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={
                    "Content-Disposition": "attachment;filename=atlas_export.csv"
                }
            )

        if export_format == "xlsx":

            df = pd.DataFrame(items)[columns_requested]

            output = BytesIO()
            df.to_excel(output, index=False)

            return Response(
                output.getvalue(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": "attachment;filename=atlas_export.xlsx"
                }
            )

        if export_format == "pdf":
            from fpdf import FPDF

            pdf = FPDF()
            pdf.add_page()

            # Fonte Unicode
            pdf.add_font("DejaVu", "", "app/main/static/fonts/NotoSans-Regular.ttf", uni=True)
            pdf.set_font("DejaVu", "", 10)

            # Cabeçalho
            pdf.set_fill_color(230, 230, 230)
            for col in columns_requested:
                pdf.cell(60, 8, col.replace("_", " ").title(), 1, 0, "L", True)
            pdf.ln()

            # Linhas
            for e in items:
                for col in columns_requested:
                    value = str(e.get(col, ""))
                    pdf.cell(60, 8, value[:60], 1)
                pdf.ln()

            pdf_bytes = pdf.output(dest="S").encode("latin-1", "replace")

            return Response(
                pdf_bytes,
                mimetype="application/pdf",
                headers={"Content-Disposition": "attachment; filename=atlas_export.pdf"}
            )

    return jsonify({
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": items
    })

# pasta 'uploads' dentro do projeto


@listar_bp.route("/listar", methods=["GET", "POST"])
@requires_permission('visualizar')
def listar():
    status_tipos = StatusTipo.query.all()

    return render_template("listar/listar.html", usuario=g.user, status_tipos=status_tipos)

@listar_bp.get("/listar/api/status/<int:id_estudo>")
def api_status(id_estudo):

    # Buscar status do estudo
    historico = (
        db.session.query(StatusEstudo)
        .join(StatusTipo, StatusEstudo.id_status_tipo == StatusTipo.id_status_tipo)
        .filter(StatusEstudo.id_estudo == id_estudo)
        .order_by(StatusEstudo.data.desc())
        .all()
    )

    result = []

    for s in historico:
        result.append({
            "id": s.id_status,
            "status": s.status_tipo.status,
            "data": s.data.strftime("%d/%m/%Y %H:%M"),
            "observacao": s.observacao,
            "criado_por": s.criado_por.nome if s.criado_por else "-"
        })

    return jsonify(result)


@listar_bp.post("/listar/api/status/salvar")
def salvar_status():
    data = request.json

    id_estudo = data.get("id_estudo")
    id_status_tipo = data.get("id_status_tipo")
    observacao = data.get("observacao", "").strip()
    #id_status = data.get("id_status")  # usado para edição opcional

    if not id_estudo or not id_status_tipo:
        return jsonify({"error": "Dados incompletos."}), 400

    # if id_status:
    #     # editar um status existente
    #     status = StatusEstudo.query.get(id_status)
    #     if not status:
    #         return jsonify({"error": "Status não encontrado."}), 404

        # status.id_status_tipo = id_status_tipo
        # status.observacao = observacao

    else:

        tz = pytz.timezone("America/Sao_Paulo")
        horario = datetime.now(tz)

        # adicionar novo
        status = StatusEstudo(
            id_estudo=id_estudo,
            id_status_tipo=id_status_tipo,
            observacao=observacao,
            id_criado_por=g.user.id_usuario,  # quem criou
            data=horario
        )
        db.session.add(status)

    db.session.commit()

    return jsonify({"success": True})


@listar_bp.route('/listar/teste/')
def teste():
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(current_app.root_path))).replace('\\', '/')
    print(current_app.root_path)
    print(os.path.dirname(current_app.root_path))
    print(os.path.dirname(os.path.dirname(current_app.root_path)))
    print(os.path.join(os.path.dirname(current_app.root_path)))
    print(UPLOAD_FOLDER)
    return jsonify({
        'teste': 'ok'
    })

@listar_bp.get("/listar/estudos/<int:id_estudo>")
def api_detalhes_estudo(id_estudo):
    e = db.session.query(ViewEstudos).filter_by(id_estudo=id_estudo).first()
    alternativas = Alternativa.query.filter_by(id_estudo=id_estudo).all()
    anexos = Anexo.query.filter_by(id_estudo=id_estudo).all()
    status = StatusEstudo.query.filter_by(id_estudo=id_estudo).all()

    if not e:
        return "<p>Estudo não encontrado.</p>"

    return render_template(
        "listar/partials/detalhes.html",
        e=e,
        alternativas=alternativas,
        anexos=anexos,
        status=status
    )

@listar_bp.route('/listar/download/<path:filename>')
@requires_permission('visualizar')
def download_file(filename):
    try:
        # Garante que o caminho seja seguro e dentro da pasta uploads
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(current_app.root_path))).replace('\\', '/')

        safe_path = safe_join(UPLOAD_FOLDER, filename)
        print(safe_path)
        if not safe_path or not os.path.isfile(safe_path):
            flash("⚠️ Arquivo não encontrado ou removido.", "warning")
            abort(404)

        directory = os.path.dirname(safe_path)
        file = os.path.basename(safe_path)

        return send_from_directory(directory, file, as_attachment=True)
    except Exception as e:
        print(f'Erro em listar/routes: def download_file() - {str(e)} ')
        flash('Não foi possível encontrar o arquivo no servidor.')
        abort(404)


@listar_bp.route('/listar/excluir/<id_estudo>')
@requires_permission('excluir')
def excluir(id_estudo):
    estudo = Estudo.query.get_or_404(id_estudo)

    if estudo.alternativas:
        # bloqueia a exclusão
        return jsonify({'teste': 'não pode excluir'})
    else:
        return jsonify({'teste': 'pode excluir'})
        # permite a exclusão


@listar_bp.route("/listar/imagem/<int:id>")
def visualizar_imagem(id):
    img = Anexo.query.get_or_404(id)

    return send_file(
        img.endereco,
        mimetype=img.tipo_mime,
        as_attachment=False
    )