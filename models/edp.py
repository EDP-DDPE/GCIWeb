from database import db

class EDP(db.Model):
    __tablename__ = 'edp'
    __table_args__ = {'schema': 'public'}

    id_edp = db.Column(db.BigInteger, primary_key=True)
    empresa = db.Column(db.String(2), nullable=False)

    # Relacionamentos com lazy='select' para evitar carregamento desnecessário
    regionais = db.relationship('Regional', back_populates='edp', lazy='select')
    municipios = db.relationship('Municipio', back_populates='edp', lazy='select')
    subestacoes = db.relationship('Subestacao', back_populates='edp', lazy='select')
    circuitos = db.relationship('Circuito', back_populates='edp', lazy='select')
    estudos = db.relationship('Estudo', back_populates='edp', lazy='select')
    usuarios = db.relationship('Usuario', back_populates='edp', lazy='select')
