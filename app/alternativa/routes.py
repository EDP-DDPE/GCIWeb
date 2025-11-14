import base64
import os

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from app.models import Alternativa, Estudo, Circuito, db, FatorK, Anexo
from app.alternativa.forms import AlternativaForm
from app.auth import requires_permission
from sqlalchemy import literal_column, and_


alternativa_bp = Blueprint(
    'alternativa',
    __name__,
    template_folder='templates',
    static_folder="static",
    static_url_path='/alternativa/static'
)


# ===========================================
#  Helpers
# ===========================================
@alternativa_bp.app_template_filter('format_date')
def format_date(value, fmt='%d/%m/%Y'):
    if value is None:
        return '—'
    return value.strftime(fmt)


def to_float_safe(value):
    if not value:
        return 0.0
    cleaned = str(value).replace('.', '').replace(',', '.').replace('R$', '').strip()
    return float(cleaned) if cleaned else 0.0


def calc_prop(form):
    dif_dem_fp = (form.dem_fp_dep.data or 0) - (form.dem_fp_ant.data or 0)
    dif_dem_p = (form.dem_p_dep.data or 0) - (form.dem_p_ant.data or 0)
    dif_dem = max(dif_dem_p, dif_dem_fp)
    disp = form.demanda_disponivel_ponto.data or 0
    return dif_dem / disp if disp > 0 else 0


def get_fator_k(subgrupo, data, edp):
    if not all([subgrupo, data, edp]):
        return None

    fator = FatorK.query.filter(
        and_(
            FatorK.id_edp == edp,
            FatorK.subgrupo_tarif == subgrupo,
            FatorK.data_ref <= data,
            literal_column("DATEADD(day, 365, data_ref)") >= data
        )
    ).order_by(FatorK.data_ref.desc()).first()

    return fator.id_k if fator else None


def save_image(file, estudo):
    """
    Salva imagem e retorna: (id_anexo, caminho)
    """
    if not file:
        return None, None

    prefix = f"DDPE_{str(estudo.num_doc).replace('/', '_')}"
    filename = secure_filename(f"{prefix}_{file.filename}")

    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], prefix)
    os.makedirs(upload_dir, exist_ok=True)

    path = os.path.join(upload_dir, filename)
    file.save(path)

    anexo = Anexo(
        nome_arquivo=filename,
        endereco=path,
        tamanho_arquivo=os.path.getsize(path),
        tipo_mime=file.content_type,
        id_estudo=estudo.id_estudo
    )
    db.session.add(anexo)
    db.session.flush()

    return anexo.id_anexo, path


# ===========================================
#  LISTAGEM E NOVA ALTERNATIVA
# ===========================================

@alternativa_bp.route('/estudo/<int:id_estudo>/alternativas/', methods=['GET', 'POST'])
@requires_permission('visualizar')
def listar(id_estudo):
    estudo = Estudo.get_with_all_relations(id_estudo)

    form = AlternativaForm()
    form.id_estudo.data = id_estudo
    form.atualizar_circuitos(estudo.id_edp, 'A2' if estudo.tensao.tensao == 'AT' else 'A4')
    alternativas = Alternativa.query.filter_by(id_estudo=id_estudo).all()

    # ========= CRIAÇÃO =========
    if request.method == 'POST':
        form.atualizar_circuitos(estudo.id_edp, form.subgrupo_tarif.data)
        if form.validate_on_submit():
            try:
                arquivo = form.imagem_blob.data
                id_anexo, path = save_image(arquivo, estudo)

                nova = Alternativa(
                    id_estudo=id_estudo,
                    id_circuito=form.id_circuito.data,
                    descricao=form.descricao.data,
                    dem_fp_ant=form.dem_fp_ant.data,
                    dem_p_ant=form.dem_p_ant.data,
                    dem_fp_dep=form.dem_fp_dep.data,
                    dem_p_dep=form.dem_p_dep.data,
                    latitude_ponto_conexao=form.latitude_ponto_conexao.data,
                    longitude_ponto_conexao=form.longitude_ponto_conexao.data,
                    flag_menor_custo_global=form.flag_menor_custo_global.data,
                    flag_alternativa_escolhida=form.flag_alternativa_escolhida.data,
                    flag_carga=form.flag_carga.data,
                    flag_geracao=form.flag_geracao.data,
                    flag_fluxo_reverso=form.flag_fluxo_reverso.data,
                    proporcionalidade=calc_prop(form),
                    letra_alternativa=form.letra_alternativa.data,
                    custo_modular=form.custo_modular.data,
                    id_k=get_fator_k(form.subgrupo_tarif.data, estudo.data_abertura_cliente, estudo.id_edp),
                    observacao=form.observacao.data,
                    ERD=form.ERD.data,
                    demanda_disponivel_ponto=form.demanda_disponivel_ponto.data,
                    subgrupo_tarifario=form.subgrupo_tarif.data,
                    etapa=form.etapa.data,
                    id_img_anexo=id_anexo
                )

                estudo.n_alternativas += 1

                db.session.add(nova)
                db.session.commit()

                flash("Alternativa cadastrada com sucesso!", "success")
                return redirect(url_for('alternativa.listar', id_estudo=id_estudo))

            except Exception as e:
                db.session.rollback()
                flash("Erro ao cadastrar alternativa.", "danger")

        else:
            flash("Verifique os campos obrigatórios.", "warning")

    return render_template(
        "alternativa/alternativa.html",
        estudo=estudo,
        alternativas=alternativas,
        form=form
    )


# ===========================================
#  GET JSON PARA EDITAR / VISUALIZAR
# ===========================================

