from database import db
from sqlalchemy import UniqueConstraint

class TipoSolicitacao(db.Model):
    __tablename__ = 'tipo_solicitacao'
    __table_args__ = (
        UniqueConstraint('viabilidade', 'analise', 'pedido', name='UQ_tipo_solicitacao_combinacao'),
        {'schema': 'public'}
    )

    id_tipo_solicitacao = db.Column(db.BigInteger, primary_key=True)
    viabilidade = db.Column(db.String(255), nullable=False)
    analise = db.Column(db.String(255), nullable=False)
    pedido = db.Column(db.String(255), nullable=False)
    viabilidade_abrev = db.Column(db.String(255))
    analise_abrev = db.Column(db.String(255))
    pedido_abrev = db.Column(db.String(255))

    estudos = db.relationship("Estudo", back_populates="tipo_solicitacao", passive_deletes=True)
    doc_padronizados = db.relationship('DocPadronizado',back_populates='tipo_solicitacao',lazy='select')
