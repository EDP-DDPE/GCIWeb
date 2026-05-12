from database import db
from sqlalchemy import desc
from datetime import datetime

class StatusEstudo(db.Model):
    __tablename__ = 'status_estudo'
    __table_args__ = {'schema': 'public'}

    id_status = db.Column(db.BigInteger, primary_key=True)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    id_status_tipo = db.Column(db.BigInteger, db.ForeignKey('public.status_tipos.id_status_tipo'), nullable=False,
                               index=True)
    observacao = db.Column(db.Text)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('public.estudos.id_estudo'), nullable=False)
    id_criado_por = db.Column(db.BigInteger, db.ForeignKey('public.usuarios.id_usuario'), nullable=False)

    # Relacionamentos

    estudo = db.relationship('Estudo', back_populates='status_estudos', lazy='joined')
    criado_por = db.relationship('Usuario', back_populates='status_estudos', lazy='joined')
    status_tipo = db.relationship('StatusTipo', back_populates='status_estudos', lazy='joined')

    @property
    def status_mais_recente(self):
        return (
            StatusEstudo.query
            .filter_by(id_estudo=self.id_estudo)
            .order_by(desc(StatusEstudo.data))
            .first()
        )


class StatusTipo(db.Model):
    __tablename__ = 'status_tipos'
    __table_args__ = {'schema': 'public'}

    id_status_tipo = db.Column(db.BigInteger, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, nullable=False, default=True)

    status_estudos = db.relationship('StatusEstudo', back_populates='status_tipo', lazy='select')
