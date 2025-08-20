from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from .forms import EstudoForm, AlternativaForm, AnexoForm
from app.models import (db, Estudo, Empresa, Municipio, Regional, TipoViabilidade,
                       TipoAnalise, TipoPedido, EDP, RespRegiao, Usuario, Circuito,
                       Subestacao, Anexo, Alternativa)
from datetime import datetime
import os


cadastro_bp = Blueprint("cadastro", __name__, template_folder="templates")


def carregar_choices_estudo(form):
    """Carrega as opções dos SelectFields do formulário de estudos"""
    try:
        # EDP
        form.edp.choices = [(0, 'Selecione uma EDP...')] + \
                           [(e.id_edp, e.empresa) for e in EDP.query.all()]

        # Empresas
        form.empresa.choices = [(0, 'Selecione uma empresa...')] + \
                               [(e.id_empresa, e.nome_empresa) for e in Empresa.query.all()]

        # Municípios (filtrar por EDP se necessário)
        form.municipio.choices = [(0, 'Selecione um município...')] + \
                                 [(m.id_municipio, m.municipio) for m in Municipio.query.all()]

        # Regionais (filtrar por EDP se necessário)
        form.regional.choices = [(0, 'Selecione uma regional...')] + \
                                [(r.id_regional, r.regional) for r in Regional.query.all()]

        # Responsáveis por região
        form.resp_regiao.choices = [(0, 'Selecione um responsável...')] + \
                                   [(rr.id_resp_regiao, f"{rr.usuario.nome} - {rr.regional.regional}")
                                    for rr in RespRegiao.query.join(Usuario).join(Regional).all()]

        # Tipos
        form.tipo_viab.choices = [(0, 'Selecione...')] + \
                                 [(tv.id_tipo_viab, tv.descricao) for tv in TipoViabilidade.query.all()]

        form.tipo_analise.choices = [(0, 'Selecione...')] + \
                                    [(ta.id_tipo_analise, ta.analise) for ta in TipoAnalise.query.all()]

        form.tipo_pedido.choices = [(0, 'Selecione...')] + \
                                   [(tp.id_tipo_pedido, tp.descricao) for tp in TipoPedido.query.all()]

    except Exception as e:
        current_app.logger.error(f"Erro ao carregar choices: {str(e)}")
        flash('Erro ao carregar opções do formulário', 'error')


def carregar_choices_alternativa(form, id_edp=None):
    """Carrega as opções dos SelectFields do formulário de alternativas"""
    try:
        if id_edp:
            # Filtrar circuitos por EDP
            circuitos = Circuito.query.filter_by(id_edp=id_edp).join(Subestacao).all()
            form.circuito.choices = [(0, 'Selecione um circuito...')] + \
                                    [(c.id_circuito, f"{c.circuito} - {c.subestacao.nome}")
                                     for c in circuitos]
        else:
            form.circuito.choices = [(0, 'Selecione um circuito...')] + \
                                    [(c.id_circuito, f"{c.circuito} - {c.subestacao.nome}")
                                     for c in Circuito.query.join(Subestacao).all()]
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar circuitos: {str(e)}")
        form.circuito.choices = [(0, 'Erro ao carregar circuitos')]


