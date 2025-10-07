from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func, UniqueConstraint
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime
from flask import jsonify, request
from decimal import Decimal

db = SQLAlchemy()


class EDP(db.Model):
    __tablename__ = 'edp'
    __table_args__ = {'schema': 'gciweb'}

    id_edp = db.Column(db.BigInteger, primary_key=True)
    empresa = db.Column(db.String(2), nullable=False)

    # Relacionamentos com lazy='select' para evitar carregamento desnecessário
    regionais = db.relationship('Regional', back_populates='edp', lazy='select')
    municipios = db.relationship('Municipio', back_populates='edp', lazy='select')
    subestacoes = db.relationship('Subestacao', back_populates='edp', lazy='select')
    circuitos = db.relationship('Circuito', back_populates='edp', lazy='select')
    estudos = db.relationship('Estudo', back_populates='edp', lazy='select')


class Instalacao(db.Model):
    __tablename__ = 'INSTALACOES'
    __table_args__ = {'schema': 'gciweb'}

    ID_INSTALACAO = db.Column(db.BigInteger, primary_key=True)
    EMPRESA = db.Column(db.Text, nullable=True)
    INSTALACAO = db.Column(db.Text, nullable=True)
    CNPJ = db.Column(db.Text, nullable=True)
    CPF = db.Column(db.Text, nullable=True)
    STATUS_INSTALACAO = db.Column(db.Text, nullable=True)
    DESCRICAO_STATUS = db.Column(db.Text, nullable=True)
    DESCRICAO_CLASSE = db.Column(db.Text, nullable=True)
    TARIFA = db.Column(db.Text, nullable=True)
    CARGA = db.Column(db.Numeric(10, 2), nullable=True)
    TIPO_CLIENTE = db.Column(db.Text, nullable=True)
    NOME_PARCEIRO = db.Column(db.Text, nullable=True)
    CEP = db.Column(db.Text, nullable=True)


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'gciweb'}

    id_usuario = db.Column(db.BigInteger, primary_key=True)
    matricula = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    admin = db.Column(db.Boolean, nullable=False)
    visualizar = db.Column(db.Boolean, nullable=False)
    criar = db.Column(db.Boolean, nullable=False)
    editar = db.Column(db.Boolean, nullable=False)
    deletar = db.Column(db.Boolean, nullable=False)
    bloqueado = db.Column(db.Boolean, nullable=False, default=False)

    # Relacionamentos
    resp_regioes = db.relationship('RespRegiao', back_populates='usuario', lazy='select')
    estudos_criados = db.relationship('Estudo', foreign_keys='Estudo.id_criado_por', back_populates='criado_por',
                                      lazy='select')
    status_estudos = db.relationship('StatusEstudo', back_populates='criado_por', lazy='select')

    @classmethod
    def get_permissions(id_user):
        pass


class RespRegiao(db.Model):
    __tablename__ = 'resp_regioes'
    __table_args__ = {'schema': 'gciweb'}

    id_resp_regiao = db.Column(db.BigInteger, primary_key=True)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('gciweb.regionais.id_regional'), nullable=False)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('gciweb.usuarios.id_usuario'), nullable=False)
    ano_ref = db.Column(db.Integer, nullable=False)

    # Relacionamentos
    regional = db.relationship('Regional', back_populates='resp_regioes', lazy='joined')
    usuario = db.relationship('Usuario', back_populates='resp_regioes', lazy='joined')
    estudos = db.relationship('Estudo', back_populates='resp_regiao', lazy='select')


class Empresa(db.Model):
    __tablename__ = 'empresas'
    __table_args__ = {'schema': 'gciweb'}

    id_empresa = db.Column(db.BigInteger, primary_key=True)
    nome_empresa = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True)
    abertura = db.Column(db.Date)
    situacao = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    porte = db.Column(db.String(255))
    natureza_juridica = db.Column(db.String(255))
    logradouro = db.Column(db.String(255))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(255))
    municipio = db.Column(db.String(255))
    bairro = db.Column(db.String(255))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(8))
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    data_situacao = db.Column(db.Date)
    ultima_atualizacao = db.Column(db.DateTime)
    status = db.Column(db.String(255))
    fantasia = db.Column(db.String(255))
    efr = db.Column(db.String(255))
    motivo_situacao = db.Column(db.String(255))
    situacao_especial = db.Column(db.String(255))
    data_situacao_especial = db.Column(db.Date)

    # Relacionamentos
    socios = db.relationship('Socio', back_populates='empresa', lazy='select')
    estudos = db.relationship('Estudo', back_populates='empresa', lazy='select')


