from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date


class RegionalSchema(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class EmpresaSchema(BaseModel):
    id: int
    nome: str
    cnpj: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MunicipioSchema(BaseModel):
    id: int
    nome: str

    model_config = ConfigDict(from_attributes=True)


class TipoSolicitacaoSchema(BaseModel):
    id: int
    viabilidade: str
    analise: str
    pedido: str

    model_config = ConfigDict(from_attributes=True)


class UsuarioSchema(BaseModel):
    id: int
    nome: str
    matricula: str

    model_config = ConfigDict(from_attributes=True)


class EstudoListSchema(BaseModel):
    id: int
    num_doc: str
    nome_projeto: str

    regional: Optional[str]
    empresa: Optional[str]
    municipio: Optional[str]

    tipo_solicitacao: Optional[str]

    eng_responsavel: Optional[str]
    criado_por: Optional[str]

    status: Optional[str]

    qtd_alternativas: int
    qtd_anexos: int

    data_registro: Optional[date]