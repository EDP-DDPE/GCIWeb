from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from app.models import Alternativa, Estudo, Circuito, db
from app.alternativa.forms import AlternativaForm
from app.auth import requires_permission

alternativa_bp = Blueprint('alternativa', __name__, template_folder='templates')


@alternativa_bp.app_template_filter('format_date')
def format_date(value, fmt='%d/%m/%Y'):
    if value is None:
        return '—'
    return value.strftime(fmt)


@alternativa_bp.route('/estudo/<id_estudo>/alternativas/')
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


    #estudo = Estudo.query.filter(Estudo.id_estudo == id_estudo).first()

    form = AlternativaForm()

    form.id_estudo.data = id_estudo

    return render_template(
        'alternativa/alternativa.html',
        alternativas=alternativas_pagination.items,
        pagination=alternativas_pagination,
        estudo=estudo,
        form=form
    )


@alternativa_bp.route('/alternativas/<int:id_estudo>/criar', methods=['POST'])
@requires_permission('criar')
def criar(id_estudo):
    """Criar nova alternativa"""
    form = AlternativaForm()

    if form.validate_on_submit():
        try:
            alternativa_obj = Alternativa(
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
                custo_modular=form.custo_modular.data,
                id_estudo=id_estudo,
                observacao=form.observacao.data,
                ERD=form.ERD.data,
                demanda_disponivel_ponto=form.demanda_disponivel_ponto.data
            )

            db.session.add(alternativa_obj)
            db.session.commit()

            flash('Alternativa criada com sucesso!', 'success')

        except IntegrityError as e:
            db.session.rollback()
            flash('Erro ao criar alternativa. Verifique se os dados estão corretos.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro inesperado: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'error')

    return redirect(url_for('alternativa.listar'))


@alternativa_bp.route('/alternativas/<int:id>/editar', methods=['GET', 'POST'])
@requires_permission('editar')
def editar(id):
    """Editar alternativa existente"""
    alternativa_obj = Alternativa.query.get_or_404(id)

    if request.method == 'GET':
        # Retornar dados da alternativa como JSON para popular o formulário
        return jsonify({
            'id_circuito': alternativa_obj.id_circuito,
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
            'custo_modular': float(alternativa_obj.custo_modular) if alternativa_obj.custo_modular else None,
            'id_estudo': alternativa_obj.id_estudo,
            'observacao': alternativa_obj.observacao,
            'ERD': float(alternativa_obj.ERD) if alternativa_obj.ERD else None,
            'demanda_disponivel_ponto': float(
                alternativa_obj.demanda_disponivel_ponto) if alternativa_obj.demanda_disponivel_ponto else None
        })

    # POST - Atualizar alternativa
    form = AlternativaForm()

    if form.validate_on_submit():
        try:
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
            alternativa_obj.id_estudo = form.id_estudo.data
            alternativa_obj.observacao = form.observacao.data
            alternativa_obj.ERD = form.ERD.data
            alternativa_obj.demanda_disponivel_ponto = form.demanda_disponivel_ponto.data

            db.session.commit()
            flash('Alternativa atualizada com sucesso!', 'success')

        except IntegrityError as e:
            db.session.rollback()
            flash('Erro ao atualizar alternativa. Verifique se os dados estão corretos.', 'error')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro inesperado: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Erro no campo {getattr(form, field).label.text}: {error}', 'error')

    return redirect(url_for('alternativa.listar'))


@alternativa_bp.route('/alternativas/<int:id>/excluir', methods=['DELETE'])
@requires_permission('deletar')
def excluir(id):
    """Excluir alternativa"""
    try:
        alternativa_obj = Alternativa.query.get_or_404(id)

        # Verificar se há obras relacionadas
        if alternativa_obj.obras:
            return jsonify({
                'success': False,
                'message': f'Não é possível excluir esta alternativa pois ela possui {len(alternativa_obj.obras)} obra(s) relacionada(s).'
            }), 400

        db.session.delete(alternativa_obj)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Alternativa excluída com sucesso!'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir alternativa: {str(e)}'
        }), 500


