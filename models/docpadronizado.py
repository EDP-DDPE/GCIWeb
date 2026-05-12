from database import db

class DocPadronizado(db.Model):
    __tablename__ = 'doc_padronizados'
    __table_args__ = {'schema': 'public'}

    id_doc_padronizado = db.Column(db.BigInteger, primary_key=True)
    nome_doc = db.Column(db.String(255), nullable=False)
    caminho_doc = db.Column(db.String(500), nullable=False)
    tipo_doc = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    data_atualizacao = db.Column(db.DateTime)
    versao = db.Column(db.Integer)
    fluxo_reverso = db.Column(db.Boolean)
    id_tipo_solicitacao = db.Column(
        db.BigInteger,
        db.ForeignKey('public.tipo_solicitacao.id_tipo_solicitacao'),
        nullable=False
    )

    # Relacionamentos
    tipo_solicitacao = db.relationship(
        'TipoSolicitacao',
        back_populates='doc_padronizados',
        lazy='joined'
    )
