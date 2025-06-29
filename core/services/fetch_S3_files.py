import boto3
import pandas as pd
from fastapi import HTTPException
from typing import List
from core.config import settings
from pydantic import BaseModel
import os
from datetime import datetime
from sqlmodel import Session
from core.database import system_engine
from api.utils.functions.CRUD_SystemDB import atualizar_tabelas_candidatos, atualizar_tabelas_vagas


s3_client = boto3.client('s3')
bucket_name = settings.BUCKET_NAME  # Substitua pelo nome do seu bucket
cache_dir = "./cache"  # Diretório local para armazenar os arquivos em cache

class DataResponse(BaseModel):
    columns: List[str]
    data: List[List[str]]
    
class TablesResponse(BaseModel):
    tables: List[str]

# Função para criar o diretório de cache, se não existir
os.makedirs(cache_dir, exist_ok=True)

def get_s3_file_last_modified(file_key: str) -> datetime:
    """Obtém a data de última modificação do arquivo no S3."""
    response = s3_client.head_object(Bucket=bucket_name, Key=f"raw/{file_key}.json")
    return response['LastModified']

def read_applicants_json_from_s3(file_key: str) -> DataResponse:
    try:
        # Caminho do arquivo em cache
        local_file_path = os.path.join(cache_dir, f"{file_key}.json")
        cache_metadata_path = os.path.join(cache_dir, f"{file_key}_metadata.txt")

        # Verificar se o arquivo está em cache e se está atualizado
        if os.path.exists(local_file_path) and os.path.exists(cache_metadata_path):
            with open(cache_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            
            s3_last_modified = get_s3_file_last_modified(file_key)
            
            # Se o arquivo em cache estiver atualizado, não há necessidade de atualizar o banco
            if cached_last_modified >= s3_last_modified:
                with Session(system_engine) as db:
                    atualizar_tabelas_candidatos(local_file_path, db)
                return {"message": "Arquivo em cache está atualizado. recarregando banco."}

        # Caso contrário, baixe o arquivo do S3 e atualize o cache
        s3_path = f"s3://{bucket_name}/raw/{file_key}.json"
        df = pd.read_json(s3_path)

        # Salvar o arquivo localmente
        df.to_json(local_file_path, orient="records")
        
        # Atualizar metadados do cache
        s3_last_modified = get_s3_file_last_modified(file_key)
        with open(cache_metadata_path, "w") as meta_file:
            meta_file.write(s3_last_modified.isoformat())

        # Atualizar as tabelas de candidatos no banco de dados criando uma nova sessão
        with Session(system_engine) as db:
            atualizar_tabelas_candidatos(local_file_path, db)

        return {"message": "Arquivo atualizado e base de dados sincronizada com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def read_vagas_json_from_s3(file_key: str) -> DataResponse:
    try:
        # Caminho do arquivo em cache
        local_file_path = os.path.join(cache_dir, f"{file_key}.json")
        cache_metadata_path = os.path.join(cache_dir, f"{file_key}_metadata.txt")

        # Verificar se o arquivo está em cache e se está atualizado
        if os.path.exists(local_file_path) and os.path.exists(cache_metadata_path):
            with open(cache_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            
            s3_last_modified = get_s3_file_last_modified(file_key)
            
            # Se o arquivo em cache estiver atualizado, não há necessidade de atualizar o banco
            if cached_last_modified >= s3_last_modified:
                with Session(system_engine) as db:
                    atualizar_tabelas_vagas(local_file_path, db)
                return {"message": "Arquivo em cache está atualizado. recarregando banco."}

        # Caso contrário, baixe o arquivo do S3 e atualize o cache
        s3_path = f"s3://{bucket_name}/raw/{file_key}.json"
        df = pd.read_json(s3_path)

        # Salvar o arquivo localmente
        df.to_json(local_file_path, orient="records")
        
        # Atualizar metadados do cache
        s3_last_modified = get_s3_file_last_modified(file_key)
        with open(cache_metadata_path, "w") as meta_file:
            meta_file.write(s3_last_modified.isoformat())

        # Atualizar as tabelas de vagas no banco de dados criando uma nova sessão
        with Session(system_engine) as db:
            atualizar_tabelas_vagas(local_file_path, db)

        return {"message": "Arquivo atualizado e base de dados sincronizada com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))