class Tensao(db.Model):
    __tablename__ = 'tensao'
    __table_args__ = {'schema': 'gciweb'}

    id_tensao = db.Column(db.BigInteger, primary_key=True)
    tensao = db.Column(db.String(2), nullable=False)

    estudos = db.relationship('Estudo', back_populates='tensao', lazy='select')


class Regional(db.Model):
    __tablename__ = 'regionais'
    __table_args__ = {'schema': 'gciweb'}

    id_regional = db.Column(db.BigInteger, primary_key=True)
    regional = db.Column(db.String(255), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='regionais', lazy='joined')
    resp_regioes = db.relationship('RespRegiao', back_populates='regional', lazy='select')
    estudos = db.relationship('Estudo', back_populates='regional', lazy='select')
    obras = db.relationship('Obra', back_populates='regional', lazy='select')
    municipios = db.relationship('Municipio', back_populates='regional', lazy='select')


class Municipio(db.Model):
    __tablename__ = 'municipios'
    __table_args__ = {'schema': 'gciweb'}

    id_municipio = db.Column(db.BigInteger, primary_key=True)
    municipio = db.Column(db.String(255), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('gciweb.regionais.id_regional'), nullable=True)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='municipios', lazy='joined')
    regional = db.relationship('Regional', back_populates='municipios', lazy='joined')
    subestacoes = db.relationship('Subestacao', back_populates='municipio', lazy='select')
    estudos = db.relationship('Estudo', back_populates='municipio', lazy='select')


class Subestacao(db.Model):
    __tablename__ = 'subestacoes'
    __table_args__ = {'schema': 'gciweb'}

    id_subestacao = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    lat = db.Column(db.Numeric(10, 2), nullable=True)
    long = db.Column(db.Numeric(10, 2), nullable=True)
    id_municipio = db.Column(db.BigInteger, db.ForeignKey('gciweb.municipios.id_municipio'), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)

    # Relacionamentos
    municipio = db.relationship('Municipio', back_populates='subestacoes', lazy='joined')
    edp = db.relationship('EDP', back_populates='subestacoes', lazy='joined')
    circuitos = db.relationship('Circuito', back_populates='subestacao', lazy='select')


class Circuito(db.Model):
    __tablename__ = 'circuitos'
    __table_args__ = {'schema': 'gciweb'}

    id_circuito = db.Column(db.BigInteger, primary_key=True)
    circuito = db.Column(db.String(255), nullable=False)
    id_subestacao = db.Column(db.BigInteger, db.ForeignKey('gciweb.subestacoes.id_subestacao'))
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)
    tensao = db.Column(db.String(20), nullable=False)

    # Relacionamentos
    subestacao = db.relationship('Subestacao', back_populates='circuitos', lazy='joined')
    edp = db.relationship('EDP', back_populates='circuitos', lazy='joined')
    alternativas = db.relationship('Alternativa', back_populates='circuito', lazy='select')


class TipoSolicitacao(db.Model):
    __tablename__ = 'tipo_solicitacao'
    __table_args__ = (
        UniqueConstraint('viabilidade', 'analise', 'pedido', name='UQ_tipo_solicitacao_combinacao'),
        {'schema': 'gciweb'}
    )

    id_tipo_solicitacao = db.Column(db.BigInteger, primary_key=True)
    viabilidade = db.Column(db.String(255), nullable=False)
    analise = db.Column(db.String(255), nullable=False)
    pedido = db.Column(db.String(255), nullable=False)

    estudos = db.relationship("Estudo", back_populates="tipo_solicitacao")


