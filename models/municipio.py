from database import db

class Municipio(db.Model):
    __tablename__ = 'municipios'
    __table_args__ = {'schema': 'public'}

    id_municipio = db.Column(db.BigInteger, primary_key=True)
    municipio = db.Column(db.String(255), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('public.regionais.id_regional'), nullable=True)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='municipios', lazy='joined')
    regional = db.relationship('Regional', back_populates='municipios', lazy='joined')
    subestacoes = db.relationship('Subestacao', back_populates='municipio', lazy='select')
    estudos = db.relationship('Estudo', back_populates='municipio', lazy='select')
