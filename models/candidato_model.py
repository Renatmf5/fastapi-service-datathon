from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from typing import Optional, List

class CandidatoInfosBasicas(SQLModel, table=True):
    __tablename__ = "candidato_infos_basicas"
    codigo_profissional: Optional[int] = Field(default=None, primary_key=True, index=True)
    nome: str
    email: Optional[str] = None
    telefone: Optional[str] = None
    telefone_recado: Optional[str] = None
    objetivo_profissional: Optional[str] = Field(default=None, sa_column=Column(Text))
    data_criacao: Optional[str] = None
    data_atualizacao: Optional[str] = None
    inserido_por: Optional[str] = None
    local: Optional[str] = None
    sabendo_de_nos_por: Optional[str] = Field(default=None, sa_column=Column(Text))

    # Relacionamento com outras tabelas
    informacoes_pessoais: Optional["CandidatoInformacoesPessoais"] = Relationship(back_populates="infos_basicas")
    informacoes_profissionais: Optional["CandidatoInformacoesProfissionais"] = Relationship(back_populates="infos_basicas")
    formacao_e_idiomas: Optional["CandidatoFormacaoEIdiomas"] = Relationship(back_populates="infos_basicas")
    curriculos: Optional["CandidatoCurriculos"] = Relationship(back_populates="infos_basicas")
    prospects: List["Prospect"] = Relationship(back_populates="candidato")  # Relacionamento com Prospect


class CandidatoInformacoesPessoais(SQLModel, table=True):
    __tablename__ = "candidato_informacoes_pessoais"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_profissional: int = Field(foreign_key="candidato_infos_basicas.codigo_profissional")
    nome: Optional[str] = None
    cpf: Optional[str] = None
    telefone_celular: Optional[str] = None
    telefone_recado: Optional[str] = None
    data_nascimento: Optional[str] = None
    sexo: Optional[str] = None
    estado_civil: Optional[str] = None
    pcd: Optional[str] = None
    endereco: Optional[str] = Field(default=None, sa_column=Column(Text))
    skype: Optional[str] = None
    url_linkedin: Optional[str] = Field(default=None, sa_column=Column(Text))
    facebook: Optional[str] = None
    fonte_indicacao: Optional[str] = Field(default=None, sa_column=Column(Text))
    email_secundario: Optional[str] = None
    data_aceite: Optional[str] = None

    infos_basicas: Optional[CandidatoInfosBasicas] = Relationship(back_populates="informacoes_pessoais")


class CandidatoInformacoesProfissionais(SQLModel, table=True):
    __tablename__ = "candidato_informacoes_profissionais"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_profissional: int = Field(foreign_key="candidato_infos_basicas.codigo_profissional")
    titulo_profissional: Optional[str] = Field(default=None, sa_column=Column(Text))
    area_atuacao: Optional[str] = Field(default=None, sa_column=Column(Text))
    conhecimentos_tecnicos: Optional[str] = Field(default=None, sa_column=Column(Text))
    certificacoes: Optional[str] = Field(default=None, sa_column=Column(Text))
    outras_certificacoes: Optional[str] = Field(default=None, sa_column=Column(Text))
    remuneracao: Optional[str] = None
    nivel_profissional: Optional[str] = None

    infos_basicas: Optional[CandidatoInfosBasicas] = Relationship(back_populates="informacoes_profissionais")


class CandidatoFormacaoEIdiomas(SQLModel, table=True):
    __tablename__ = "candidato_formacao_e_idiomas"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_profissional: int = Field(foreign_key="candidato_infos_basicas.codigo_profissional")
    nivel_academico: Optional[str] = None
    nivel_ingles: Optional[str] = None
    nivel_espanhol: Optional[str] = None
    outro_idioma: Optional[str] = None

    infos_basicas: Optional[CandidatoInfosBasicas] = Relationship(back_populates="formacao_e_idiomas")


class CandidatoCurriculos(SQLModel, table=True):
    __tablename__ = "candidato_curriculos"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_profissional: int = Field(foreign_key="candidato_infos_basicas.codigo_profissional")
    cv_pt: Optional[str] = Field(default=None, sa_column=Column(Text))

    infos_basicas: Optional[CandidatoInfosBasicas] = Relationship(back_populates="curriculos")