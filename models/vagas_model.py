from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text
from typing import List, Optional


class VagaInfosBasicas(SQLModel, table=True):
    __tablename__ = "vaga_infos_basicas"
    # Usando Integer com auto-increment; não é necessário passar o sa_column se usar o Field padrão
    codigo_vaga: Optional[int] = Field(default=None, primary_key=True, index=True)
    data_requisicao: Optional[str] = None
    limite_esperado_para_contratacao: Optional[str] = None
    titulo_vaga: Optional[str] = None
    vaga_sap: Optional[str] = None
    cliente: Optional[str] = None
    solicitante_cliente: Optional[str] = None
    empresa_divisao: Optional[str] = None
    requisitante: Optional[str] = None
    analista_responsavel: Optional[str] = None
    tipo_contratacao: Optional[str] = None
    prazo_contratacao: Optional[str] = None
    objetivo_vaga: Optional[str] = Field(default=None, sa_column=Column(Text))
    prioridade_vaga: Optional[str] = Field(default=None, sa_column=Column(Text))
    origem_vaga: Optional[str] = Field(default=None, sa_column=Column(Text))
    superior_imediato: Optional[str] = None
    nome: Optional[str] = None
    telefone: Optional[str] = None

    perfil_vaga: Optional["VagaPerfil"] = Relationship(back_populates="infos_basicas", sa_relationship_kwargs={"uselist": False})
    beneficios: Optional["VagaBeneficios"] = Relationship(back_populates="infos_basicas", sa_relationship_kwargs={"uselist": False})
    prospects: List["Prospect"] = Relationship(back_populates="vaga")  # Adicionado o relacionamento


class VagaPerfil(SQLModel, table=True):
    __tablename__ = "vaga_perfil"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_vaga: int = Field(foreign_key="vaga_infos_basicas.codigo_vaga")
    pais: Optional[str] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    regiao: Optional[str] = None
    local_trabalho: Optional[str] = None
    vaga_especifica_para_pcd: Optional[str] = None
    faixa_etaria: Optional[str] = None
    horario_trabalho: Optional[str] = None
    nivel_profissional: Optional[str] = None
    nivel_academico: Optional[str] = None
    nivel_ingles: Optional[str] = None
    nivel_espanhol: Optional[str] = None
    outro_idioma: Optional[str] = None
    areas_atuacao: Optional[str] = None
    principais_atividades: Optional[str] = Field(default=None, sa_column=Column(Text))
    competencia_tecnicas_e_comportamentais: Optional[str] = Field(default=None, sa_column=Column(Text))
    demais_observacoes: Optional[str] = Field(default=None, sa_column=Column(Text))
    viagens_requeridas: Optional[str] = None
    equipamentos_necessarios: Optional[str] = None

    infos_basicas: Optional[VagaInfosBasicas] = Relationship(back_populates="perfil_vaga")


class VagaBeneficios(SQLModel, table=True):
    __tablename__ = "vaga_beneficios"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_vaga: int = Field(foreign_key="vaga_infos_basicas.codigo_vaga")
    valor_venda: Optional[str] = None
    valor_compra_1: Optional[str] = None
    valor_compra_2: Optional[str] = None

    infos_basicas: Optional[VagaInfosBasicas] = Relationship(back_populates="beneficios")