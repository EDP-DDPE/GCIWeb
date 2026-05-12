from database import db

class Tensao(db.Model):
    __tablename__ = 'tensao'
    __table_args__ = {'schema': 'public'}

    id_tensao = db.Column(db.BigInteger, primary_key=True)
    tensao = db.Column(db.String(2), nullable=False)

    estudos = db.relationship('Estudo', back_populates='tensao', lazy='select')

