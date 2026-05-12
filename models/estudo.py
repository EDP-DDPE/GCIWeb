from database import db
from sqlalchemy.orm import joinedload, selectinload, column_property
from sqlalchemy import select


from .respregiao import RespRegiao
from .status import StatusEstudo
from .alternativa import Alternativa


class Estudo(db.Model):
    __tablename__ = 'estudos'
    __table_args__ = {'schema': 'public'}

    id_estudo = db.Column(db.BigInteger, primary_key=True)
    num_doc = db.Column(db.String(255), nullable=False, index=True)
    protocolo = db.Column(db.BigInteger)
    nome_projeto = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text)
    instalacao = db.Column(db.BigInteger)
    n_alternativas = db.Column(db.Integer, nullable=False, default=0)
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

    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('public.regionais.id_regional'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('public.usuarios.id_usuario'), nullable=False)
    id_resp_alteracao = db.Column(db.BigInteger, db.ForeignKey('public.usuarios.id_usuario'), nullable=False)
    id_resp_regiao = db.Column(db.BigInteger, db.ForeignKey('public.resp_regioes.id_resp_regiao'), nullable=True)
    id_empresa = db.Column(db.BigInteger, db.ForeignKey('public.empresas.id_empresa'))
    id_municipio = db.Column(db.BigInteger, db.ForeignKey('public.municipios.id_municipio'), nullable=False)
    id_tensao = db.Column(db.BigInteger, db.ForeignKey('public.tensao.id_tensao'), nullable=False)
    id_tipo_solicitacao = db.Column(db.BigInteger, db.ForeignKey('public.tipo_solicitacao.id_tipo_solicitacao'),
                                    nullable=False)
    data_registro = db.Column(db.Date, nullable=False)
    data_abertura_cliente = db.Column(db.Date, nullable=False)
    data_desejada_cliente = db.Column(db.Date, nullable=False)
    data_vencimento_cliente = db.Column(db.Date, nullable=False)
    data_prevista_conexao = db.Column(db.Date, nullable=False)
    data_vencimento_ddpe = db.Column(db.Date, nullable=False)
    data_alteracao = db.Column(db.Date, nullable=True)
    tipo_geracao = db.Column(db.String(255), nullable=True)

    id_status_ultimo = column_property(
        select(StatusEstudo.id_status)
        .where(StatusEstudo.id_estudo == id_estudo)
        .order_by(StatusEstudo.data.desc())
        .limit(1)
        .correlate_except(StatusEstudo)
        .scalar_subquery()
    )


    # Relacionamentos com lazy estratégico
    edp = db.relationship('EDP', back_populates='estudos', lazy='joined')
    regional = db.relationship('Regional', back_populates='estudos', lazy='joined')
    criado_por = db.relationship('Usuario', foreign_keys=[id_criado_por], back_populates='estudos_criados',
                                 lazy='joined')
    alterado_por = db.relationship('Usuario', foreign_keys=[id_resp_alteracao], back_populates='resp_alteracao',
                                   lazy='joined')
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
        if self.id_status_ultimo:
            return StatusEstudo.query.get(self.id_status_ultimo)
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







class ViewEstudos(db.Model):
    __tablename__ = "vw_estudos_completos"
    __table_args__ = {"schema": "public"}

    id_estudo = db.Column(db.Integer, primary_key=True)
    num_doc = db.Column(db.String)
    protocolo = db.Column(db.String)
    nome_projeto = db.Column(db.String)
    descricao = db.Column(db.String)
    instalacao = db.Column(db.String)
    n_alternativas = db.Column(db.Integer)
    latitude_cliente = db.Column(db.Float)
    longitude_cliente = db.Column(db.Float)
    observacao = db.Column(db.String)
    empresa = db.Column(db.String)
    regional = db.Column(db.String)
    nome_criador = db.Column(db.String)
    nome_responsavel = db.Column(db.String)
    nome_empresa = db.Column(db.String)
    municipio = db.Column(db.String)
    data_registro = db.Column(db.DateTime)
    viabilidade = db.Column(db.String)
    analise = db.Column(db.String)
    pedido = db.Column(db.String)
    data_abertura_cliente = db.Column(db.DateTime)
    data_desejada_cliente = db.Column(db.DateTime)
    data_vencimento_cliente = db.Column(db.DateTime)
    data_prevista_conexao = db.Column(db.DateTime)
    data_vencimento_ddpe = db.Column(db.DateTime)
    dem_carga_atual_fp = db.Column(db.Float)
    dem_carga_atual_p = db.Column(db.Float)
    dem_carga_solicit_fp = db.Column(db.Float)
    dem_carga_solicit_p = db.Column(db.Float)
    dem_ger_atual_fp = db.Column(db.Float)
    dem_ger_atual_p = db.Column(db.Float)
    dem_ger_solicit_fp = db.Column(db.Float)
    dem_ger_solicit_p = db.Column(db.Float)
    tensao = db.Column(db.Integer)
    data_alteracao = db.Column(db.DateTime)
    qtd_anexos = db.Column(db.Integer)
    ultimo_status = db.Column(db.String)
    id_alternativa = db.Column(db.Integer)
    alternativa_descricao = db.Column(db.String)
    alternativa_dem_fp_ant = db.Column(db.Float)
    alternativa_dem_p_ant = db.Column(db.Float)
    alternativa_dem_fp_dep = db.Column(db.Float)
    alternativa_dem_p_dep = db.Column(db.Float)
    alternativa_circuito = db.Column(db.String)
    subestacao = db.Column(db.String)
    sigla_subestacao = db.Column(db.String)
    fronteira = db.Column(db.Boolean)
    custo_modular = db.Column(db.Float)
    subgrupo_tarifario = db.Column(db.String)
    etapa = db.Column(db.String)
    ERD = db.Column(db.Float)
    demanda_disponivel_ponto = db.Column(db.Float)
    proporcionalidade = db.Column(db.Float)
    flag_alternativa_escolhida = db.Column(db.Boolean)
    flag_menor_custo_global = db.Column(db.Boolean)
    flag_carga = db.Column(db.Boolean)
    flag_geracao = db.Column(db.Boolean)
    alternativa_observacao = db.Column(db.String)
