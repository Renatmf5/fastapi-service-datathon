import os
import json
import boto3
from collections import OrderedDict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from core.config import settings
from api.utils.functions.CRUD_SystemDB import listar_prospects, add_candidate_to_prospect, update_candidate_in_prospect, listar_prospects_group, listar_prospects_group_eager
from core.services.fetch_S3_files import read_prospects_json_from_s3
from pydantic import BaseModel
from fastapi import BackgroundTasks

router = APIRouter()

class ProspectAddPayload(BaseModel):
    codigo_vaga: int
    titulo_vaga: str
    nome: str
    codigo_candidato: int
    situacao_candidato: str
    data_candidatura: str
    comentario: str = ""
    recrutador: str

class ProspectUpdatePayload(BaseModel):
    codigo_vaga: int
    codigo_candidato: int
    situacao_candidato: str
    comentario: str


@router.post("/add-candidate", summary="Adicionar candidato à vaga (prospect)")
async def add_candidate(payload: ProspectAddPayload, db: Session = Depends(get_system_session)):
    try:
        prospect = add_candidate_to_prospect(payload.model_dump(), db)
        return {"message": "Prospect criado com sucesso.", "data": prospect.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/update-candidate", summary="Atualizar informações do candidato no prospect")
async def update_candidate(payload: ProspectUpdatePayload, db: Session = Depends(get_system_session)):
    try:
        prospect = update_candidate_in_prospect(payload.model_dump(), db)
        return {"message": "Prospect atualizado com sucesso.", "data": prospect.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
# Endpoint para listar todos os prospects
@router.get("/list", summary="Listar Prospects")
async def listar_todos_prospects(offset: int = 0, limit: int = 100, db: Session = Depends(get_system_session)):
    try:
        prospects = listar_prospects(db, offset, limit)
        return {"total": len(prospects), "offset": offset, "limit": limit, "data": [prospect.model_dump() for prospect in prospects]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar prospects.")    
    
@router.get("/grouped-list", summary="Listar prospects agrupados por vaga")
async def listar_grouped(offset: int = 0, limit: int = 100, db: Session = Depends(get_system_session)):
    try:
        grupos = listar_prospects_group(db, offset, limit)
        # Converte cada prospect para dicionário usando model_dump
        grupos_convertidos = []
        for grupo in grupos:
            grupo["prospects"] = [p.model_dump() for p in grupo["prospects"]]
            grupos_convertidos.append(grupo)
        return {"total_grupos": len(grupos_convertidos), "offset": offset, "limit": limit, "data": grupos_convertidos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-tables", summary="Atualizar Tabelas de Prospects")
async def atualizar_tabelas(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
    try:
        # Ler o arquivo JSON do S3
        file_key = data.get("file_key")
        if not file_key:
                raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")
        # Adiciona a tarefa em background para ler o JSON e atualizar o BD
        background_tasks.add_task(read_prospects_json_from_s3, file_key)

        return {"message": "Tarefa de atualização iniciada em background."}
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))    

def do_export_prospects(db: Session):
    try:
        chunk_size = 1000  # ajuste conforme necessário
        offset = 0
        export_data = OrderedDict()
        s3_client = boto3.client("s3")
        
        # Processa os grupos de prospects em lotes usando a função eager
        while True:
            grupos = listar_prospects_group_eager(db, offset=offset, limit=chunk_size)
            if not grupos:
                break

            for grupo in grupos:
                codigo_vaga = str(grupo.get("codigo_vaga", ""))
                titulo = grupo.get("titulo_vaga") or ""
                modalidade = grupo.get("modalidade") or ""
                prospects_list = []

                for prospect in grupo.get("prospects", []):
                    prospect_dict = prospect.model_dump() if hasattr(prospect, "model_dump") else prospect
                    prospects_list.append({
                        "nome": prospect_dict.get("nome", ""),
                        "codigo": str(prospect_dict.get("codigo_candidato", "")),
                        "situacao_candidado": prospect_dict.get("situacao_candidato", ""),
                        "data_candidatura": prospect_dict.get("data_candidatura", ""),
                        "ultima_atualizacao": prospect_dict.get("ultima_atualizacao", ""),
                        "comentario": prospect_dict.get("comentario", ""),
                        "recrutador": prospect_dict.get("recrutador", "")
                    })
                    
                export_data[codigo_vaga] = OrderedDict({
                    "titulo": titulo,
                    "modalidade": modalidade,
                    "prospects": prospects_list
                })

            offset += chunk_size

        json_output = json.dumps(export_data, ensure_ascii=False, indent=2)
        s3_key = "raw/prospects.json"
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=s3_key,
            Body=json_output.encode("utf-8")
        )
    except Exception as e:
        print(f"Erro na exportação de prospects: {str(e)}")

@router.post("/export-prospects", summary="Exportar Prospects para S3 (Background)")
def export_prospects(background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
    background_tasks.add_task(do_export_prospects, db)
    return {"message": "Tarefa de exportação de prospects iniciada em background."}