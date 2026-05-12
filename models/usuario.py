from database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'schema': 'public'}

    id_usuario = db.Column(db.BigInteger, primary_key=True)
    matricula = db.Column(db.String(255), nullable=False, unique=True)
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text)
    admin = db.Column(db.Boolean, nullable=False)
    visualizar = db.Column(db.Boolean, nullable=False)
    criar = db.Column(db.Boolean, nullable=False)
    editar = db.Column(db.Boolean, nullable=False)
    deletar = db.Column(db.Boolean, nullable=False)
    bloqueado = db.Column(db.Boolean, nullable=False, default=False)
    id_edp = db.Column(db.BigInteger, db.ForeignKey('public.edp.id_edp'), nullable=False)
    aprovar = db.Column(db.Boolean, nullable=False, default=False)

    # Relacionamentos
    edp = db.relationship('EDP', back_populates='usuarios', lazy='joined')

    resp_regioes = db.relationship('RespRegiao', back_populates='usuario', lazy='select')
    estudos_criados = db.relationship('Estudo', foreign_keys='Estudo.id_criado_por', back_populates='criado_por',
                                      lazy='select')
    resp_alteracao = db.relationship('Estudo', foreign_keys='Estudo.id_resp_alteracao', back_populates='alterado_por',
                                     lazy='select')
    status_estudos = db.relationship('StatusEstudo', back_populates='criado_por', lazy='select')

    @classmethod
    def get_permissions(id_user):
        pass

