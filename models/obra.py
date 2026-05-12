
from database import db

class Obra(db.Model):
    __tablename__ = 'obras'
    __table_args__ = {'schema': 'public'}

    id_obra = db.Column(db.BigInteger, primary_key=True)
    quantidade = db.Column(db.Numeric(10, 3), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('public.regionais.id_regional'), nullable=False)
    id_kit = db.Column(db.BigInteger, db.ForeignKey('public.kits.id_kit'), nullable=False)
    id_alternativa = db.Column(db.BigInteger, db.ForeignKey('public.alternativas.id_alternativa'), nullable=False)

    # Relacionamentos simples - sem ambiguidade
    regional = db.relationship('Regional', back_populates='obras', lazy='joined')
    kit = db.relationship('Kit', back_populates='obras', lazy='joined')

    # Relacionamento N:1 - Várias obras podem pertencer a uma alternativa
    alternativa = db.relationship('Alternativa', back_populates='obras', lazy='joined')
