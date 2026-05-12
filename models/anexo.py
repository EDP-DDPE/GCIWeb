from database import db
from datetime import datetime

class Anexo(db.Model):
    __tablename__ = 'anexos'
    __table_args__ = {'schema': 'public'}

    id_anexo = db.Column(db.BigInteger, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.String(500), nullable=False)
    tamanho_arquivo = db.Column(db.BigInteger)
    tipo_mime = db.Column(db.String(100))
    data_upload = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    id_estudo = db.Column(db.BigInteger, db.ForeignKey('public.estudos.id_estudo'), nullable=False)

    # Relacionamentos
    estudo = db.relationship('Estudo', back_populates='anexos', lazy='joined')
    alternativas = db.relationship('Alternativa', back_populates='img_anexo', lazy='select')