@alternativa_bp.route('/alternativas/<int:id>/')
@requires_permission('visualizar')
def visualizar(id):
    """Visualizar detalhes da alternativa"""
    alternativa_obj = Alternativa.query.get_or_404(id)

    html_content = f"""
    <div class="row">
        <div class="col-md-6">
            <h6 class="text-primary">Informações Básicas</h6>
            <table class="table table-sm">
                <tr><td><strong>ID:</strong></td><td>{alternativa_obj.id_alternativa}</td></tr>
                <tr><td><strong>Descrição:</strong></td><td>{alternativa_obj.descricao or 'N/A'}</td></tr>
                <tr><td><strong>Estudo:</strong></td><td>{alternativa_obj.estudo.nome if alternativa_obj.estudo else 'N/A'}</td></tr>
                <tr><td><strong>Circuito:</strong></td><td>{alternativa_obj.circuito.nome if alternativa_obj.circuito else 'N/A'}</td></tr>
                <tr><td><strong>Custo Modular:</strong></td><td>R$ {"{:,.2f}".format(alternativa_obj.custo_modular) if alternativa_obj.custo_modular else 'N/A'}</td></tr>
            </table>

            <h6 class="text-primary mt-3">Status</h6>
            <table class="table table-sm">
                <tr><td><strong>Menor Custo Global:</strong></td><td>{'Sim' if alternativa_obj.flag_menor_custo_global else 'Não'}</td></tr>
                <tr><td><strong>Alternativa Escolhida:</strong></td><td>{'Sim' if alternativa_obj.flag_alternativa_escolhida else 'Não'}</td></tr>
            </table>
        </div>

        <div class="col-md-6">
            <h6 class="text-primary">Demandas</h6>
            <table class="table table-sm">
                <tr><td><strong>Dem. FP Anterior:</strong></td><td>{alternativa_obj.dem_fp_ant or 'N/A'}</td></tr>
                <tr><td><strong>Dem. P Anterior:</strong></td><td>{alternativa_obj.dem_p_ant or 'N/A'}</td></tr>
                <tr><td><strong>Dem. FP Depois:</strong></td><td>{alternativa_obj.dem_fp_dep or 'N/A'}</td></tr>
                <tr><td><strong>Dem. P Depois:</strong></td><td>{alternativa_obj.dem_p_dep or 'N/A'}</td></tr>
                <tr><td><strong>Dem. Disponível Ponto:</strong></td><td>{alternativa_obj.demanda_disponivel_ponto or 'N/A'}</td></tr>
            </table>

            <h6 class="text-primary mt-3">Localização</h6>
            <table class="table table-sm">
                <tr><td><strong>Latitude:</strong></td><td>{alternativa_obj.latitude_ponto_conexao or 'N/A'}</td></tr>
                <tr><td><strong>Longitude:</strong></td><td>{alternativa_obj.longitude_ponto_conexao or 'N/A'}</td></tr>
            </table>

            <h6 class="text-primary mt-3">Outros</h6>
            <table class="table table-sm">
                <tr><td><strong>ERD:</strong></td><td>{alternativa_obj.ERD or 'N/A'}</td></tr>
            </table>
        </div>
    </div>

    {f'<div class="row mt-3"><div class="col-12"><h6 class="text-primary">Observações</h6><p>{alternativa_obj.observacao}</p></div></div>' if alternativa_obj.observacao else ''}

    <div class="row mt-3">
        <div class="col-12">
            <h6 class="text-primary">Obras Relacionadas</h6>
            {f'<p>Esta alternativa possui {len(alternativa_obj.obras)} obra(s) relacionada(s).</p>' if alternativa_obj.obras else '<p>Nenhuma obra relacionada.</p>'}
        </div>
    </div>
    """

    return html_content


@alternativa_bp.route('/api/circuitos/<int:estudo_id>')
def get_circuitos_por_estudo(estudo_id):
    """API para obter circuitos de um estudo específico"""
    circuitos = Circuito.query.filter_by(id_estudo=estudo_id).order_by(Circuito.nome).all()
    return jsonify([
        {'id': c.id_circuito, 'nome': c.nome}
        for c in circuitos
    ])


@alternativa_bp.route('/alternativas/relatorio')
def relatorio():
    """Relatório de alternativas"""
    # Filtros
    estudo_id = request.args.get('estudo', type=int)
    circuito_id = request.args.get('circuito', type=int)

    # Query base
    query = Alternativa.query

    # Aplicar filtros
    if estudo_id:
        query = query.filter(Alternativa.id_estudo == estudo_id)
    if circuito_id:
        query = query.filter(Alternativa.id_circuito == circuito_id)

    alternativas = query.order_by(Alternativa.custo_modular).all()

    # Estatísticas
    total_alternativas = len(alternativas)
    custo_total = sum(alt.custo_modular for alt in alternativas if alt.custo_modular)
    alternativas_escolhidas = sum(1 for alt in alternativas if alt.flag_alternativa_escolhida)
    menor_custo_global = sum(1 for alt in alternativas if alt.flag_menor_custo_global)

    # Dados para filtros
    estudos = Estudo.query.order_by(Estudo.nome).all()
    circuitos = Circuito.query.order_by(Circuito.nome).all()

    return render_template(
        '/alternativas/relatorio.html',
        alternativas=alternativas,
        estudos=estudos,
        circuitos=circuitos,
        estatisticas={
            'total_alternativas': total_alternativas,
            'custo_total': custo_total,
            'alternativas_escolhidas': alternativas_escolhidas,
            'menor_custo_global': menor_custo_global
        }
    )