from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from api.utils.functions.CRUD_SystemDB import (
    salvar_vaga,
    listar_vagas,
    listar_detalhes_vaga_por_codigo
)
from core.services.fetch_S3_files import read_vagas_json_from_s3 

router = APIRouter()

@router.post("/create", summary="Criar Vaga")
def criar_vaga(data: dict, db: Session = Depends(get_system_session)):
    try:
        codigo = salvar_vaga(data, db)
        return {"message": "Vaga criada com sucesso!", "codigo_vaga": codigo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar vaga.")

@router.get("/list", summary="Listar Vagas")
def listar_todas_vagas(offset: int = 0, limit: int = 100, db: Session = Depends(get_system_session)):
    try:
        vagas = listar_vagas(db, offset, limit)
        return {"total": len(vagas), "offset": offset, "limit": limit, "data": [vaga.model_dump() for vaga in vagas]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar vagas.")

@router.get("/details/{codigo_vaga}", summary="Detalhes da Vaga")
def detalhes_vaga(codigo_vaga: str, db: Session = Depends(get_system_session)):
    try:
        vaga_detalhes = listar_detalhes_vaga_por_codigo(codigo_vaga, db)
        if not vaga_detalhes:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")
        return {"data": vaga_detalhes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar detalhes da vaga.")

@router.post("/update-tables", summary="Atualizar Tabelas de Vagas")
def atualizar_tabelas_vagas_endpoint(data: dict, db: Session = Depends(get_system_session)):
    try:
        file_key = data.get("file_key")
        if not file_key:
            raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")

        response = read_vagas_json_from_s3(file_key)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))