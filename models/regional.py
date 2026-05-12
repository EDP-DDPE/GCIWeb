from database import db

class Regional(db.Model):
    __tablename__ = 'regionais'
    __table_args__ = {'schema': 'public'}

    id_regional = db.Column(db.BigInteger, primary_key=True)
    regional = db.Column(db.String(255), nullable=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='regionais', lazy='joined')
    resp_regioes = db.relationship('RespRegiao', back_populates='regional', lazy='select')
    estudos = db.relationship('Estudo', back_populates='regional', lazy='select')
    obras = db.relationship('Obra', back_populates='regional', lazy='select')
    municipios = db.relationship('Municipio', back_populates='regional', lazy='select')

