from pydantic import BaseModel
from typing import Optional

class CandidatoInfosBasicasBase(BaseModel):
    codigo_profissional: Optional[int] = None
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    telefone_recado: Optional[str] = None
    objetivo_profissional: Optional[str] = None
    data_criacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
    inserido_por: Optional[str] = None
    local: Optional[str] = None
    sabendo_de_nos_por: Optional[str] = None

    class Config:
        from_attributes = True


class CandidatoInformacoesPessoaisBase(BaseModel):
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone_celular: Optional[str] = None
    telefone_recado: Optional[str] = None
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    pcd: Optional[str] = None
    endereco: Optional[str] = None
    skype: Optional[str] = None
    url_linkedin: Optional[str] = None
    facebook: Optional[str] = None
    fonte_indicacao: Optional[str] = None
    email_secundario: Optional[str] = None
    data_aceite: Optional[str] = None

    class Config:
        from_attributes = True


class CandidatoInformacoesProfissionaisBase(BaseModel):
    titulo_profissional: Optional[str] = None
    area_atuacao: Optional[str] = None
    conhecimentos_tecnicos: Optional[str] = None
    certificacoes: Optional[str] = None
    outras_certificacoes: Optional[str] = None
    remuneracao: Optional[str] = None
    nivel_profissional: Optional[str] = None

    class Config:
        from_attributes = True


class CandidatoFormacaoEIdiomasBase(BaseModel):
    nivel_academico: Optional[str] = None
    nivel_ingles: Optional[str] = None
    nivel_espanhol: Optional[str] = None
    outro_idioma: Optional[str] = None

    class Config:
        from_attributes = True


class CandidatoCurriculosBase(BaseModel):
    cv_pt: Optional[str] = None

    class Config:
        from_attributes = True


# Schemas para criação e atualização
class CandidatoCreate(BaseModel):
    infos_basicas: CandidatoInfosBasicasBase
    informacoes_pessoais: Optional[CandidatoInformacoesPessoaisBase] = None
    informacoes_profissionais: Optional[CandidatoInformacoesProfissionaisBase] = None
    formacao_e_idiomas: Optional[CandidatoFormacaoEIdiomasBase] = None
    curriculos: Optional[CandidatoCurriculosBase] = None


class CandidatoUpdate(BaseModel):
    infos_basicas: Optional[CandidatoInfosBasicasBase] = None
    informacoes_pessoais: Optional[CandidatoInformacoesPessoaisBase] = None
    informacoes_profissionais: Optional[CandidatoInformacoesProfissionaisBase] = None
    formacao_e_idiomas: Optional[CandidatoFormacaoEIdiomasBase] = None
    curriculos: Optional[CandidatoCurriculosBase] = None