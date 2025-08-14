from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, func
from sqlalchemy.orm import joinedload, selectinload
from datetime import datetime
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


class Municipio(db.Model):
    __tablename__ = 'municipios'
    __table_args__ = {'schema': 'gciweb'}

    id_municipio = db.Column(db.BigInteger, primary_key=True)
    municipio = db.Column(db.String(255), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='municipios', lazy='joined')
    subestacoes = db.relationship('Subestacao', back_populates='municipio', lazy='select')
    estudos = db.relationship('Estudo', back_populates='municipio', lazy='select')


class Subestacao(db.Model):
    __tablename__ = 'subestacoes'
    __table_args__ = {'schema': 'gciweb'}

    id_subestacao = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
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


class TipoViabilidade(db.Model):
    __tablename__ = 'tipo_viabilidade'
    __table_args__ = {'schema': 'gciweb'}

    id_tipo_viab = db.Column(db.BigInteger, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

    # Relacionamentos
    estudos = db.relationship('Estudo', back_populates='tipo_viabilidade', lazy='select')


class TipoAnalise(db.Model):
    __tablename__ = 'tipo_analise'
    __table_args__ = {'schema': 'gciweb'}

    id_tipo_analise = db.Column(db.BigInteger, primary_key=True)
    analise = db.Column(db.String(255), nullable=False)

    # Relacionamentos
    estudos = db.relationship('Estudo', back_populates='tipo_analise', lazy='select')


class TipoPedido(db.Model):
    __tablename__ = 'tipo_pedido'
    __table_args__ = {'schema': 'gciweb'}

    id_tipo_pedido = db.Column(db.BigInteger, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)

    # Relacionamentos
    estudos = db.relationship('Estudo', back_populates='tipo_pedido', lazy='select')


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
    dem_solicit_fp = db.Column(db.Numeric(10, 2), nullable=False)
    dem_solicit_p = db.Column(db.Numeric(10, 2), nullable=False)
    latitude_cliente = db.Column(db.Numeric(10, 8))
    longitude_cliente = db.Column(db.Numeric(11, 8))
    observacao = db.Column(db.Text)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('gciweb.edp.id_edp'), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('gciweb.regionais.id_regional'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('gciweb.usuarios.id_usuario'), nullable=False)
    id_resp_regiao = db.Column(db.BigInteger, db.ForeignKey('gciweb.resp_regioes.id_resp_regiao'), nullable=False)
    id_empresa = db.Column(db.BigInteger, db.ForeignKey('gciweb.empresas.id_empresa'))
    id_municipio = db.Column(db.BigInteger, db.ForeignKey('gciweb.municipios.id_municipio'), nullable=False)
    id_tipo_viab = db.Column(db.BigInteger, db.ForeignKey('gciweb.tipo_viabilidade.id_tipo_viab'), nullable=False)
    id_tipo_analise = db.Column(db.BigInteger, db.ForeignKey('gciweb.tipo_analise.id_tipo_analise'), nullable=False)
    id_tipo_pedido = db.Column(db.BigInteger, db.ForeignKey('gciweb.tipo_pedido.id_tipo_pedido'), nullable=False)
    data_registro = db.Column(db.Date, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    data_transgressao = db.Column(db.Date)
    data_vencimento = db.Column(db.Date)

    # Relacionamentos com lazy estratégico
    edp = db.relationship('EDP', back_populates='estudos', lazy='joined')
    regional = db.relationship('Regional', back_populates='estudos', lazy='joined')
    criado_por = db.relationship('Usuario', foreign_keys=[id_criado_por], back_populates='estudos_criados',
                                 lazy='joined')
    resp_regiao = db.relationship('RespRegiao', back_populates='estudos', lazy='joined')
    empresa = db.relationship('Empresa', back_populates='estudos', lazy='joined')
    municipio = db.relationship('Municipio', back_populates='estudos', lazy='joined')
    tipo_viabilidade = db.relationship('TipoViabilidade', back_populates='estudos', lazy='joined')
    tipo_analise = db.relationship('TipoAnalise', back_populates='estudos', lazy='joined')
    tipo_pedido = db.relationship('TipoPedido', back_populates='estudos', lazy='joined')

    # Relacionamentos 1:N com lazy='select' para evitar carregamento automático
    anexos = db.relationship('Anexo', back_populates='estudo', lazy='select', cascade='all, delete-orphan')
    status_estudos = db.relationship('StatusEstudo', back_populates='estudo', lazy='select',
                                     cascade='all, delete-orphan', order_by='StatusEstudo.data.desc()')
    alternativas = db.relationship('Alternativa', back_populates='estudo', lazy='select', cascade='all, delete-orphan')

    @property
    def ultimo_status(self):
        """Retorna o último status do estudo sem executar uma nova query"""
        if self.status_estudos:
            return self.status_estudos[0]
        return None

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
            joinedload(cls.tipo_viabilidade),
            joinedload(cls.tipo_analise),
            joinedload(cls.tipo_pedido),
            selectinload(cls.anexos),
            selectinload(cls.status_estudos),
            selectinload(cls.alternativas).joinedload(Alternativa.circuito)
        ).filter_by(id_estudo=estudo_id).first()

    @classmethod
    def get_list_with_basic_relations(cls):
        """Método otimizado para listar estudos com relacionamentos básicos"""
        return cls.query.options(
            joinedload(cls.regional),
            joinedload(cls.empresa),
            joinedload(cls.municipio),
            joinedload(cls.tipo_viabilidade),
            joinedload(cls.criado_por)
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
    status = db.Column(db.String(100), nullable=False)
    observacao = db.Column(db.Text)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('gciweb.estudos.id_estudo'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('gciweb.usuarios.id_usuario'), nullable=False)

    # Relacionamentos
    estudo = db.relationship('Estudo', back_populates='status_estudos', lazy='joined')
    criado_por = db.relationship('Usuario', back_populates='status_estudos', lazy='joined')


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
    id_obra = db.Column(db.BigInteger, db.ForeignKey('gciweb.obras.id_obra'))
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('gciweb.estudos.id_estudo'), nullable=False)
    blob_image = db.Column(db.Text)
    observacao = db.Column(db.Text)
    ERD = db.Column(db.Numeric(10, 3))
    demanda_disponivel_ponto = db.Column(db.Numeric(10, 2))

    # Relacionamentos
    circuito = db.relationship('Circuito', back_populates='alternativas', lazy='joined')
    estudo = db.relationship('Estudo', back_populates='alternativas', lazy='joined')
    obra = db.relationship('Obra', back_populates='alternativa', lazy='joined')
    obras = db.relationship('Obra', foreign_keys='Obra.id_alternativa', back_populates='alternativa', lazy='select')


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

    # Relacionamentos
    regional = db.relationship('Regional', back_populates='obras', lazy='joined')
    kit = db.relationship('Kit', back_populates='obras', lazy='joined')
    alternativa = db.relationship('Alternativa', foreign_keys=[id_alternativa], back_populates='obras', lazy='joined')


class StatusTipo(db.Model):
    __tablename__ = 'status_tipos'
    __table_args__ = {'schema': 'gciweb'}

    id_status_tipo = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)


# Funções utilitárias para queries otimizadas

def get_estudos_com_paginacao(page=1, per_page=20, filters=None):
    """
    Função otimizada para paginação de estudos evitando N+1
    """
    query = Estudo.query.options(
        joinedload(Estudo.regional),
        joinedload(Estudo.empresa),
        joinedload(Estudo.municipio),
        joinedload(Estudo.tipo_viabilidade),
        joinedload(Estudo.criado_por)
    )

    if filters:
        # Aplicar filtros conforme necessário
        if 'regional_id' in filters:
            query = query.filter(Estudo.id_regional == filters['regional_id'])
        if 'data_inicio' in filters and 'data_fim' in filters:
            query = query.filter(Estudo.data_criacao.between(filters['data_inicio'], filters['data_fim']))

    return query.order_by(Estudo.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )


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