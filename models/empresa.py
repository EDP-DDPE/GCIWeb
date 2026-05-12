from database import db


class Empresa(db.Model):
    __tablename__ = 'empresas'
    __table_args__ = {'schema': 'public'}

    id_empresa = db.Column(db.BigInteger, primary_key=True)
    nome_empresa = db.Column(db.String(255), nullable=False)
    cnpj = db.Column(db.String(14), nullable=False, unique=True)
    abertura = db.Column(db.Date)
    situacao = db.Column(db.String(255))
    tipo = db.Column(db.String(255))
    porte = db.Column(db.String(255))
    natureza_juridica = db.Column(db.String(255))
    logradouro = db.Column(db.String(255))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(255))
    municipio = db.Column(db.String(255))
    bairro = db.Column(db.String(255))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(8))
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(20))
    data_situacao = db.Column(db.Date)
    ultima_atualizacao = db.Column(db.DateTime)
    status = db.Column(db.String(255))
    fantasia = db.Column(db.String(255))
    efr = db.Column(db.String(255))
    motivo_situacao = db.Column(db.String(255))
    situacao_especial = db.Column(db.String(255))
    data_situacao_especial = db.Column(db.Date)

    # Relacionamentos
    socios = db.relationship('Socio', back_populates='empresa', lazy='select')
    estudos = db.relationship('Estudo', back_populates='empresa', lazy='select')
