from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from .forms import EstudoForm, AlternativaForm, AnexoForm
from app.models import (db, Estudo, Empresa, Municipio, Regional, TipoSolicitacao, EDP, RespRegiao, Usuario, Circuito,
                        Subestacao, Anexo, Alternativa)
from datetime import datetime
from app.auth import requires_permission, get_usuario_logado
import os

cadastro_bp = Blueprint("cadastro", __name__, template_folder="templates")


def gerar_proximo_documento():
    doc_atual = db.session.query(Estudo.num_doc).order_by(Estudo.id_estudo.desc()).first()

    print(doc_atual[0])
    if doc_atual[0]:
        num, ano = str(doc_atual[0]).split('/')
        ano = int(ano) + 2000
        if ano == datetime.now().year:
            num = int(num) + 1
        else:
            ano = datetime.now().year
            num = 1
        proximo_doc = f"{num:04d}/{str(ano)[-2:]}"
        return proximo_doc


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

        viabilidades = (
            db.session.query(TipoSolicitacao.viabilidade)
            .distinct()
            .order_by(TipoSolicitacao.viabilidade)
            .all()
        )

        # Tipos
        form.tipo_viab.choices = [('', 'Selecione...')] + \
                                 [(v[0], v[0]) for v in viabilidades]

        form.num_doc.data = gerar_proximo_documento()


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
@requires_permission('criar')
def cadastro_estudo():
    """Rota para cadastro de estudos"""
    form = EstudoForm()
    carregar_choices_estudo(form)
    usuario = get_usuario_logado()
    print(f'usuario: {usuario.nome}, id: {usuario.id_usuario}')

    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Criar novo estudo
            novo_estudo = Estudo(
                num_doc=gerar_proximo_documento(),
                protocolo=int(form.protocolo.data) if form.protocolo.data else None,
                nome_projeto=form.nome_projeto.data,
                descricao=form.descricao.data,
                instalacao=int(
                    form.instalacao.data) if form.instalacao.data and form.instalacao.data.isdigit() else None,
                n_alternativas=form.n_alternativas.data or 0,
                dem_carga_atual_fp=form.dem_carga_atual_fp.data or 0,
                dem_carga_atual_p=form.dem_carga_atual_p.data or 0,
                dem_carga_solicit_fp=form.dem_carga_solicit_fp.data or 0,
                dem_carga_solicit_p=form.dem_carga_solicit_p.data or 0,
                dem_ger_atual_fp=form.dem_ger_atual_fp.data or 0,
                dem_ger_atual_p=form.dem_ger_atual_p.data or 0,
                dem_ger_solicit_fp=form.dem_ger_solicit_fp.data or 0,
                dem_ger_solicit_p=form.dem_ger_solicit_p.data or 0,
                latitude_cliente=form.latitude_cliente.data,
                longitude_cliente=form.longitude_cliente.data,
                observacao=form.observacao.data,
                id_edp=form.edp.data,
                id_regional=form.regional.data,
                id_criado_por=usuario.id_usuario,  # Assumindo que o ID do usuário está na sessão
                id_resp_regiao=form.resp_regiao.data,
                id_empresa=form.empresa.data if form.empresa.data else None,
                id_municipio=form.municipio.data,
                id_tipo_solicitacao=form.tipo_pedido.data,
                data_registro=datetime.today(),
                data_abertura_cliente=form.data_abertura_cliente.data,
                data_desejada_cliente=form.data_desejada_cliente.data,
                data_vencimento_cliente=form.data_vencimento_cliente.data,
                data_prevista_conexao=form.data_prevista_conexao.data,
                data_vencimento_ddpe=form.data_vencimento_ddpe.data,
            )

            db.session.add(novo_estudo)
            db.session.flush()  # Para obter o ID do estudo

            # Processar arquivo se foi enviado
            for file in form.arquivos.data:
                if file:
                    prefix = f"DDPE_{str(novo_estudo.num_doc).replace('/', '_')}"
                    if not prefix in file.filename:
                        new_name = f"{prefix}_{file.filename}"
                    else:
                        new_name = file.filename
                    nome_arquivo = secure_filename(new_name)

                    # Criar diretório se não existir
                    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], prefix)
                    os.makedirs(upload_folder, exist_ok=True)

                    # Salvar arquivo
                    caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
                    file.save(caminho_arquivo)

                    # Criar registro do anexo
                    novo_anexo = Anexo(
                        nome_arquivo=nome_arquivo,
                        endereco=caminho_arquivo,
                        tamanho_arquivo=os.path.getsize(caminho_arquivo),
                        tipo_mime=file.content_type,
                        id_estudo=novo_estudo.id_estudo
                    )
                    db.session.add(novo_anexo)
                    db.session.flush()

            db.session.commit()
            flash(f'Estudo {novo_estudo.num_doc} cadastrado com sucesso!', 'success')
            return redirect(url_for('listar.listar'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao cadastrar estudo: {str(e)}")
            flash(f'Erro ao cadastrar estudo. Tente novamente.', 'error')

    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'error')

    return render_template('cadastro/cadastrar_estudo.html', form=form)


@cadastro_bp.route("/estudos/editar/<int:id_estudo>", methods=['GET', 'POST'])
@requires_permission('editar')
def editar_estudo(id_estudo):
    estudo = Estudo.query.get_or_404(id_estudo)
    form = EstudoForm()

    form.num_doc.data = estudo.num_doc
    form.protocolo.data = estudo.protocolo
    form.nome_projeto.data = estudo.nome_projeto
    form.descricao.data = estudo.descricao
    form.instalacao.data = estudo.instalacao
    form.n_alternativas.data = estudo.n_alternativas
    form.dem_carga_atual_fp.data = estudo.dem_carga_atual_fp
    form.dem_carga_atual_p.data = estudo.dem_carga_atual_p
    form.dem_carga_solicit_fp.data = estudo.dem_carga_solicit_fp
    form.dem_carga_solicit_p.data = estudo.dem_carga_solicit_p
    form.dem_ger_atual_fp.data = estudo.dem_ger_atual_fp
    form.dem_ger_atual_p.data = estudo.dem_ger_atual_p
    form.dem_ger_solicit_fp.data = estudo.dem_ger_solicit_fp
    form.dem_ger_solicit_p.data = estudo.dem_ger_solicit_p
    form.latitude_cliente.data = estudo.latitude_cliente
    form.longitude_cliente.data = estudo.longitude_cliente
    form.observacao.data = estudo.observacao
    form.edp.data = estudo.id_edp
    form.regional.data = estudo.id_regional
    form.resp_regiao.data = estudo.id_resp_regiao
    form.empresa.data = estudo.id_empresa
    form.municipio.data = estudo.id_municipio
    form.tipo_pedido.data = estudo.id_tipo_solicitacao
    form.data_registro.data = estudo.data_registro
    form.data_abertura_cliente.data = estudo.data_abertura_cliente
    form.data_desejada_cliente.data = estudo.data_desejada_cliente
    form.data_vencimento_cliente.data = estudo.data_vencimento_cliente
    form.data_prevista_conexao.data = estudo.data_prevista_conexao
    form.data_vencimento_ddpe.data = estudo.data_vencimento_ddpe
    return render_template('cadastro/editar_estudo.html', form=form)


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

    estudos = Estudo.query.order_by(Estudo.data_registro.desc()).paginate(
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