@alternativa_bp.route('/alternativas/<int:id_alternativa>', methods=['GET'])
@requires_permission('visualizar')
def carregar_alternativa(id_alternativa):
    alt = Alternativa.query.get_or_404(id_alternativa)
    id_edp = Estudo.query.get_or_404(alt.id_estudo).id_edp
    img64 = None
    if alt.id_img_anexo:
        anexo = Anexo.query.get(alt.id_img_anexo)
        if anexo and os.path.exists(anexo.endereco):
            with open(anexo.endereco, "rb") as f:
                img64 = base64.b64encode(f.read()).decode('utf-8')

    return jsonify({
        'id_alternativa': alt.id_alternativa,
        'id_edp': id_edp,
        'id_estudo': alt.id_estudo,
        'id_circuito': alt.id_circuito,
        'descricao': alt.descricao,
        'dem_fp_ant': float(alt.dem_fp_ant or 0),
        'dem_p_ant': float(alt.dem_p_ant or 0),
        'dem_fp_dep': float(alt.dem_fp_dep or 0),
        'dem_p_dep': float(alt.dem_p_dep or 0),
        'latitude_ponto_conexao': float(alt.latitude_ponto_conexao or 0),
        'longitude_ponto_conexao': float(alt.longitude_ponto_conexao or 0),
        'flag_menor_custo_global': alt.flag_menor_custo_global,
        'flag_alternativa_escolhida': alt.flag_alternativa_escolhida,
        'flag_carga': alt.flag_carga,
        'flag_geracao': alt.flag_geracao,
        'flag_fluxo_reverso': alt.flag_fluxo_reverso,
        'custo_modular': float(alt.custo_modular or 0),
        'observacao': alt.observacao,
        'ERD': float(alt.ERD or 0),
        'demanda_disponivel_ponto': float(alt.demanda_disponivel_ponto or 0),
        'imagem_base64': img64,
        'letra_alternativa': alt.letra_alternativa,
        'subgrupo_tarifario': alt.subgrupo_tarifario,
        'etapa': alt.etapa
    })


# ===========================================
#  EDIÇÃO POST
# ===========================================

@alternativa_bp.route('/alternativas/<int:id_alternativa>', methods=['POST'])
@requires_permission('editar')
def editar_alternativa(id_alternativa):

    alt = Alternativa.query.get_or_404(id_alternativa)
    estudo = Estudo.query.get_or_404(alt.id_estudo)

    form = AlternativaForm()
    form.atualizar_circuitos(estudo.id_edp, alt.subgrupo_tarifario)
    if form.validate_on_submit():
        try:
            arquivo = form.imagem_blob.data
            novo_id_anexo = alt.id_img_anexo

            # nova imagem
            if arquivo:
                novo_id_anexo, path = save_image(arquivo, estudo)

                # remove imagem antiga
                if alt.id_img_anexo:
                    antigo = Anexo.query.get(alt.id_img_anexo)
                    if antigo and os.path.exists(antigo.endereco):
                        os.remove(antigo.endereco)
                    db.session.delete(antigo)

            # atualizar campos
            alt.id_circuito = form.id_circuito.data
            alt.descricao = form.descricao.data
            alt.dem_fp_ant = form.dem_fp_ant.data
            alt.dem_p_ant = form.dem_p_ant.data
            alt.dem_fp_dep = form.dem_fp_dep.data
            alt.dem_p_dep = form.dem_p_dep.data
            alt.latitude_ponto_conexao = form.latitude_ponto_conexao.data
            alt.longitude_ponto_conexao = form.longitude_ponto_conexao.data
            alt.flag_menor_custo_global = form.flag_menor_custo_global.data
            alt.flag_alternativa_escolhida = form.flag_alternativa_escolhida.data
            alt.flag_carga = form.flag_carga.data
            alt.flag_geracao = form.flag_geracao.data
            alt.flag_fluxo_reverso = form.flag_fluxo_reverso.data
            alt.letra_alternativa = form.letra_alternativa.data
            alt.subgrupo_tarifario = form.subgrupo_tarif.data
            alt.etapa = form.etapa.data
            alt.custo_modular = form.custo_modular.data
            alt.observacao = form.observacao.data
            alt.ERD = form.ERD.data
            alt.demanda_disponivel_ponto = form.demanda_disponivel_ponto.data
            alt.proporcionalidade = calc_prop(form)
            alt.id_img_anexo = novo_id_anexo

            db.session.commit()
            flash("Alternativa atualizada com sucesso!", "success")

        except Exception as e:
            db.session.rollback()
            flash("Erro ao atualizar alternativa.", "danger")

    else:
        flash("Erros no formulário.", "danger")

    return redirect(url_for("alternativa.listar", id_estudo=estudo.id_estudo))


# ===========================================
#  DELETAR (AJAX)
# ===========================================

@alternativa_bp.route('/alternativas/excluir/<int:id>', methods=['DELETE'])
@requires_permission('deletar')
def excluir_alternativa(id):
    alt = Alternativa.query.get_or_404(id)
    estudo = Estudo.query.get_or_404(alt.id_estudo)

    # regras de negócio
    if alt.obras:
        return jsonify({
            "success": False,
            "message": "Não é possível excluir: alternativa possui obras vinculadas."
        }), 400

    # remove imagem
    if alt.id_img_anexo:
        anexo = Anexo.query.get(alt.id_img_anexo)
        if anexo and os.path.exists(anexo.endereco):
            os.remove(anexo.endereco)
        db.session.delete(anexo)

    estudo.n_alternativas -= 1

    db.session.delete(alt)
    db.session.commit()

    return jsonify({"success": True})
