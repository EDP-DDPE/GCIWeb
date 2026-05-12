from database import db

class Instalacao(db.Model):
    __tablename__ = 'instalacoes'
    __table_args__ = {'schema': 'public'}

    #ID_INSTALACAO = db.Column(db.BigInteger, primary_key=True)
    EMPRESA = db.Column(db.Text, nullable=True)
    INSTALACAO = db.Column(db.Text, primary_key=True)
    CNPJ = db.Column(db.Text, nullable=True)
    # CPF = db.Column(db.Text, nullable=True)
    STATUS_INSTALACAO = db.Column(db.Text, nullable=True)
    DESCRICAO_STATUS = db.Column(db.Text, nullable=True)
    DESCRICAO_CLASSE = db.Column(db.Text, nullable=True)
    TARIFA = db.Column(db.Text, nullable=True)
    CARGA = db.Column(db.Numeric(10, 2), nullable=True)
    TIPO_CLIENTE = db.Column(db.Text, nullable=True)
    NOME_PARCEIRO = db.Column(db.Text, nullable=True)
    CEP = db.Column(db.Text, nullable=True)