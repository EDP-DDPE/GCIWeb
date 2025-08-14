from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SelectField, DateField, validators
from wtforms.validators import DataRequired, Optional

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}


class DocumentoForm(FlaskForm):
    protocolo = StringField('Protocolo', validators=[DataRequired()])
    num_doc = StringField('Número do Documento', validators=[DataRequired()])
    nome_cliente = StringField('Nome do Cliente', validators=[DataRequired()])
    cnpj = StringField('CNPJ', validators=[DataRequired()])
    instalacao = StringField('Instalação', validators=[DataRequired()])
    pass
    tipo_viab = SelectField('Tipo de Viabilidade',
                            choices=[('', 'Selecione...'), ('tecnica', 'Técnica'), ('comercial', 'Comercial'),
                                     ('completa', 'Completa')])
    tipo_analise = SelectField('Tipo de Análise',
                               choices=[('', 'Selecione...'), ('preliminar', 'Preliminar'), ('detalhada', 'Detalhada')])
    tipo_pedido = SelectField('Tipo de Pedido',
                              choices=[('', 'Selecione...'), ('novo', 'Novo'), ('alteracao', 'Alteração'),
                                       ('renovacao', 'Renovação')])

    dem_fp_ant = FloatField('Demanda FP Anterior', validators=[Optional()])
    dem_p_ant = FloatField('Demanda P Anterior', validators=[Optional()])
    dem_fp_dep = FloatField('Demanda FP Depois', validators=[Optional()])
    dem_p_dep = FloatField('Demanda P Depois', validators=[Optional()])

    municipio = StringField('Município', validators=[DataRequired()])
    latitude_x = FloatField('Latitude X', validators=[Optional()])
    longitude_y = FloatField('Longitude Y', validators=[Optional()])

    area_resp = SelectField('Área Responsável',
                            choices=[('', 'Selecione...'), ('norte', 'Norte'), ('at', 'AT'), ('projeto', 'Projeto'),
                                     ('guarulhos', 'Guarulhos')])
    elaborador_doc = StringField('Elaborador do Documento', validators=[DataRequired()])
    eng_responsavel = StringField('Engenheiro Responsável', validators=[DataRequired()])

    arquivo = FileField('Anexar Documento',
                        validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Tipo de arquivo não permitido!')])