class Estudo(db.Model):

    __tablename__ = 'estudos'
    __table_args__ = {'schema': 'gciweb'}

    id_estudo = db.Column(db.BigInteger, primary_key=True)
    num_doc = db.Column(db.String(255), nullable=False, index=True)
    protocolo = db.Column(db.BigInteger)
    nome_projeto = db.Column(db.Text, nullable=False)
    descricao = db.Column(db.Text)
    instalacao = db.Column(db.BigInteger)
    n_alternativas = db.Column(db.Integer, nullable=False, default=0)
    # dem_solicit_fp = db.Column(db.Numeric(10, 2), nullable=False)
    # dem_solicit_p = db.Column(db.Numeric(10, 2), nullable=False)
    dem_carga_atual_fp = db.Column(db.Numeric(10, 2), nullable=False)
    dem_carga_atual_p = db.Column(db.Numeric(10, 2), nullable=False)
    dem_carga_solicit_fp = db.Column(db.Numeric(10, 2), nullable=False)
    dem_carga_solicit_p = db.Column(db.Numeric(10, 2), nullable=False)
    dem_ger_atual_fp = db.Column(db.Numeric(10, 2), nullable=False)
    dem_ger_atual_p = db.Column(db.Numeric(10, 2), nullable=False)
    dem_ger_solicit_fp = db.Column(db.Numeric(10, 2), nullable=False)
    dem_ger_solicit_p = db.Column(db.Numeric(10, 2), nullable=False)

    latitude_cliente = db.Column(db.Numeric(10, 8))
    longitude_cliente = db.Column(db.Numeric(11, 8))
    observacao = db.Column(db.Text)

    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('gciweb.regionais.id_regional'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('gciweb.usuarios.id_usuario'), nullable=False)
    id_resp_regiao = db.Column(db.BigInteger, db.ForeignKey('gciweb.resp_regioes.id_resp_regiao'), nullable=False)
    id_empresa = db.Column(db.BigInteger, db.ForeignKey('gciweb.empresas.id_empresa'))
    id_municipio = db.Column(db.BigInteger, db.ForeignKey('gciweb.municipios.id_municipio'), nullable=False)
    id_tensao = db.Column(db.BigInteger, db.ForeignKey('gciweb.tensao.id_tensao'), nullable=False)
    id_tipo_solicitacao = db.Column(db.BigInteger, db.ForeignKey('gciweb.tipo_solicitacao.id_tipo_solicitacao'), nullable=False)
    data_registro = db.Column(db.Date, nullable=False)
    data_abertura_cliente = db.Column(db.Date, nullable=False)
    data_desejada_cliente = db.Column(db.Date, nullable=False)
    data_vencimento_cliente = db.Column(db.Date, nullable=False)
    data_prevista_conexao = db.Column(db.Date, nullable=False)
    data_vencimento_ddpe = db.Column(db.Date, nullable=False)

    # Relacionamentos com lazy estratégico
    edp = db.relationship('EDP', back_populates='estudos', lazy='joined')
    regional = db.relationship('Regional', back_populates='estudos', lazy='joined')
    criado_por = db.relationship('Usuario', foreign_keys=[id_criado_por], back_populates='estudos_criados', lazy='joined')
    resp_regiao = db.relationship('RespRegiao', back_populates='estudos', lazy='joined')
    empresa = db.relationship('Empresa', back_populates='estudos', lazy='joined')
    municipio = db.relationship('Municipio', back_populates='estudos', lazy='joined')
    tensao = db.relationship('Tensao', back_populates='estudos', lazy='joined')
    tipo_solicitacao = db.relationship('TipoSolicitacao', back_populates='estudos', lazy='joined')

    # Relacionamentos 1:N com lazy='select' para evitar carregamento automático
    anexos = db.relationship('Anexo', back_populates='estudo', lazy='select', cascade='all, delete-orphan')
    status_estudos = db.relationship('StatusEstudo', back_populates='estudo', lazy='select',
                                     cascade='all, delete-orphan', order_by='StatusEstudo.data.desc()')
    alternativas = db.relationship('Alternativa', back_populates='estudo', lazy='select', cascade='all, delete-orphan')

    @classmethod
    def get_with_all_relations(cls, estudo_id):
        """Método para carregar um estudo com todos os relacionamentos necessários de uma vez"""
        return cls.query.options(
            joinedload(cls.edp),
            joinedload(cls.regional),
            joinedload(cls.criado_por),
            joinedload(cls.resp_regiao).joinedload(RespRegiao.usuario),
            joinedload(cls.empresa),
            joinedload(cls.municipio),
            joinedload(cls.tensao),
            joinedload(cls.tipo_solicitacao),
            selectinload(cls.anexos),
            selectinload(cls.status_estudos).joinedload(StatusEstudo.status_tipo),
            selectinload(cls.alternativas).joinedload(Alternativa.circuito),
            selectinload(cls.alternativas).selectinload(Alternativa.obras)).filter_by(id_estudo=estudo_id).first()

    @property
    def ultimo_status(self):
        """Retorna o último status do estudo sem executar uma nova query"""
        if self.status_estudos:
            return self.status_estudos[0]
        return None

    def __repr__(self):
        string = f'''
        Código: {self.num_doc},
        Projeto: {self.nome_projeto},
        Descrição: {self.descricao},
        Município: {self.municipio.municipio},
        Data DDPE: {self.data_vencimento_ddpe}
        '''
        return string


    @classmethod
    def get_list_with_basic_relations(cls):
        """Método otimizado para listar estudos com relacionamentos básicos"""
        return cls.query.options(
            joinedload(cls.regional),
            joinedload(cls.empresa),
            joinedload(cls.municipio),
            joinedload(cls.tipo_solicitacao),
            joinedload(cls.criado_por),
            joinedload(cls.tensao)
        )


