from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from .forms import EstudoForm, AlternativaForm, AnexoForm
from app.models import (db, Estudo, Empresa, Municipio, Regional, TipoSolicitacao, EDP, RespRegiao, Usuario, Circuito,
                        Subestacao, Anexo, Alternativa, Tensao, Instalacao)

from datetime import datetime, timedelta
from app.auth import requires_permission, get_usuario_logado
import os

cadastro_bp = Blueprint("cadastro", __name__, template_folder="templates", static_folder="static", static_url_path='/cadastro/static')


def gerar_proximo_documento():
    doc_atual = db.session.query(Estudo.num_doc).order_by(Estudo.num_doc.desc()).first()

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

        # Classe de Tensão
        form.tensao.choices = [(0, 'Selecione uma classe de tensão...')] + \
                              [(t.id_tensao, t.tensao) for t in Tensao.query.all()]

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
                                   [(rr.id_resp_regiao, f"{rr.usuario.nome} - {rr.regional.regional} ({rr.ano_ref})")
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
    form.num_doc.data = gerar_proximo_documento()

    carregar_choices_estudo(form)
    usuario = get_usuario_logado()
    # print(f'usuario: {usuario.nome}, id: {usuario.id_usuario}')

    if request.method == 'POST' and form.validate_on_submit():

        if not form.tipo_pedido.data or form.tipo_pedido.data == '0':
            flash('Selecione um tipo de pedido válido.', 'warning')
            return redirect(request.url)
        
        try:
            # Criar novo estudo
            novo_estudo = Estudo(
                num_doc=gerar_proximo_documento(),
                protocolo=int(form.protocolo.data) if form.protocolo.data else None,
                nome_projeto=form.nome_projeto.data,
                descricao=form.descricao.data,

                id_tensao=form.tensao.data,
                instalacao=int(form.instalacao.data) if form.instalacao.data else 0,
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
                id_empresa=form.id_empresa.data,
                id_municipio=form.municipio.data,
                id_tipo_solicitacao=form.tipo_pedido.data,
                data_registro=datetime.today(),
                data_abertura_cliente=form.data_abertura_cliente.data,
                data_desejada_cliente=form.data_desejada_cliente.data,
                data_vencimento_cliente=form.data_vencimento_cliente.data,
                data_prevista_conexao=form.data_prevista_conexao.data,
                data_vencimento_ddpe=form.data_vencimento_ddpe.data,
                tipo_geracao=form.tipo_geracao.data
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
            return redirect(url_for('alternativa.listar', id_estudo=novo_estudo.id_estudo))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao cadastrar estudo: {str(e)}")
            flash(f'Erro ao cadastrar estudo. Tente novamente.', 'error')

    elif request.method == 'POST':
        flash('Por favor, corrija os erros no formulário.', 'error')

    return render_template('cadastro/cadastrar_estudo.html', form=form, datetime=datetime, timedelta=timedelta)


def carregar_classificacao(form, id):
    classificacao = TipoSolicitacao.query.get_or_404(id)

    analises = (
        db.session.query(TipoSolicitacao.analise)
        .filter(TipoSolicitacao.viabilidade == classificacao.viabilidade)
        .distinct()
        .order_by(TipoSolicitacao.analise)
        .all()
    )

    pedidos = (
        db.session.query(TipoSolicitacao).filter(
            (TipoSolicitacao.viabilidade == classificacao.viabilidade) &
            (TipoSolicitacao.analise == classificacao.analise)
        )
        .distinct()
        .order_by(TipoSolicitacao.pedido)
        .all()
    )

    form.tipo_analise.choices = [(a[0], a[0]) for a in analises if a[0]]
    form.tipo_pedido.choices = [(p.id_tipo_solicitacao, p.pedido) for p in pedidos]


@cadastro_bp.route("/estudos/editar/<int:id_estudo>", methods=['GET', 'POST'])
@requires_permission('editar')
def editar_estudo(id_estudo):
    estudo = Estudo.query.get_or_404(id_estudo)
    form = EstudoForm()
    carregar_choices_estudo(form)
    carregar_classificacao(form, estudo.id_tipo_solicitacao)
    anexos = Anexo.query.filter_by(id_estudo=estudo.id_estudo).all()
    usuario = get_usuario_logado()

    #print(request.method)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            estudo.protocolo = int(form.protocolo.data) if form.protocolo.data else None
            estudo.nome_projeto = form.nome_projeto.data
            estudo.descricao = form.descricao.data
            estudo.id_tensao = form.tensao.data
            estudo.instalacao = int(form.instalacao.data)
            estudo.n_alternativas = form.n_alternativas.data or 0
            estudo.dem_carga_atual_fp = form.dem_carga_atual_fp.data or 0
            estudo.dem_carga_atual_p = form.dem_carga_atual_p.data or 0
            estudo.dem_carga_solicit_fp = form.dem_carga_solicit_fp.data or 0
            estudo.dem_carga_solicit_p = form.dem_carga_solicit_p.data or 0
            estudo.dem_ger_atual_fp = form.dem_ger_atual_fp.data or 0
            estudo.dem_ger_atual_p = form.dem_ger_atual_p.data or 0
            estudo.dem_ger_solicit_fp = form.dem_ger_solicit_fp.data or 0
            estudo.dem_ger_solicit_p = form.dem_ger_solicit_p.data or 0
            estudo.latitude_cliente = form.latitude_cliente.data
            estudo.longitude_cliente = form.longitude_cliente.data
            estudo.observacao = form.observacao.data
            estudo.id_edp = form.edp.data
            estudo.id_regional = form.regional.data
            estudo.id_resp_regiao = form.resp_regiao.data
            estudo.id_empresa = form.id_empresa.data
            estudo.id_municipio = form.municipio.data
            estudo.id_tipo_solicitacao = form.tipo_pedido.data
            estudo.data_abertura_cliente = form.data_abertura_cliente.data
            estudo.data_desejada_cliente = form.data_desejada_cliente.data
            estudo.data_vencimento_cliente = form.data_vencimento_cliente.data
            estudo.data_prevista_conexao = form.data_prevista_conexao.data
            estudo.data_vencimento_ddpe = form.data_vencimento_ddpe.data
            estudo.id_resp_alteracao = usuario.id_usuario
            estudo.data_alteracao = datetime.today()
            estudo.tipo_geracao = form.tipo_geracao.data

            anexos_excluir = request.form.getlist('excluir_anexo')


            # Upload de novos arquivos (opcional)
            for file in form.arquivos.data:
                if file:
                    prefix = f"DDPE_{str(estudo.num_doc).replace('/', '_')}"
                    if not prefix in file.filename:
                        new_name = f"{prefix}_{file.filename}"
                    else:
                        new_name = file.filename
                    nome_arquivo = secure_filename(new_name)



                    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], prefix)
                    os.makedirs(upload_folder, exist_ok=True)
                    caminho_arquivo = os.path.join(upload_folder, nome_arquivo)

                    overwrite_file = Anexo.query.filter_by(endereco=caminho_arquivo).first()
                    if overwrite_file:
                        if os.path.exists(overwrite_file.endereco):
                            os.remove(overwrite_file.endereco)
                        db.session.delete(overwrite_file)

                    file.save(caminho_arquivo)

                    novo_anexo = Anexo(
                        nome_arquivo=nome_arquivo,
                        endereco=caminho_arquivo,
                        tamanho_arquivo=os.path.getsize(caminho_arquivo),
                        tipo_mime=file.content_type,
                        id_estudo=estudo.id_estudo
                    )
                    db.session.add(novo_anexo)

            for id_anexo in anexos_excluir:
                anexo = Anexo.query.get_or_404(id_anexo)
                if anexo:
                    if os.path.exists(anexo.endereco):
                        os.remove(anexo.endereco)
                    db.session.delete(anexo)

            db.session.commit()
            flash(f'Estudo {estudo.num_doc} atualizado com sucesso!', 'success')
            return redirect(url_for('alternativa.listar', id_estudo=estudo.id_estudo))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao editar estudo: {str(e)}")
            flash('Erro ao salvar alterações. Tente novamente.', 'error')



    # Preenche os dados no formulário (GET)
    # Aba Básicas
    form.num_doc.data = estudo.num_doc
    form.protocolo.data = estudo.protocolo
    form.nome_projeto.data = estudo.nome_projeto
    form.descricao.data = estudo.descricao
    form.instalacao.data = estudo.instalacao
    form.tensao.data = estudo.id_tensao
    form.n_alternativas.data = estudo.n_alternativas
    if estudo.id_empresa:
        form.id_empresa.data = estudo.id_empresa
        form.CNPJ.data = estudo.empresa.cnpj
        form.nome_empresa.data = estudo.empresa.nome_empresa
        try:
            form.demanda.data = Instalacao.query.filter(Instalacao.CNPJ == estudo.empresa.cnpj).first().CARGA
        except AttributeError as e:
            pass

    # Aba Demandas
    form.dem_carga_atual_fp.data = estudo.dem_carga_atual_fp
    form.dem_carga_atual_p.data = estudo.dem_carga_atual_p
    form.dem_carga_solicit_fp.data = estudo.dem_carga_solicit_fp
    form.dem_carga_solicit_p.data = estudo.dem_carga_solicit_p
    form.dem_ger_atual_fp.data = estudo.dem_ger_atual_fp
    form.dem_ger_atual_p.data = estudo.dem_ger_atual_p
    form.dem_ger_solicit_fp.data = estudo.dem_ger_solicit_fp
    form.dem_ger_solicit_p.data = estudo.dem_ger_solicit_p

    # Aba Localização
    form.edp.data = estudo.id_edp
    form.regional.data = estudo.id_regional
    form.municipio.data = estudo.id_municipio
    form.resp_regiao.data = estudo.id_resp_regiao
    form.latitude_cliente.data = estudo.latitude_cliente
    form.longitude_cliente.data = estudo.longitude_cliente

    # Aba Classificação
    form.tipo_viab.data = estudo.tipo_solicitacao.viabilidade
    form.tipo_pedido.data = estudo.tipo_solicitacao.pedido
    form.tipo_analise.data = estudo.tipo_solicitacao.analise
    form.tipo_geracao.data = estudo.tipo_geracao

    # Aba Datas
    form.data_registro.data = estudo.data_registro
    form.data_abertura_cliente.data = estudo.data_abertura_cliente
    form.data_desejada_cliente.data = estudo.data_desejada_cliente
    form.data_vencimento_cliente.data = estudo.data_vencimento_cliente
    form.data_prevista_conexao.data = estudo.data_prevista_conexao
    form.data_vencimento_ddpe.data = estudo.data_vencimento_ddpe

    # Aba Observações

    form.observacao.data = estudo.observacao
    return render_template('cadastro/editar_estudo.html', form=form, estudo=estudo, anexos=anexos, datetime=datetime)


