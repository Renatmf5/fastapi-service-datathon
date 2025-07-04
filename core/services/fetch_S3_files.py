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
from api.utils.functions.CRUD_SystemDB import atualizar_tabelas_candidatos, atualizar_tabelas_vagas, atualizar_tabelas_prospects
import pickle


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

def get_s3_file_last_modified(key: str) -> datetime:
    """Obtém a data de última modificação do arquivo no S3."""
    response = s3_client.head_object(Bucket=bucket_name, Key= key)
    return response['LastModified']

def get_latest_model_key(model: str) -> str:
    """
    Busca a chave do último modelo de matching conforme informado no arquivo latest.txt
    contido no bucket dentro do diretório models/Modelo_Matching_Classificacao/.
    
    Exemplo: se o conteúdo de latest.txt for "v10/model_matching.pkl", a função retorna:
           "models/Modelo_Matching_Classificacao/v10/model_matching.pkl"
    """
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=f"{model}latest.txt")
        latest_content = response["Body"].read().decode("utf-8").strip()
        return f"models/Modelo_Matching_Classificacao/{latest_content}"
    except Exception as e:
        raise Exception(f"Erro ao obter a chave do modelo: {str(e)}")


def read_applicants_json_from_s3(file_key: str) -> DataResponse:
    try:
        # Caminho do arquivo em cache
        local_file_path = os.path.join(cache_dir, f"{file_key}.json")
        cache_metadata_path = os.path.join(cache_dir, f"{file_key}_metadata.txt")

        # Verificar se o arquivo está em cache e se está atualizado
        if os.path.exists(local_file_path) and os.path.exists(cache_metadata_path):
            with open(cache_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            
            s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
            
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
        s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
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
            
            s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
            
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
        s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
        with open(cache_metadata_path, "w") as meta_file:
            meta_file.write(s3_last_modified.isoformat())

        # Atualizar as tabelas de vagas no banco de dados criando uma nova sessão
        with Session(system_engine) as db:
            atualizar_tabelas_vagas(local_file_path, db)

        return {"message": "Arquivo atualizado e base de dados sincronizada com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def read_prospects_json_from_s3(file_key: str) -> DataResponse:
    try:
        # Caminho do arquivo em cache
        local_file_path = os.path.join(cache_dir, f"{file_key}.json")
        cache_metadata_path = os.path.join(cache_dir, f"{file_key}_metadata.txt")

        # Verificar se o arquivo está em cache e se está atualizado
        if os.path.exists(local_file_path) and os.path.exists(cache_metadata_path):
            with open(cache_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            
            s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
            
            # Se o arquivo em cache estiver atualizado, não há necessidade de atualizar o banco
            if cached_last_modified >= s3_last_modified:
                with Session(system_engine) as db:
                    atualizar_tabelas_prospects(local_file_path, db)
                return {"message": "Arquivo em cache está atualizado. recarregando banco."}

        # Caso contrário, baixe o arquivo do S3 e atualize o cache
        s3_path = f"s3://{bucket_name}/raw/{file_key}.json"
        df = pd.read_json(s3_path)

        # Salvar o arquivo localmente
        df.to_json(local_file_path, orient="records")
        
        # Atualizar metadados do cache
        s3_last_modified = get_s3_file_last_modified(key=f"raw/{file_key}.json")
        with open(cache_metadata_path, "w") as meta_file:
            meta_file.write(s3_last_modified.isoformat())

        # Atualizar as tabelas de prospects no banco de dados criando uma nova sessão
        with Session(system_engine) as db:
            atualizar_tabelas_prospects(local_file_path, db)

        return {"message": "Arquivo atualizado e base de dados sincronizada com sucesso."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
def busca_modelo_pkl_classificacao():
    try:
        # Caminho do arquivo em cache e metadados atualizados
        local_file_path = os.path.join(cache_dir, "model_matching.pkl")
        cached_metadata_path = os.path.join(cache_dir, "model_matching_metadata.txt")
        model_key_prefix = "models/Modelo_Matching_Classificacao/"
        latest_model = get_latest_model_key(model=model_key_prefix)  # Ex: "models/Modelo_Matching_Classificacao/v10/model_matching.pkl"
        
        # Verificar se o arquivo em cache está atualizado
        if os.path.exists(local_file_path) and os.path.exists(cached_metadata_path):
            with open(cached_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            s3_last_modified = get_s3_file_last_modified(key=latest_model)
            
            # Se estiver atualizado, carrega o modelo do cache.
            if cached_last_modified >= s3_last_modified:
                with open(local_file_path, "rb") as file:
                    model_data = pickle.load(file)
                return model_data
        
        # Caso contrário, baixa o arquivo do S3 usando a chave correta
        s3_client.download_file(Bucket=bucket_name, Key=latest_model, Filename=local_file_path)
        
        # Atualizar o metadado do arquivo baixado
        s3_last_modified = get_s3_file_last_modified(key=latest_model)
        with open(cached_metadata_path, "w") as meta_file:
            meta_file.write(s3_last_modified.isoformat())
        
        # Carregar o modelo a partir do arquivo local
        with open(local_file_path, "rb") as file:
            model_data = pickle.load(file)
        
        return model_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def busca_modelo_recomendacao():
    """
    Baixa e retorna os caminhos locais dos arquivos necessários para o modelo de recomendação.
    São 3 arquivos:
      - annoy_index.ann
      - candidate_embeddings.npy
      - job_embeddings.npy
    
    O arquivo latest.txt, contido em models/Modelo_Recomendacao_Vagas/, possui 3 linhas,
    onde cada linha é o caminho relativo (como "v10/annoy_index.ann") para cada arquivo.
    A função baixa (ou utiliza o cache, se atualizado) cada arquivo e retorna um dicionário
    com as chaves:
      - "annoy_index_path"
      - "candidate_embeddings_path"
      - "job_embeddings_path"
    """
    try:
        model_key_prefix = "models/Modelo_Recomendacao_Vagas/"
        latest_txt_key = f"{model_key_prefix}latest.txt"
        
        # Baixar o arquivo latest.txt
        response = s3_client.get_object(Bucket=bucket_name, Key=latest_txt_key)
        latest_content = response["Body"].read().decode("utf-8").strip()
        lines = latest_content.splitlines()
        if len(lines) < 3:
            raise Exception("latest.txt deve conter 3 linhas para os 3 arquivos.")
        
        # Monta as keys completas para cada arquivo
        annoy_relative = lines[0].strip()
        candidate_embeddings_relative = lines[1].strip()
        job_embeddings_relative = lines[2].strip()
        
        annoy_key = f"{model_key_prefix}{annoy_relative}"
        candidate_embeddings_key = f"{model_key_prefix}{candidate_embeddings_relative}"
        job_embeddings_key = f"{model_key_prefix}{job_embeddings_relative}"
        
        # Define os caminhos locais e os caminhos dos metadados
        local_annoy = os.path.join(cache_dir, "annoy_index.ann")
        local_candidate = os.path.join(cache_dir, "candidate_embeddings.npy")
        local_job = os.path.join(cache_dir, "job_embeddings.npy")
        
        cache_annoy_metadata = os.path.join(cache_dir, "annoy_index_metadata.txt")
        cache_candidate_metadata = os.path.join(cache_dir, "candidate_embeddings_metadata.txt")
        cache_job_metadata = os.path.join(cache_dir, "job_embeddings_metadata.txt")
        
        # Função auxiliar para verificar e baixar o arquivo se necessário
        def update_file(file_key: str, local_path: str, metadata_path: str):
            download_required = True
            if os.path.exists(local_path) and os.path.exists(metadata_path):
                with open(metadata_path, "r") as meta_file:
                    cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
                s3_last_modified = get_s3_file_last_modified(file_key)
                if cached_last_modified >= s3_last_modified:
                    download_required = False
            if download_required:
                s3_client.download_file(Bucket=bucket_name, Key=file_key, Filename=local_path)
                s3_last_modified = get_s3_file_last_modified(file_key)
                with open(metadata_path, "w") as meta_file:
                    meta_file.write(s3_last_modified.isoformat())
        
        # Atualiza (ou mantém) os três arquivos
        update_file(annoy_key, local_annoy, cache_annoy_metadata)
        update_file(candidate_embeddings_key, local_candidate, cache_candidate_metadata)
        update_file(job_embeddings_key, local_job, cache_job_metadata)
        
        return {
            "annoy_index_path": local_annoy,
            "candidate_embeddings_path": local_candidate,
            "job_embeddings_path": local_job
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def busca_recommendation_pairs() -> str:
    """
    Baixa (ou usa a versão em cache) do arquivo recommendation_pairs.parquet,
    localizado em "models/Modelo_Recomendacao_Vagas/data/recommendation_pairs.parquet", 
    aplicando o controle de last_modified.
    
    Retorna o caminho local do arquivo.
    """
    try:
        # Definir a key do arquivo no S3
        file_key = "processed/recommendation_pairs.parquet"
        
        # Definir o caminho local para o arquivo e para os metadados
        local_file_path = os.path.join(cache_dir, "recommendation_pairs.parquet")
        cache_metadata_path = os.path.join(cache_dir, "recommendation_pairs_metadata.txt")
        
        download_required = True
        if os.path.exists(local_file_path) and os.path.exists(cache_metadata_path):
            with open(cache_metadata_path, "r") as meta_file:
                cached_last_modified = datetime.fromisoformat(meta_file.read().strip())
            s3_last_modified = get_s3_file_last_modified(key=file_key)
            if cached_last_modified >= s3_last_modified:
                download_required = False
        
        if download_required:
            s3_client.download_file(Bucket=bucket_name, Key=file_key, Filename=local_file_path)
            s3_last_modified = get_s3_file_last_modified(key=file_key)
            with open(cache_metadata_path, "w") as meta_file:
                meta_file.write(s3_last_modified.isoformat())
                
        return local_file_path
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))