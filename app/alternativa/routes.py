from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app.models import Alternativa, Estudo, Circuito, db, FatorK
from app.alternativa.forms import AlternativaForm
from app.auth import requires_permission
from sqlalchemy import literal_column, and_

alternativa_bp = Blueprint('alternativa', __name__, template_folder='templates')


@alternativa_bp.app_template_filter('format_date')
def format_date(value, fmt='%d/%m/%Y'):
    if value is None:
        return '—'
    return value.strftime(fmt)


def calc_prop(form):
    dif_dem_fp = (form.dem_fp_dep.data or 0) - (form.dem_fp_ant.data or 0)
    dif_dem_p = (form.dem_p_dep.data or 0) - (form.dem_p_ant.data or 0)
    dif_dem = max(dif_dem_p, dif_dem_fp)
    demanda_disponivel = form.demanda_disponivel_ponto.data or 0

    if demanda_disponivel == 0:
        return 0

    prop = dif_dem / demanda_disponivel
    return prop

def to_float_safe(value):
    if not value:
        return 0.0
    cleaned = str(value).replace('.', '').replace(',', '.').replace('R$', '').replace(' ', '')
    return float(cleaned) if cleaned else 0.0

def get_fator_k(subgrupo, data, edp):

    if not all([subgrupo, data, edp]):
        #print("⚠️ get_fator_k recebeu parâmetro nulo:", subgrupo, data, edp)
        return None

    fator_k = FatorK.query.filter(
        and_(
            FatorK.id_edp == edp,
            FatorK.subgrupo_tarif == subgrupo,
            FatorK.data_ref <= data,
            literal_column("DATEADD(day, 365, data_ref)") >= data,
        )
    ).order_by(FatorK.data_ref.desc()).first()
    if fator_k:
        return fator_k.id_k
    else:
        return None


