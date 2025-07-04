from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.vagas_model import VagaInfosBasicas
from models.candidato_model import CandidatoInfosBasicas

class Prospect(SQLModel, table=True):
    __tablename__ = "prospects"
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_vaga: int = Field(foreign_key="vaga_infos_basicas.codigo_vaga", index=True)
    titulo_vaga: str
    nome: str
    codigo_candidato: int = Field(foreign_key="candidato_infos_basicas.codigo_profissional")
    situacao_candidato: str
    data_candidatura: str
    ultima_atualizacao: str
    comentario: Optional[str] = None
    recrutador: str

    vaga: Optional[VagaInfosBasicas] = Relationship(back_populates="prospects")
    candidato: Optional[CandidatoInfosBasicas] = Relationship()

# Adicione o relacionamento na tabela VagaInfosBasicas
VagaInfosBasicas.prospects = Relationship(back_populates="vaga")