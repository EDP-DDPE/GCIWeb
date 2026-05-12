from database import db


class Subestacao(db.Model):
    __tablename__ = 'subestacoes'
    __table_args__ = {'schema': 'public'}

    id_subestacao = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    sigla = db.Column(db.String(10), nullable=False)
    lat = db.Column(db.Numeric(10, 2), nullable=True)
    long = db.Column(db.Numeric(10, 2), nullable=True)
    id_municipio = db.Column(db.BigInteger, db.ForeignKey('public.municipios.id_municipio'), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)

    # Relacionamentos
    municipio = db.relationship('Municipio', back_populates='subestacoes', lazy='joined')
    edp = db.relationship('EDP', back_populates='subestacoes', lazy='joined')
    circuitos = db.relationship('Circuito', back_populates='subestacao', lazy='select', passive_deletes=True)