@cadastro_bp.route("/estudos/cadastro", methods=["GET", "POST"])
def cadastro_estudo():
    """Rota para cadastro de estudos"""
    form = EstudoForm()
    carregar_choices_estudo(form)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Criar novo estudo
            novo_estudo = Estudo(
                num_doc=form.num_doc.data,
                protocolo=int(form.protocolo.data) if form.protocolo.data else None,
                nome_projeto=form.nome_projeto.data,
                descricao=form.descricao.data,
                instalacao=int(
                    form.instalacao.data) if form.instalacao.data and form.instalacao.data.isdigit() else None,
                n_alternativas=form.n_alternativas.data or 0,
                dem_solicit_fp=form.dem_solicit_fp.data,
                dem_solicit_p=form.dem_solicit_p.data,
                latitude_cliente=form.latitude_cliente.data,
                longitude_cliente=form.longitude_cliente.data,
                observacao=form.observacao.data,
                id_edp=form.edp.data,
                id_regional=form.regional.data,
                id_criado_por=session.get('user_id'),  # Assumindo que o ID do usuário está na sessão
                id_resp_regiao=form.resp_regiao.data,
                id_empresa=form.empresa.data if form.empresa.data else None,
                id_municipio=form.municipio.data,
                id_tipo_viab=form.tipo_viab.data,
                id_tipo_analise=form.tipo_analise.data,
                id_tipo_pedido=form.tipo_pedido.data,
                data_registro=form.data_registro.data,
                data_transgressao=form.data_transgressao.data,
                data_vencimento=form.data_vencimento.data,
                data_criacao=datetime.now()
            )

            db.session.add(novo_estudo)
            db.session.flush()  # Para obter o ID do estudo

            # Processar arquivo se foi enviado
            if form.arquivo.data:
                arquivo = form.arquivo.data
                nome_arquivo = secure_filename(arquivo.filename)

                # Criar diretório se não existir
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'estudos', str(novo_estudo.id_estudo))
                os.makedirs(upload_folder, exist_ok=True)

                # Salvar arquivo
                caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
                arquivo.save(caminho_arquivo)

                # Criar registro do anexo
                novo_anexo = Anexo(
                    nome_arquivo=nome_arquivo,
                    endereco=caminho_arquivo,
                    tamanho_arquivo=os.path.getsize(caminho_arquivo),
                    tipo_mime=arquivo.content_type,
                    id_estudo=novo_estudo.id_estudo
                )
                db.session.add(novo_anexo)

            db.session.commit()
            flash(f'Estudo {novo_estudo.num_doc} cadastrado com sucesso!', 'success')
            return redirect(url_for('cadastro.listar_estudos'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao cadastrar estudo: {str(e)}")
            flash('Erro ao cadastrar estudo. Tente novamente.', 'error')

    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'error')

    return render_template('cadastro/cadastrar_estudo.html', form=form)


@cadastro_bp.route("/estudos/<int:id_estudo>/alternativas/cadastro", methods=["GET", "POST"])
def cadastro_alternativa(id_estudo):
    """Rota para cadastro de alternativas de um estudo"""
    estudo = Estudo.query.get_or_404(id_estudo)
    form = AlternativaForm()
    carregar_choices_alternativa(form, estudo.id_edp)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            nova_alternativa = Alternativa(
                id_circuito=form.circuito.data,
                descricao=form.descricao.data,
                dem_fp_ant=form.dem_fp_ant.data,
                dem_p_ant=form.dem_p_ant.data,
                dem_fp_dep=form.dem_fp_dep.data,
                dem_p_dep=form.dem_p_dep.data,
                latitude_ponto_conexao=form.latitude_ponto_conexao.data,
                longitude_ponto_conexao=form.longitude_ponto_conexao.data,
                custo_modular=form.custo_modular.data,
                id_estudo=id_estudo,
                observacao=form.observacao.data,
                ERD=form.ERD.data,
                demanda_disponivel_ponto=form.demanda_disponivel_ponto.data
            )

            db.session.add(nova_alternativa)

            # Atualizar número de alternativas no estudo
            estudo.n_alternativas = Alternativa.query.filter_by(id_estudo=id_estudo).count() + 1

            db.session.commit()
            flash('Alternativa cadastrada com sucesso!', 'success')
            return redirect(url_for('cadastro.detalhar_estudo', id_estudo=id_estudo))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao cadastrar alternativa: {str(e)}")
            flash('Erro ao cadastrar alternativa. Tente novamente.', 'error')

    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'error')

    return render_template('cadastro/cadastrar_alternativa.html', form=form, estudo=estudo)


