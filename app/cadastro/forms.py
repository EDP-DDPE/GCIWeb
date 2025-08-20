from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SelectField, DateField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import date


ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'dwg', 'kmz', 'kml'}


class DocumentoForm(FlaskForm):
    protocolo = StringField('Protocolo', validators=[DataRequired()])
    num_doc = StringField('Número do Documento', validators=[DataRequired()])
    nome_cliente = StringField('Nome do Cliente', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired()])
    instalacao = StringField('Instalação', validators=[DataRequired()])
    pass
    tipo_viab = SelectField('Tipo de Viabilidade', coerce=int, validators=[DataRequired()])
    tipo_analise = SelectField('Tipo de Análise', coerce=int, validators=[DataRequired()])
    tipo_pedido = SelectField('Tipo de Pedido', coerce=int, validators=[DataRequired()])

    dem_fp_ant = FloatField('Demanda FP Anterior', validators=[Optional()])
    dem_p_ant = FloatField('Demanda P Anterior', validators=[Optional()])
    dem_fp_dep = FloatField('Demanda FP Depois', validators=[Optional()])
    dem_p_dep = FloatField('Demanda P Depois', validators=[Optional()])

    municipio = SelectField("Município", coerce=int, validators=[DataRequired()])
    latitude_x = FloatField('Latitude X', validators=[Optional()])
    longitude_y = FloatField('Longitude Y', validators=[Optional()])

    area_resp = SelectField('Área Responsável',
                            choices=[(0, 'Selecione...'), ('norte', 'Norte'), ('at', 'AT'), ('projeto', 'Projeto'),
                                     ('guarulhos', 'Guarulhos')])
    elaborador_doc = StringField('Elaborador do Documento', validators=[DataRequired()])
    eng_responsavel = StringField('Engenheiro Responsável', validators=[DataRequired()])

    arquivo = FileField('Anexar Documento',
                        validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Tipo de arquivo não permitido!')])

    # SelectFields para relacionamentos (você vai popular com query do banco)
    empresa = SelectField("Empresa", coerce=int, validators=[DataRequired()])
    regional = SelectField("Regional", coerce=int, validators=[DataRequired()])


class EstudoForm(FlaskForm):
    # Campos básicos do estudo
    num_doc = StringField('Número do Documento', validators=[DataRequired()])
    protocolo = StringField('Protocolo', validators=[Optional()])
    nome_projeto = TextAreaField('Nome do Projeto', validators=[DataRequired()])
    descricao = TextAreaField('Descrição', validators=[Optional()])

    # Campo instalação (pode ser um número ou texto dependendo do uso)
    instalacao = StringField('Instalação', validators=[Optional()])

    # Número de alternativas
    n_alternativas = IntegerField('Número de Alternativas',
                                  validators=[Optional(), NumberRange(min=0)],
                                  default=0)

    # Demandas solicitadas
    dem_solicit_fp = FloatField('Demanda Solicitada FP (kW)',
                                validators=[DataRequired(), NumberRange(min=0)])
    dem_solicit_p = FloatField('Demanda Solicitada P (kW)',
                               validators=[DataRequired(), NumberRange(min=0)])

    # Coordenadas do cliente
    latitude_cliente = FloatField('Latitude do Cliente',
                                  validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude_cliente = FloatField('Longitude do Cliente',
                                   validators=[Optional(), NumberRange(min=-180, max=180)])

    # Observações
    observacao = TextAreaField('Observações', validators=[Optional()])

    # Datas
    data_registro = DateField('Data de Registro',
                              validators=[DataRequired()],
                              default=date.today)
    data_transgressao = DateField('Data de Transgressão', validators=[Optional()])
    data_vencimento = DateField('Data de Vencimento', validators=[Optional()])

    # SelectFields para relacionamentos
    edp = SelectField('EDP', coerce=int, validators=[DataRequired()])
    empresa = SelectField('Empresa', coerce=int, validators=[Optional()])
    regional = SelectField('Regional', coerce=int, validators=[DataRequired()])
    municipio = SelectField('Município', coerce=int, validators=[DataRequired()])
    resp_regiao = SelectField('Responsável da Região', coerce=int, validators=[DataRequired()])

    # Tipos
    tipo_viab = SelectField('Tipo de Viabilidade', coerce=int, validators=[DataRequired()])
    tipo_analise = SelectField('Tipo de Análise', coerce=int, validators=[DataRequired()])
    tipo_pedido = SelectField('Tipo de Pedido', coerce=int, validators=[DataRequired()])

    # Arquivo anexo (opcional no cadastro inicial)
    arquivo = FileField('Anexar Documento',
                        validators=[FileAllowed(ALLOWED_EXTENSIONS, 'Tipo de arquivo não permitido!')])

    def __init__(self, *args, **kwargs):
        super(EstudoForm, self).__init__(*args, **kwargs)
        # Adicionar opção vazia para campos opcionais
        self.empresa.choices = [(0, 'Selecione uma empresa...')]
        self.edp.choices = [(1, 'Selecione uma EDP...')]
        self.regional.choices = [(0, 'Selecione uma regional...')]
        self.municipio.choices = [(0, 'Selecione um município...')]
        self.resp_regiao.choices = [(0, 'Selecione um responsável...')]
        self.tipo_viab.choices = [(0, 'Selecione um tipo...')]
        self.tipo_analise.choices = [(0, 'Selecione um tipo...')]
        self.tipo_pedido.choices = [(0, 'Selecione um tipo...')]

#TODO Adicionar campo com Livre e Cativo (Alterar modelagem SQL, models, forms e o html)
#TODO Alterar a demanda antes e migrar para Estudos
#TODO Separar demanda de carga e geração
#TODO Adionar data desejada pelo cliente, data prevista de energização pela EDP, adicionar data de inicio do processo
#TODO ALterar data transgressão para prazo interno
#TODO Salvar anexos por protocolo


class AlternativaForm(FlaskForm):
    """Formulário para cadastro de alternativas de um estudo"""
    descricao = TextAreaField('Descrição da Alternativa', validators=[DataRequired()])

    # Demandas antes e depois
    dem_fp_ant = FloatField('Demanda FP Anterior (kW)',
                            validators=[DataRequired(), NumberRange(min=0)])
    dem_p_ant = FloatField('Demanda P Anterior (kW)',
                           validators=[DataRequired(), NumberRange(min=0)])
    dem_fp_dep = FloatField('Demanda FP Depois (kW)',
                            validators=[DataRequired(), NumberRange(min=0)])
    dem_p_dep = FloatField('Demanda P Depois (kW)',
                           validators=[DataRequired(), NumberRange(min=0)])

    # Coordenadas do ponto de conexão
    latitude_ponto_conexao = FloatField('Latitude Ponto de Conexão',
                                        validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude_ponto_conexao = FloatField('Longitude Ponto de Conexão',
                                         validators=[Optional(), NumberRange(min=-180, max=180)])

    # Custo modular
    custo_modular = FloatField('Custo Modular (R$)',
                               validators=[DataRequired(), NumberRange(min=0)])

    # Campos opcionais
    ERD = FloatField('ERD', validators=[Optional(), NumberRange(min=0)])
    demanda_disponivel_ponto = FloatField('Demanda Disponível no Ponto (kW)',
                                          validators=[Optional(), NumberRange(min=0)])
    observacao = TextAreaField('Observações', validators=[Optional()])

    # Relacionamentos
    circuito = SelectField('Circuito', coerce=int, validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(AlternativaForm, self).__init__(*args, **kwargs)
        self.circuito.choices = [(0, 'Selecione um circuito...')]

class AnexoForm(FlaskForm):
    """Formulário para upload de anexos"""
    arquivo = FileField('Selecionar Arquivo',
                        validators=[DataRequired(),
                                    FileAllowed(ALLOWED_EXTENSIONS, 'Tipo de arquivo não permitido!')])

    descricao = StringField('Descrição do Arquivo', validators=[Optional()])