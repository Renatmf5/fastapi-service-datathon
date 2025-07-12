import pandas as pd
import os
from sentence_transformers import SentenceTransformer
from annoy import AnnoyIndex
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.services.fetch_S3_files import busca_modelo_pkl_classificacao, busca_modelo_recomendacao, busca_recommendation_pairs, busca_drift_report

router = APIRouter()

class InputDataMatchModel(BaseModel):
    sexo: str
    estado_civil: str
    pcd: str
    vaga_especifica_para_pcd: str
    pais_vaga: str
    nivel_academico: str
    tipo_contratacao: str
    cidade: str
    cidade_vaga: str
    nivel_profissional: str
    nivel_profissional_vaga: str
    ingles: str
    espanhol: str
    outros_idiomas: str
    nivel_ingles_vaga: str
    nivel_espanhol_vaga: str
    titulo_profissional: str
    titulo_vaga: str
    conhecimentos_tecnicos: str
    certificacoes: str
    outras_certificacoes: str
    area_atuacao: str
    areas_atuacao_vaga: str
    competencia_tecnicas_e_comportamentais: str
    cv_candidato: str

class InputDataRecomendacaoModel(BaseModel):
    titulo_profissional: str
    conhecimentos_tecnicos: str
    certificacoes: str
    outras_certificacoes: str
    cidade: str
    ingles: str
    espanhol: str
    outros_idiomas: str
    pcd: str
    cv_candidato: str
    
@router.post("/matchModel/predict")
async def inferir(payload: InputDataMatchModel):
    try:
        # Carrega o modelo (usa a função que busca o arquivo .pkl no S3 ou cache)
        model = busca_modelo_pkl_classificacao()
        
        # Converte o payload para um DataFrame do pandas para manter as colunas nomeadas
        input_data = pd.DataFrame([payload.model_dump()])
        
        # Realiza a predição de probabilidade
        prediction = model.predict_proba(input_data)
        
        # Acessa somente a segunda posição
        match_probability = round(float(prediction[0][1]),3) * 100
        
        return {"match_probability": match_probability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/recommendationModel/predict")
async def inferir_recomendacao(payload: InputDataRecomendacaoModel):
    try:
        # Carrega o modelo (usa a função que busca o arquivo .pkl no S3 ou cache)
        recommendation_files = busca_modelo_recomendacao()
        annoy_index_path = recommendation_files["annoy_index_path"]
        recommendation_pairs_path = busca_recommendation_pairs()
        input_data = pd.DataFrame([payload.model_dump()])
        candidate_text = " ".join([
            payload.titulo_profissional,
            payload.conhecimentos_tecnicos,
            payload.certificacoes,
            payload.outras_certificacoes,
            payload.cidade,
            payload.ingles,
            payload.espanhol,
            payload.outros_idiomas,
            payload.pcd,
            payload.cv_candidato
        ])
        
        # Carrega modelos
        transformer_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")        
        candidate_embedding = transformer_model.encode([candidate_text])[0]
        dim = len(candidate_embedding)
        
        # Carrega o índice Annoy (que foi criado com base nos embeddings de vagas)
        annoy_index = AnnoyIndex(384, "angular")
        annoy_index.load(annoy_index_path)
        
        # Busca os 5 índices mais próximos
        indices = annoy_index.get_nns_by_vector(candidate_embedding, 5, include_distances=False)
        
        # Carrega os pares de recomendação (arquivo parquet) 
        df = pd.read_parquet(recommendation_pairs_path)
        # É esperado que o dataframe contenha as colunas utilizadas para criar os embeddings de vaga: 
        # "titulo_vaga", "competencia_tecnicas_e_comportamentais" e "area_atuacao_vaga"
        recommendations = df.iloc[indices][["codigo_vaga","titulo_vaga", "competencia_tecnicas_e_comportamentais", "areas_atuacao_vaga"]]
        # dropar duplicados
        recommendations = recommendations.drop_duplicates(subset=["codigo_vaga"])
        
        

        return {"data": recommendations.to_dict(orient="records")}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/driftReport")
async def inferir_drift_report():
    try:
        # Busca o caminho do relatório de drift
        drift_report_path = busca_drift_report()
        
        if not drift_report_path or not os.path.exists(drift_report_path):
            raise HTTPException(status_code=404, detail="Drift report not found")
        
        with open(drift_report_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        return {"drift_report": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