@cadastro_bp.route("/estudos/<int:id_estudo>/anexos/upload", methods=["GET", "POST"])
def upload_anexo(id_estudo):
    """Rota para upload de anexos de um estudo"""
    estudo = Estudo.query.get_or_404(id_estudo)
    form = AnexoForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            arquivo = form.arquivo.data
            nome_arquivo = secure_filename(arquivo.filename)

            # Criar diretório se não existir
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'estudos', str(id_estudo))
            os.makedirs(upload_folder, exist_ok=True)

            # Gerar nome único se arquivo já existir
            base_name, ext = os.path.splitext(nome_arquivo)
            counter = 1
            while os.path.exists(os.path.join(upload_folder, nome_arquivo)):
                nome_arquivo = f"{base_name}_{counter}{ext}"
                counter += 1

            # Salvar arquivo
            caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
            arquivo.save(caminho_arquivo)

            # Criar registro do anexo
            novo_anexo = Anexo(
                nome_arquivo=form.descricao.data or nome_arquivo,
                endereco=caminho_arquivo,
                tamanho_arquivo=os.path.getsize(caminho_arquivo),
                tipo_mime=arquivo.content_type,
                id_estudo=id_estudo
            )

            db.session.add(novo_anexo)
            db.session.commit()

            flash('Arquivo enviado com sucesso!', 'success')
            return redirect(url_for('cadastro.detalhar_estudo', id_estudo=id_estudo))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao fazer upload do anexo: {str(e)}")
            flash('Erro ao enviar arquivo. Tente novamente.', 'error')

    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'error')

    return render_template('cadastro/upload_anexo.html', form=form, estudo=estudo)


@cadastro_bp.route("/estudos")
def listar_estudos():
    """Rota para listar estudos"""
    page = request.args.get('page', 1, type=int)
    per_page = 10

    estudos = Estudo.query.order_by(Estudo.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('cadastro/listar_estudos.html', estudos=estudos)


@cadastro_bp.route("/estudos/<int:id_estudo>")
def detalhar_estudo(id_estudo):
    """Rota para detalhar um estudo específico"""
    estudo = Estudo.query.get_or_404(id_estudo)
    alternativas = Alternativa.query.filter_by(id_estudo=id_estudo).all()
    anexos = Anexo.query.filter_by(id_estudo=id_estudo).all()

    return render_template('cadastro/detalhar_estudo.html',
                           estudo=estudo,
                           alternativas=alternativas,
                           anexos=anexos)


# Rotas AJAX para filtros dinâmicos
@cadastro_bp.route("/api/municipios/<int:id_edp>")
def get_municipios_by_edp(id_edp):
    """API para buscar municípios por EDP"""
    municipios = Municipio.query.filter_by(id_edp=id_edp).all()
    return {'municipios': [{'id': m.id_municipio, 'nome': m.municipio} for m in municipios]}


@cadastro_bp.route("/api/regionais/<int:id_edp>")
def get_regionais_by_edp(id_edp):
    """API para buscar regionais por EDP"""
    regionais = Regional.query.filter_by(id_edp=id_edp).all()
    return {'regionais': [{'id': r.id_regional, 'nome': r.regional} for r in regionais]}


@cadastro_bp.route("/api/circuitos/<int:id_edp>")
def get_circuitos_by_edp(id_edp):
    """API para buscar circuitos por EDP"""
    circuitos = Circuito.query.filter_by(id_edp=id_edp).join(Subestacao).all()
    return {'circuitos': [{'id': c.id_circuito, 'nome': f"{c.circuito} - {c.subestacao.nome}"}
                          for c in circuitos]}


@cadastro_bp.route("/api/resp_regioes/<int:id_regional>")
def get_resp_by_regional(id_regional):
    """API para buscar responsáveis por regional"""
    responsaveis = RespRegiao.query.filter_by(id_regional=id_regional).join(Usuario).all()
    return {'responsaveis': [{'id': r.id_resp_regiao, 'nome': r.usuario.nome}
                             for r in responsaveis]}