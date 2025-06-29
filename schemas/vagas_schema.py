from pydantic import BaseModel
from typing import Optional

class VagaInfosBasicasBase(BaseModel):
    codigo_vaga: Optional[int] = None
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
    objetivo_vaga: Optional[str] = None
    prioridade_vaga: Optional[str] = None
    origem_vaga: Optional[str] = None
    superior_imediato: Optional[str] = None
    nome: Optional[str] = None
    telefone: Optional[str] = None

    class Config:
        from_attributes = True

class VagaPerfilBase(BaseModel):
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
    principais_atividades: Optional[str] = None
    competencia_tecnicas_e_comportamentais: Optional[str] = None
    demais_observacoes: Optional[str] = None
    viagens_requeridas: Optional[str] = None
    equipamentos_necessarios: Optional[str] = None

    class Config:
        from_attributes = True

class VagaBeneficiosBase(BaseModel):
    valor_venda: Optional[str] = None
    valor_compra_1: Optional[str] = None
    valor_compra_2: Optional[str] = None

    class Config:
        from_attributes = True

# Schemas para criação e atualização
class VagaCreate(BaseModel):
    infos_basicas: VagaInfosBasicasBase
    perfil_vaga: Optional[VagaPerfilBase] = None
    beneficios: Optional[VagaBeneficiosBase] = None

class VagaUpdate(BaseModel):
    infos_basicas: Optional[VagaInfosBasicasBase] = None
    perfil_vaga: Optional[VagaPerfilBase] = None
    beneficios: Optional[VagaBeneficiosBase] = None
