from database import db

class Alternativa(db.Model):
    __tablename__ = 'alternativas'
    __table_args__ = {'schema': 'public'}

    id_alternativa = db.Column(db.BigInteger, primary_key=True)
    id_circuito = db.Column(db.BigInteger, db.ForeignKey('public.circuitos.id_circuito'), nullable=False)
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
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('public.estudos.id_estudo'), nullable=False)
    blob_image = db.Column(db.LargeBinary)
    observacao = db.Column(db.Text)
    ERD = db.Column(db.Numeric(10, 3))
    demanda_disponivel_ponto = db.Column(db.Numeric(10, 2))
    flag_carga = db.Column(db.Boolean, nullable=True, default=False)
    flag_geracao = db.Column(db.Boolean, nullable=True, default=False)
    flag_fluxo_reverso = db.Column(db.Boolean, nullable=True, default=False)
    letra_alternativa = db.Column(db.String(1), nullable=True)
    proporcionalidade = db.Column(db.Numeric(3, 2), nullable=True)
    subgrupo_tarifario = db.Column(db.String(3), nullable=True)
    etapa = db.Column(db.BigInteger, nullable=False, default=1)
    id_k = db.Column(db.BigInteger, db.ForeignKey('public.fator_k.id_k'), nullable=True)
    id_img_anexo = db.Column(db.BigInteger, db.ForeignKey('public.anexos.id_anexo'), nullable=True)


    # Relacionamentos simples - sem ambiguidade
    circuito = db.relationship('Circuito', back_populates='alternativas', lazy='joined')
    estudo = db.relationship('Estudo', back_populates='alternativas', lazy='joined')
    fatorK = db.relationship('FatorK', back_populates='alternativas', lazy='joined')
    img_anexo = db.relationship('Anexo', back_populates='alternativas', lazy='joined')

    # Relacionamento 1:N - Uma alternativa pode ter várias obras
    obras = db.relationship(
        'Obra',
        back_populates='alternativa',
        lazy='select',
        cascade='all, delete-orphan'
    )