# @cadastro_bp.route("/estudos/<int:id_estudo>/anexos/upload", methods=["GET", "POST"])
# def upload_anexo(id_estudo):
#     """Rota para upload de anexos de um estudo"""
#     estudo = Estudo.query.get_or_404(id_estudo)
#     form = AnexoForm()
#
#     if request.method == 'POST' and form.validate_on_submit():
#         try:
#             arquivo = form.arquivo.data
#             nome_arquivo = secure_filename(arquivo.filename)
#
#             # Criar diretório se não existir
#             upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'estudos', str(id_estudo))
#             os.makedirs(upload_folder, exist_ok=True)
#
#             # Gerar nome único se arquivo já existir
#             base_name, ext = os.path.splitext(nome_arquivo)
#             counter = 1
#             while os.path.exists(os.path.join(upload_folder, nome_arquivo)):
#                 nome_arquivo = f"{base_name}_{counter}{ext}"
#                 counter += 1
#
#             # Salvar arquivo
#             caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
#             arquivo.save(caminho_arquivo)
#
#             # Criar registro do anexo
#             novo_anexo = Anexo(
#                 nome_arquivo=form.descricao.data or nome_arquivo,
#                 endereco=caminho_arquivo,
#                 tamanho_arquivo=os.path.getsize(caminho_arquivo),
#                 tipo_mime=arquivo.content_type,
#                 id_estudo=id_estudo
#             )
#
#             db.session.add(novo_anexo)
#             db.session.commit()
#
#             flash('Arquivo enviado com sucesso!', 'success')
#             return redirect(url_for('cadastro.detalhar_estudo', id_estudo=id_estudo))
#
#         except Exception as e:
#             db.session.rollback()
#             current_app.logger.error(f"Erro ao fazer upload do anexo: {str(e)}")
#             flash('Erro ao enviar arquivo. Tente novamente.', 'error')
#
#     elif request.method == 'POST':
#         flash('Por favor, corrija os erros no formulário.', 'error')
#
#     return render_template('cadastro/upload_anexo.html', form=form, estudo=estudo)