@alternativa_bp.route('/estudo/<id_estudo>/alternativas/', methods=['POST', 'GET'])
@requires_permission('visualizar')
def listar(id_estudo):
    """Página principal de alternativas com filtros opcionais"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Query base
    query = Alternativa.query

    # Aplicar filtros
    if id_estudo:
        query = query.filter(Alternativa.id_estudo == id_estudo)

    # Paginação e ordenação
    alternativas_pagination = query.order_by(Alternativa.id_alternativa.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Dados para filtros
    estudo = Estudo.get_with_all_relations(id_estudo)

    form = AlternativaForm()

    form.atualizar_circuitos(estudo.id_edp, estudo.tensao.tensao)

    form.id_estudo.data = id_estudo
    form.dem_fp_ant.data = max(estudo.dem_carga_atual_fp, estudo.dem_ger_atual_fp)
    form.dem_p_ant.data = max(estudo.dem_carga_atual_p, estudo.dem_ger_atual_p)
    form.dem_fp_dep.data = max(estudo.dem_carga_solicit_fp, estudo.dem_ger_solicit_fp)
    form.dem_p_dep.data = max(estudo.dem_carga_solicit_p, estudo.dem_ger_solicit_p)

    form.latitude_ponto_conexao.data = estudo.latitude_cliente
    form.longitude_ponto_conexao.data = estudo.longitude_cliente

    if request.method == 'POST':
        if form.validate_on_submit():

            try:
                arquivo = form.imagem_blob.data
                blob = None
                if arquivo:
                    blob = arquivo.read()

                # Criar novo estudo
                nova_alternativa = Alternativa(
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
                    custo_modular=to_float_safe(form.custo_modular.data),
                    id_k=get_fator_k(form.subgrupo_tarif.data, estudo.data_abertura_cliente, estudo.id_edp),
                    id_estudo=id_estudo,
                    observacao=form.observacao.data,
                    ERD=to_float_safe(form.ERD.data),
                    demanda_disponivel_ponto=form.demanda_disponivel_ponto.data,
                    blob_image=blob

                )

                estudo.n_alternativas = estudo.n_alternativas + 1

                db.session.add(nova_alternativa)
                # db.session.flush()  # Para obter o ID do estudo

                db.session.commit()
                flash(f'Alternativa cadastrada com sucesso!', 'success')
                return redirect(url_for('alternativa.listar', id_estudo=id_estudo))

            except Exception as e:
                print(f'erro: {e}')
                db.session.rollback()
                flash(f'Erro ao cadastrar alternativa. Tente novamente.', 'error')
        else:
            flash('Verifique os campos obrigatórios antes de salvar.', 'warning')
            # Indica ao template para reabrir o modal automaticamente
            return render_template(
                'alternativa/alternativa.html',
                estudo=estudo,
                alternativas=alternativas_pagination.items,
                pagination=alternativas_pagination,
                form=form,
                abrir_modal=True
            )

    return render_template(
        'alternativa/alternativa.html',
        alternativas=alternativas_pagination.items,
        pagination=alternativas_pagination,
        estudo=estudo,
        form=form
    )


@alternativa_bp.route('/alternativas/<id_alternativa>', methods=['GET', 'POST'])
@requires_permission('editar')
def editar(id_alternativa):
    """Editar alternativa existente"""
    alternativa_obj = Alternativa.query.get_or_404(id_alternativa)

    if not alternativa_obj:
        return jsonify({'error': 'Alternativa não encontrada'}), 404

    import base64
    imagem_base64 = base64.b64encode(alternativa_obj.blob_image).decode('utf-8') if alternativa_obj.blob_image else None

    if request.method == 'GET':
        letra_alternativa = alternativa_obj.letra_alternativa
        if isinstance(letra_alternativa, (list, tuple)):
            letra_alternativa = letra_alternativa[0] if letra_alternativa else None
        elif isinstance(letra_alternativa, str) and len(letra_alternativa) > 1:
            letra_alternativa = letra_alternativa.strip("() ").replace("'", "").replace(",", "")

        # circuito = alternativa_obj.circuito
        # if isinstance(circuito, (list, tuple)):
        #     circuito = circuito[0] if circuito else None
        # elif isinstance(letra_alternativa, str) and len(letra_alternativa) > 1:
        #     circuito = circuito.strip("() ").replace("'", "").replace(",", "")

        return jsonify({
            'id_circuito': alternativa_obj.id_circuito,
            'id_estudo': alternativa_obj.id_estudo,
            'descricao': alternativa_obj.descricao,
            'dem_fp_ant': float(alternativa_obj.dem_fp_ant) if alternativa_obj.dem_fp_ant else None,
            'dem_p_ant': float(alternativa_obj.dem_p_ant) if alternativa_obj.dem_p_ant else None,
            'dem_fp_dep': float(alternativa_obj.dem_fp_dep) if alternativa_obj.dem_fp_dep else None,
            'dem_p_dep': float(alternativa_obj.dem_p_dep) if alternativa_obj.dem_p_dep else None,
            'latitude_ponto_conexao': float(
                alternativa_obj.latitude_ponto_conexao) if alternativa_obj.latitude_ponto_conexao else None,
            'longitude_ponto_conexao': float(
                alternativa_obj.longitude_ponto_conexao) if alternativa_obj.longitude_ponto_conexao else None,
            'flag_menor_custo_global': alternativa_obj.flag_menor_custo_global,
            'flag_alternativa_escolhida': alternativa_obj.flag_alternativa_escolhida,
            'flag_carga': alternativa_obj.flag_carga,
            'flag_geracao': alternativa_obj.flag_geracao,
            'flag_fluxo_reverso': alternativa_obj.flag_fluxo_reverso,
            'custo_modular': float(alternativa_obj.custo_modular) if alternativa_obj.custo_modular else None,
            'observacao': alternativa_obj.observacao,
            'ERD': float(alternativa_obj.ERD) if alternativa_obj.ERD else None,
            'demanda_disponivel_ponto': float(alternativa_obj.demanda_disponivel_ponto) if alternativa_obj.demanda_disponivel_ponto else None,
            'imagem_base64': imagem_base64,
            'letra_alternativa': letra_alternativa,
            'id_k': alternativa_obj.id_k,
            'proporcionalidade': alternativa_obj.proporcionalidade})

    # POST - Atualizar alternativa
    form = AlternativaForm()
    if form.validate_on_submit():
        try:
            estudo = Estudo.query.get_or_404(form.id_estudo.data)
            alternativa_obj.id_estudo = form.id_estudo.data
            alternativa_obj.id_circuito = form.id_circuito.data
            alternativa_obj.descricao = form.descricao.data
            alternativa_obj.dem_fp_ant = form.dem_fp_ant.data
            alternativa_obj.dem_p_ant = form.dem_p_ant.data
            alternativa_obj.dem_fp_dep = form.dem_fp_dep.data
            alternativa_obj.dem_p_dep = form.dem_p_dep.data
            alternativa_obj.latitude_ponto_conexao = form.latitude_ponto_conexao.data
            alternativa_obj.longitude_ponto_conexao = form.longitude_ponto_conexao.data
            alternativa_obj.flag_menor_custo_global = form.flag_menor_custo_global.data
            alternativa_obj.flag_alternativa_escolhida = form.flag_alternativa_escolhida.data
            alternativa_obj.custo_modular = form.custo_modular.data
            alternativa_obj.observacao = form.observacao.data
            alternativa_obj.ERD = form.ERD.data
            alternativa_obj.demanda_disponivel_ponto = form.demanda_disponivel_ponto.data
            alternativa_obj.letra_alternativa = form.letra_alternativa.data
            alternativa_obj.id_k = get_fator_k(form.subgrupo_tarif.data, estudo.data_abertura_cliente, estudo.id_edp)
            alternativa_obj.proporcionalidade = calc_prop(form)

            db.session.commit()
            flash('Alternativa atualizada com sucesso!', 'success')

        except IntegrityError as e:
            print(e)
            db.session.rollback()
            flash(f'Erro ao atualizar alternativa. Verifique se os dados estão corretos. {str(e)}', 'error')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash(f'Erro inesperado: {str(e)}', 'error')
    else:
        print(form.errors.items())
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'error')

    return redirect(url_for('alternativa.listar', id_estudo=alternativa_obj.id_estudo))


@alternativa_bp.route('/alternativas/excluir/<int:id>', methods=['DELETE'])
@requires_permission('deletar')
def excluir_alternativa(id):
    try:
        alt = Alternativa.query.get_or_404(id)
        estudo = Estudo.query.get_or_404(alt.id_circuito)
        if not alt:
            return jsonify({'error': 'Alternativa não encontrada'}), 404

        # Verificar se há obras relacionadas
        if alt.obras:
            return jsonify({
                'success': False,
                'message': f'Não é possível excluir esta alternativa pois ela possui {len(alt.obras)} obra(s) relacionada(s).'
            }), 400

        if estudo.n_alternativas > 0:
            estudo.n_alternativas = estudo.n_alternativas - 1

        db.session.delete(alt)
        db.session.commit()
        return jsonify({'status': 'ok'})
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir alternativa: {str(e)}'
        }), 500
