from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from api.utils.functions.CRUD_SystemDB import salvar_candidato, listar_candidatos, listar_detalhes_candidato_por_codigo
from core.services.fetch_S3_files import read_applicants_json_from_s3

router = APIRouter()

@router.post("/create", summary="Criar Candidato")
def criar_candidato(data: dict, db: Session = Depends(get_system_session)):
    try:
        codigo = salvar_candidato(data, db)
        return {"message": "Candidato inserido com sucesso!", "codigo_candidato": codigo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao inserir candidato.")

# Endpoint para listar todos os candidatos
@router.get("/list", summary="Listar Candidatos")
def listar_todos_candidatos(offset: int = 0, limit: int = 100, db: Session = Depends(get_system_session)):
    try:
        candidatos = listar_candidatos(db, offset, limit)
        return {"total": len(candidatos), "offset": offset, "limit": limit, "data": [cand.model_dump() for cand in candidatos]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar candidatos.")

# Endpoint para listar detalhes de um candidato específico
@router.get("/details/{codigo_profissional}", summary="Detalhes do Candidato")
def detalhes_candidato(codigo_profissional: str, db: Session = Depends(get_system_session)):
    try:
        candidato_detalhes = listar_detalhes_candidato_por_codigo(codigo_profissional, db)
        if not candidato_detalhes:
            raise HTTPException(status_code=404, detail="Candidato não encontrado.")
        return candidato_detalhes
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar detalhes do candidato.")
    
# Endpoint para atualizar tabelas de candidatos a partir de arquivos S3
@router.post("/update-tables", summary="Atualizar Tabelas de Candidatos")
def atualizar_tabelas(data: dict):
    try:
        # Extrair o nome do arquivo do corpo da requisição
        file_key = data.get("file_key")
        if not file_key:
            raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")

        # Chamar a função para ler o arquivo do S3 e atualizar as tabelas
        response = read_applicants_json_from_s3(file_key)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))