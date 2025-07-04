from pydantic import BaseModel
from typing import Optional, List

class ProspectBase(BaseModel):
    id: Optional[int] = None
    nome: str
    codigo_candidato: int
    situacao_candidato: str
    data_candidatura: str
    ultima_atualizacao: str
    comentario: Optional[str] = None
    recrutador: str

    class Config:
        from_attributes = True

# Schema para representar a vaga com seus prospects (caso de listagem ou atualização em grupo)
class ProspectGroup(BaseModel):
    codigo_vaga: int
    titulo_vaga: str
    modalidade: Optional[str] = ""
    prospects: List[ProspectBase]

    class Config:
        from_attributes = True

# Schema para update de um prospect individual dentro de uma vaga
class ProspectUpdate(BaseModel):
    codigo_vaga: int
    codigo_candidato: int
    situacao_candidato: Optional[str] = None
    comentario: Optional[str] = None

# Schema para atualizar o grupo de prospects de uma vaga
class ProspectGroupUpdate(BaseModel):
    codigo_vaga: int
    prospects: List[ProspectUpdate]