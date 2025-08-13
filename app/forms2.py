# Formulários
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FloatField, SelectField, DateField, validators
from wtforms.validators import DataRequired, Optional

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'}


class StatusForm(FlaskForm):
    protocolo = StringField('Protocolo', validators=[DataRequired()])
    dt_criacao = DateField('Data de Criação', validators=[Optional()])
    dt_concl = DateField('Data de Conclusão', validators=[Optional()])
    dt_transgressao = DateField('Data de Transgressão', validators=[Optional()])
    status = SelectField('Status',
                         choices=[('', 'Selecione...'), ('pendente', 'Pendente'), ('em_andamento', 'Em Andamento'),
                                  ('concluido', 'Concluído'), ('cancelado', 'Cancelado')])
    dt_fim = DateField('Data de Fim', validators=[Optional()])