class Anexo(db.Model):
    __tablename__ = 'anexos'
    __table_args__ = {'schema': 'gciweb'}

    id_anexo = db.Column(db.BigInteger, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(500), nullable=False)
    tamanho_arquivo = db.Column(db.BigInteger)
    tipo_mime = db.Column(db.String(100))
    data_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('gciweb.estudos.id_estudo'), nullable=False)

    # Relacionamentos
    estudo = db.relationship('Estudo', back_populates='anexos', lazy='joined')


class Socio(db.Model):
    __tablename__ = 'socios'
    __table_args__ = {'schema': 'gciweb'}

    id_socios = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(255))
    id_empresa = db.Column(db.BigInteger, db.ForeignKey('gciweb.empresas.id_empresa'), nullable=False)

    # Relacionamentos
    empresa = db.relationship('Empresa', back_populates='socios', lazy='joined')


class StatusEstudo(db.Model):
    __tablename__ = 'status_estudo'
    __table_args__ = {'schema': 'gciweb'}

    id_status = db.Column(db.BigInteger, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    id_status_tipo = db.Column(db.BigInteger, db.ForeignKey('gciweb.status_tipos.id_status_tipo'), nullable=False, index=True)
    observacao = db.Column(db.Text)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('gciweb.estudos.id_estudo'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('gciweb.usuarios.id_usuario'), nullable=False)

    # Relacionamentos

    estudo = db.relationship('Estudo', back_populates='status_estudos', lazy='joined')
    criado_por = db.relationship('Usuario', back_populates='status_estudos', lazy='joined')
    status_tipo = db.relationship('StatusTipo', back_populates='status_estudos', lazy='joined')


class StatusTipo(db.Model):
    __tablename__ = 'status_tipos'
    __table_args__ = {'schema': 'gciweb'}

    id_status_tipo = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    status_estudos = db.relationship('StatusEstudo', back_populates='status_tipo', lazy='select')


class Kit(db.Model):
    __tablename__ = 'kits'
    __table_args__ = {'schema': 'gciweb'}

    id_kit = db.Column(db.BigInteger, primary_key=True)
    kit = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    valor_unit = db.Column(db.Numeric(15, 2), nullable=False)
    ano_ref = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamentos
    obras = db.relationship('Obra', back_populates='kit', lazy='select')


class Alternativa(db.Model):
    __tablename__ = 'alternativas'
    __table_args__ = {'schema': 'gciweb'}

    id_alternativa = db.Column(db.BigInteger, primary_key=True)
    id_circuito = db.Column(db.BigInteger, db.ForeignKey('gciweb.circuitos.id_circuito'), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    dem_fp_ant = db.Column(db.Numeric(10, 2), nullable=False)
    dem_p_ant = db.Column(db.Numeric(10, 2), nullable=False)
    dem_fp_dep = db.Column(db.Numeric(10, 2), nullable=False)
    dem_p_dep = db.Column(db.Numeric(10, 2), nullable=False)
    latitude_ponto_conexao = db.Column(db.Numeric(10, 8))
    longitude_ponto_conexao = db.Column(db.Numeric(11, 8))
    flag_menor_custo_global = db.Column(db.Boolean, nullable=False, default=False)
    flag_alternativa_escolhida = db.Column(db.Boolean, nullable=False, default=False)
    custo_modular = db.Column(db.Numeric(15, 2), nullable=False)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('gciweb.estudos.id_estudo'), nullable=False)
    blob_image = db.Column(db.Text)
    observacao = db.Column(db.Text)
    ERD = db.Column(db.Numeric(10, 3))
    demanda_disponivel_ponto = db.Column(db.Numeric(10, 2))

    # Relacionamentos simples - sem ambiguidade
    circuito = db.relationship('Circuito', back_populates='alternativas', lazy='joined')
    estudo = db.relationship('Estudo', back_populates='alternativas', lazy='joined')

    # Relacionamento 1:N - Uma alternativa pode ter várias obras
    obras = db.relationship(
        'Obra',
        back_populates='alternativa',
        lazy='select',
        cascade='all, delete-orphan'
    )


class Obra(db.Model):
    __tablename__ = 'obras'
    __table_args__ = {'schema': 'gciweb'}

    id_obra = db.Column(db.BigInteger, primary_key=True)
    quantidade = db.Column(db.Numeric(10, 3), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('gciweb.regionais.id_regional'), nullable=False)
    id_kit = db.Column(db.BigInteger, db.ForeignKey('gciweb.kits.id_kit'), nullable=False)
    id_alternativa = db.Column(db.BigInteger, db.ForeignKey('gciweb.alternativas.id_alternativa'), nullable=False)

    # Relacionamentos simples - sem ambiguidade
    regional = db.relationship('Regional', back_populates='obras', lazy='joined')
    kit = db.relationship('Kit', back_populates='obras', lazy='joined')

    # Relacionamento N:1 - Várias obras podem pertencer a uma alternativa
    alternativa = db.relationship('Alternativa', back_populates='obras', lazy='joined')





# Funções utilitárias para queries otimizadas

# def get_estudos_com_paginacao(page=1, per_page=20, filters=None):
#     """
#     Função otimizada para paginação de estudos evitando N+1
#     """
#     query = Estudo.query.options(
#         joinedload(Estudo.regional),
#         joinedload(Estudo.empresa),
#         joinedload(Estudo.municipio),
#         joinedload(Estudo.tipo_viabilidade),
#         joinedload(Estudo.criado_por)
#     )
#
#     if filters:
#         # Aplicar filtros conforme necessário
#         if 'regional_id' in filters:
#             query = query.filter(Estudo.id_regional == filters['regional_id'])
#         if 'data_inicio' in filters and 'data_fim' in filters:
#             query = query.filter(Estudo.data_criacao.between(filters['data_inicio'], filters['data_fim']))
#
#     return query.order_by(Estudo.data_criacao.desc()).paginate(
#         page=page, per_page=per_page, error_out=False
#     )


def listar_estudos(page, per_page):
    """Lista estudos com paginação otimizada"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Query otimizada evitando N+1
        estudos_paginated = Estudo.query.options(
            db.joinedload(Estudo.regional),
            db.joinedload(Estudo.empresa),
            db.joinedload(Estudo.municipio),
            db.joinedload(Estudo.tipo_solicitacao),
            db.joinedload(Estudo.criado_por),
            db.joinedload(Estudo.resp_regiao).joinedload(RespRegiao.usuario),
            db.selectinload(Estudo.status_estudos).selectinload(StatusEstudo.status_tipo)
        ).order_by(Estudo.id_estudo.desc()) \
            .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )


        estudos_data = []
        for estudo in estudos_paginated.items:
            print(estudo.ultimo_status.status_tipo.status) if estudo.ultimo_status else None

            estudos_data.append({
                'id': estudo.id_estudo,
                'num_doc': estudo.num_doc,
                'nome_projeto': estudo.nome_projeto,
                'regional': estudo.regional.regional if estudo.regional else None,
                'empresa': estudo.empresa.nome_empresa if estudo.empresa else None,
                'municipio': estudo.municipio.municipio if estudo.municipio else None,
                'tipo_solicitacao': estudo.tipo_solicitacao.viabilidade if estudo.tipo_solicitacao else None,
                'eng_responsavel': estudo.resp_regiao.usuario.nome if estudo.resp_regiao else None,
                'criado_por': estudo.criado_por.nome if estudo.criado_por else None,
                'status': estudo.ultimo_status.status_tipo.status if estudo.ultimo_status else "Status não cadastrado",
                'data_registro': estudo.data_registro.isoformat() if estudo.data_registro else None
            })

        return {
            'estudos': estudos_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': estudos_paginated.total,
                'pages': estudos_paginated.pages,
                'has_next': estudos_paginated.has_next,
                'has_prev': estudos_paginated.has_prev
            }
        }

    except Exception as e:
        return {
            'error': 'Erro ao listar estudos',
            'message': str(e)
        }, 500


def obter_estudo(estudo_id):
    """Obtém um estudo específico com todos os relacionamentos"""

    try:
        # Método otimizado que carrega tudo de uma vez
        estudo = Estudo.get_with_all_relations(estudo_id)

        if not estudo:
            return jsonify({'error': 'Estudo não encontrado'}), 404

        estudo_data = {
            'id': estudo.id_estudo,
            'num_doc': estudo.num_doc,
            'protocolo': estudo.protocolo,
            'nome_projeto': estudo.nome_projeto,
            'descricao': estudo.descricao,

            'dem_carga_atual_fp': float(estudo.dem_carga_atual_fp),
            'dem_carga_atual_p': float(estudo.dem_carga_atual_p),
            'dem_carga_solicit_fp': float(estudo.dem_carga_solicit_fp),
            'dem_carga_solicit_p': float(estudo.dem_carga_solicit_p),
            'dem_ger_atual_fp': float(estudo.dem_ger_atual_fp),
            'dem_ger_atual_p': float(estudo.dem_ger_atual_p),
            'dem_ger_solicit_fp': float(estudo.dem_ger_solicit_fp),
            'dem_ger_solicit_p': float(estudo.dem_ger_solicit_p),
            'latitude_cliente': float(estudo.latitude_cliente) if estudo.latitude_cliente else None,
            'longitude_cliente': float(estudo.longitude_cliente) if estudo.longitude_cliente else None,
            'observacao': estudo.observacao,
            'data_registro': estudo.data_registro.isoformat() if estudo.data_registro else None,

            # Relacionamentos (já carregados, sem N+1)
            'regional': {
                'id': estudo.regional.id_regional,
                'nome': estudo.regional.regional
            } if estudo.regional else None,

            'empresa': {
                'id': estudo.empresa.id_empresa,
                'nome': estudo.empresa.nome_empresa,
                'cnpj': estudo.empresa.cnpj
            } if estudo.empresa else None,

            'municipio': {
                'id': estudo.municipio.id_municipio,
                'nome': estudo.municipio.municipio
            } if estudo.municipio else None,

            'tipo_solicitacao': {
                'id': estudo.tipo_solicitacao.id_tipo_solicitacao,
                'viabilidade': estudo.tipo_solicitacao.viabilidade
            } if estudo.tipo_solicitacao else None,

            'criado_por': {
                'id': estudo.criado_por.id_usuario,
                'nome': estudo.criado_por.nome,
                'matricula': estudo.criado_por.matricula
            } if estudo.criado_por else None,

            'responsavel_regiao': {
                'id': estudo.resp_regiao.id_resp_regiao,
                'usuario': {
                    'id': estudo.resp_regiao.usuario.id_usuario,
                    'nome': estudo.resp_regiao.usuario.nome,
                    'matricula': estudo.resp_regiao.usuario.matricula
                }
            } if estudo.resp_regiao and estudo.resp_regiao.usuario else None,

            # Coleções (carregadas com selectinload)
            'anexos': [
                {
                    'id': anexo.id_anexo,
                    'nome_arquivo': anexo.nome_arquivo,
                    'endereco': anexo.endereco,
                    'tamanho_arquivo': anexo.tamanho_arquivo,
                    'tipo_mime': anexo.tipo_mime,
                    'data_upload': anexo.data_upload.isoformat() if anexo.data_upload else None
                }
                for anexo in estudo.anexos
            ],

            'status_historico': [
                {
                    'id': status.id_status,
                    'data': status.data.isoformat() if status.data else None,
                    'status': status.status_tipo.status if status.status_tipo else None,
                    'observacao': status.observacao,
                    'criado_por': status.criado_por.nome if status.criado_por else None
                }
                for status in estudo.status_estudos
            ],

            'alternativas': [
                {
                    'id': alt.id_alternativa,
                    'descricao': alt.descricao,
                    'custo_modular': float(alt.custo_modular),
                    'flag_alternativa_escolhida': alt.flag_alternativa_escolhida,
                    'circuito': {
                        'id': alt.circuito.id_circuito,
                        'nome': alt.circuito.circuito,
                        'tensao': alt.circuito.tensao
                    } if alt.circuito else None
                }
                for alt in estudo.alternativas
            ]
        }

        return estudo_data

    except Exception as e:
        return {
            'error': 'Erro ao obter estudo',
            'message': str(e)
        }, 500


def get_dashboard_stats():
    """
    Função otimizada para estatísticas do dashboard
    """
    return {
        'total_estudos': db.session.query(func.count(Estudo.id_estudo)).scalar(),
        'estudos_por_regional': db.session.query(
            Regional.regional,
            func.count(Estudo.id_estudo)
        ).join(Estudo).group_by(Regional.regional).all(),
        'estudos_por_status': db.session.query(
            StatusEstudo.status,
            func.count(StatusEstudo.id_status)
        ).group_by(StatusEstudo.status).all()
    }

