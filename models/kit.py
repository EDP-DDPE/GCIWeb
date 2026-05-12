from database import db

class Kit(db.Model):
    __tablename__ = 'kits'
    __table_args__ = {'schema': 'public'}

    id_kit = db.Column(db.BigInteger, primary_key=True)
    kit = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500), nullable=False)
    valor_unit = db.Column(db.Numeric(15, 2), nullable=False)
    ano_ref = db.Column(db.Integer, nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamentos
    obras = db.relationship('Obra', back_populates='kit', lazy='select')
