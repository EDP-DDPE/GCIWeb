from database import db

class Socio(db.Model):
    __tablename__ = 'socios'
    __table_args__ = {'schema': 'public'}

    id_socios = db.Column(db.BigInteger, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(255))
    id_empresa = db.Column(db.BigInteger, db.ForeignKey('public.empresas.id_empresa'), nullable=False)

    # Relacionamentos
    empresa = db.relationship('Empresa', back_populates='socios', lazy='joined')


