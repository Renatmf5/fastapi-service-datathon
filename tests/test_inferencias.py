import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE_URL = "/api/v1/inferencias"


# Teste para o endpoint de predição do modelo de match (/matchModel/predict)
def test_match_model_predict_success():
    payload = {
        "sexo": "Feminino",
        "estado_civil": "Solteira",
        "pcd": "Não",
        "vaga_especifica_para_pcd": "Não",
        "pais_vaga": "Brasil",
        "nivel_academico": "Superior Completo",
        "tipo_contratacao": "CLT",
        "cidade": "São Paulo",
        "cidade_vaga": "São Paulo",
        "nivel_profissional": "Pleno",
        "nivel_profissional_vaga": "Pleno",
        "ingles": "Avançado",
        "espanhol": "Básico",
        "outros_idiomas": "Nenhum",
        "nivel_ingles_vaga": "Avançado",
        "nivel_espanhol_vaga": "Intermediário",
        "titulo_profissional": "Analista de Dados",
        "titulo_vaga": "Analista de Dados",
        "conhecimentos_tecnicos": "Python, SQL",
        "certificacoes": "Certificação X",
        "outras_certificacoes": "Nenhuma",
        "area_atuacao": "Tecnologia",
        "areas_atuacao_vaga": "Tecnologia",
        "competencia_tecnicas_e_comportamentais": "Boa comunicação, trabalho em equipe",
        "cv_candidato": "Link para CV ou descrição resumida"
    }
    response = client.post(f"{BASE_URL}/matchModel/predict", json=payload)
    # Se o modelo estiver disponível, espera status 200
    assert response.status_code == 200, response.text
    data = response.json()
    # Verifica se a chave match_probability está presente e é um número
    assert "match_probability" in data
    assert isinstance(data["match_probability"], (int, float))


# Teste para o endpoint de predição do modelo de recomendação (/recommendationModel/predict)
def test_recommendation_model_predict_success():
    payload = {
        "titulo_profissional": "Analista de Dados",
        "conhecimentos_tecnicos": "Python, SQL",
        "certificacoes": "Certificação X",
        "outras_certificacoes": "Nenhuma",
        "cidade": "São Paulo",
        "ingles": "Avançado",
        "espanhol": "Básico",
        "outros_idiomas": "Nenhum",
        "pcd": "Não",
        "cv_candidato": "Link para CV ou descrição resumida"
    }
    response = client.post(f"{BASE_URL}/recommendationModel/predict", json=payload)
    # Se os modelos estiverem disponíveis, espera status 200
    assert response.status_code == 200, response.text
    data = response.json()
    # Verifica se a chave data está presente e contém uma lista de recomendações
    assert "data" in data
    assert isinstance(data["data"], list)


# Teste para o endpoint de drift report (/driftReport)
def test_drift_report():
    response = client.get(f"{BASE_URL}/driftReport")
    # O endpoint pode retornar 200 se o drift report existir ou 404 caso contrário
    assert response.status_code in (200, 404), response.text
    data = response.json()
    if response.status_code == 200:
        # Se encontrado, verifica se o conteúdo está presente
        assert "drift_report" in data
        assert isinstance(data["drift_report"], str)
    else:
        # Se não encontrado, a resposta deve conter a chave detail
        assert "detail" in data