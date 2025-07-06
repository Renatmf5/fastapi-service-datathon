import json
import boto3
from collections import OrderedDict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from core.config import settings
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
    
@router.post("/export-applicants", summary="Exportar Candidatos para S3")
def export_applicants(db: Session = Depends(get_system_session)):
    """
    Consulta toda a base de candidatos, monta um JSON no formato necessário e faz o upload 
    do arquivo no bucket S3 na chave "raw/applicants.json". 
    O formato gerado:
    {
      "codigo": {
          "infos_basicas": { ... },
          "informacoes_pessoais": { ... },
          "informacoes_profissionais": { ... },
          "formacao_e_idiomas": { ... },
          "cargo_atual": {},
          "cv_pt": "",
          "cv_en": ""
      }
    }
    """
    try:
        # Aqui definimos um limite grande; ajuste conforme o volume esperado
        candidatos = listar_candidatos(db, offset=0, limit=10)
        export_data = OrderedDict()

        def clean_dict(data: dict) -> dict:
            # Remove os campos 'id' e 'codigo_profissional'
            return {k: v for k, v in data.items() if k not in ["id", "codigo_profissional"]}

        # Para cada candidato, montar o JSON com a estrutura exata desejada
        for cand in candidatos:
            codigo = str(cand.codigo_profissional)
            detalhes = listar_detalhes_candidato_por_codigo(codigo, db)
            if not detalhes:
                continue

            # Garantir que 'cargo_atual' exista
            detalhes["cargo_atual"] = detalhes.get("cargo_atual", {})

            # Montar a estrutura ordenada conforme o exemplo
            ordered_entry = OrderedDict()
            ordered_entry["infos_basicas"] = detalhes.get("infos_basicas", {})
            ordered_entry["informacoes_pessoais"] = clean_dict(detalhes.get("informacoes_pessoais", {}))
            ordered_entry["informacoes_profissionais"] = clean_dict(detalhes.get("informacoes_profissionais", {}))
            ordered_entry["formacao_e_idiomas"] = clean_dict(detalhes.get("formacao_e_idiomas", {}))
            ordered_entry["cargo_atual"] = detalhes.get("cargo_atual", {})

            # Extrair e achatar 'curriculos'
            curriculos = detalhes.get("curriculos", {})
            ordered_entry["cv_pt"] = curriculos.get("cv_pt", "")
            ordered_entry["cv_en"] = curriculos.get("cv_en", "")

            export_data[codigo] = ordered_entry

        json_payload = json.dumps(export_data, ensure_ascii=False, indent=2)
        # Realiza o upload do JSON para o bucket S3 na pasta "raw"
        s3_client = boto3.client("s3")
        key = "raw/applicants.json"
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=key,
            Body=json_payload.encode("utf-8")
        )
        return {"message": "Exportação realizada com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))