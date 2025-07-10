import json
import boto3
from collections import OrderedDict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from core.config import settings
from api.utils.functions.CRUD_SystemDB import salvar_candidato, listar_candidatos, listar_detalhes_candidato_por_codigo, listar_candidatos_eager
from core.services.fetch_S3_files import read_applicants_json_from_s3
from fastapi import BackgroundTasks

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
def atualizar_tabelas(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
    try:
        # Extrair o nome do arquivo do corpo da requisição
        file_key = data.get("file_key")
        if not file_key:
            raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")

        # Adiciona a tarefa em background para ler o JSON e atualizar o BD
        background_tasks.add_task(read_applicants_json_from_s3, file_key)

        return {"message": "Tarefa de atualização iniciada em background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def clean_dict(data):
    """
    Limpa recursivamente o dicionário removendo as chaves "id" e "codigo_profissional".
    Se o valor for um dicionário ou uma lista de dicionários, a função é aplicada recursivamente.
    """
    if isinstance(data, dict):
        return {
            key: clean_dict(value)
            for key, value in data.items()
            if key not in ["id", "codigo_profissional"]
        }
    elif isinstance(data, list):
        return [clean_dict(item) for item in data]
    else:
        return data
    
def do_export_applicants(db: Session):
    try:
        chunk_size = 1000  # ajusta conforme necessário
        offset = 0
        export_data = OrderedDict()

        while True:
            candidatos = listar_candidatos_eager(db, offset=offset, limit=chunk_size)
            if not candidatos:
                break

            for cand in candidatos:
                codigo = str(cand.codigo_profissional)
                ordered_entry = OrderedDict()

                # Dados básicos: todos os atributos do candidato, exceto os relacionamentos
                ordered_entry["infos_basicas"] = cand.model_dump(
                    exclude={
                        "informacoes_pessoais", 
                        "informacoes_profissionais", 
                        "formacao_e_idiomas", 
                        "curriculos", 
                        "cargo_atual", 
                        "prospects"
                    }
                )
                
                # Informações pessoais – se não existir, retorna dicionário vazio
                if hasattr(cand, "informacoes_pessoais") and cand.informacoes_pessoais is not None:
                    dados = cand.informacoes_pessoais.model_dump()
                    ordered_entry["informacoes_pessoais"] = clean_dict(dados)
                else:
                    ordered_entry["informacoes_pessoais"] = {}

                # Informações profissionais
                if hasattr(cand, "informacoes_profissionais") and cand.informacoes_profissionais is not None:
                    dados = cand.informacoes_profissionais.model_dump()
                    ordered_entry["informacoes_profissionais"] = clean_dict(dados)
                else:
                    ordered_entry["informacoes_profissionais"] = {}

                # Formação e idiomas
                if hasattr(cand, "formacao_e_idiomas") and cand.formacao_e_idiomas is not None:
                    dados = cand.formacao_e_idiomas.model_dump()
                    ordered_entry["formacao_e_idiomas"] = clean_dict(dados)
                else:
                    ordered_entry["formacao_e_idiomas"] = {}

                # Cargo atual: se não existir, retorna sempre dicionário vazio
                if hasattr(cand, "cargo_atual") and cand.cargo_atual is not None:
                    ordered_entry["cargo_atual"] = cand.cargo_atual.model_dump()
                else:
                    ordered_entry["cargo_atual"] = {}

                # Currículos – extraindo cv_pt e cv_en
                if hasattr(cand, "curriculos") and cand.curriculos is not None:
                    curriculos = cand.curriculos.model_dump() if hasattr(cand.curriculos, "model_dump") else cand.curriculos
                    ordered_entry["cv_pt"] = curriculos.get("cv_pt", "")
                    ordered_entry["cv_en"] = curriculos.get("cv_en", "")
                else:
                    ordered_entry["cv_pt"] = ""
                    ordered_entry["cv_en"] = ""

                export_data[codigo] = ordered_entry

            offset += chunk_size

        json_payload = json.dumps(export_data, ensure_ascii=False, indent=4)
        s3_client = boto3.client("s3")
        key = "raw/applicants.json"
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=key,
            Body=json_payload.encode("utf-8")
        )
    except Exception as e:
        print(f"Erro na exportação de candidatos: {str(e)}")

@router.post("/export-applicants", summary="Exportar Candidatos para S3 (Background)")
def export_applicants(background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
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
    background_tasks.add_task(do_export_applicants, db)
    return {"message": "Tarefa de exportação de candidatos iniciada em background."}