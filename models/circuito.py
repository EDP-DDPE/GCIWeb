from database import db

class Circuito(db.Model):
    __tablename__ = 'circuitos'
    __table_args__ = {'schema': 'public'}

    id_circuito = db.Column(db.BigInteger, primary_key=True)
    circuito = db.Column(db.String(255), nullable=False)
    id_subestacao = db.Column(db.BigInteger, db.ForeignKey('public.subestacoes.id_subestacao'))
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)
    tensao = db.Column(db.String(20), nullable=False)

    # Relacionamentos
    subestacao = db.relationship('Subestacao', back_populates='circuitos', lazy='joined')
    edp = db.relationship('EDP', back_populates='circuitos', lazy='joined')
    alternativas = db.relationship('Alternativa', back_populates='circuito', lazy='select', passive_deletes=True)

    def to_dict(self):
        return {
            'id_circuito': self.id_circuito,
            'circuito': self.circuito,
            'tensao': self.tensao,
            'edp': {
                'empresa': self.edp.empresa if self.edp else None
            },
            'subestacao': {
                'nome': self.subestacao.nome if self.subestacao else None
            }
        }