# @cadastro_bp.route("/estudos/<int:id_estudo>")
# def detalhar_estudo(id_estudo):
#     """Rota para detalhar um estudo específico"""
#     estudo = Estudo.query.get_or_404(id_estudo)
#     alternativas = Alternativa.query.filter_by(id_estudo=id_estudo).all()
#     anexos = Anexo.query.filter_by(id_estudo=id_estudo).all()
#
#     return render_template('cadastro/detalhar_estudo.html',
#                            estudo=estudo,
#                            alternativas=alternativas,
#                            anexos=anexos)


@cadastro_bp.route("/estudos/excluir/<int:id_estudo>", methods=['DELETE'])
@requires_permission('deletar')
@requires_permission('deletar')
def excluir_estudo(id_estudo):
    print("entrei no excluir")
    user = get_usuario_logado()
    try:
        estudo = Estudo.query.get_or_404(id_estudo)
        id_resp = RespRegiao.query.get_or_404(estudo.id_resp_regiao).id_usuario

        if user.id_usuario not in [id_resp, estudo.id_criado_por] and not user.admin:
            return jsonify({'success': False, 'message': 'Você não tem permissão para deletar esse estudo. Solicite ao criador do estudo, o resposável da região ou à algum admin.'})

        print(f"{datetime.now()}: Estudo {id_estudo} excluído pelo usuário {user.nome} ")
        db.session.delete(estudo)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Estudo excluído com sucesso!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir estudo: {e}")
        return jsonify({'success': False, 'message': 'Erro ao excluir o estudo.'}), 500

