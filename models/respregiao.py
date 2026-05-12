from database import db

class RespRegiao(db.Model):
    __tablename__ = 'resp_regioes'
    __table_args__ = {'schema': 'public'}

    id_resp_regiao = db.Column(db.BigInteger, primary_key=True)
    id_regional = db.Column(db.BigInteger, db.ForeignKey('public.regionais.id_regional'), nullable=False)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('public.usuarios.id_usuario'), nullable=False)
    ano_ref = db.Column(db.Integer, nullable=False)

    # Relacionamentos
    regional = db.relationship('Regional', back_populates='resp_regioes', lazy='joined')
    usuario = db.relationship('Usuario', back_populates='resp_regioes', lazy='joined')
    estudos = db.relationship('Estudo', back_populates='resp_regiao', lazy='select')

