from database import db

class FatorK(db.Model):
    __tablename__ = 'fator_k'
    __table_args__ = {'schema': 'public'}

    id_k = db.Column(db.BigInteger, primary_key=True)
    k = db.Column(db.Numeric(6, 2), nullable=True)
    kg = db.Column(db.Numeric(6, 2), nullable=True)
    subgrupo_tarif = db.Column(db.String(3), nullable=False)
    data_ref = db.Column(db.Date)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)

    alternativas = db.relationship('Alternativa', back_populates='fatorK', lazy='select')