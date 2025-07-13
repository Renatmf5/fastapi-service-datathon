import sys
import random
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE_URL = "/api/v1/prospects"

def test_add_candidate_success():
    """Teste para adicionar um prospect (candidato à vaga) com payload válido."""
    # Use um código aleatório para evitar conflitos em testes consecutivos
    unique_code = random.randint(10000, 99999)
    payload = {
        "codigo_vaga": 1,
        "titulo_vaga": "Vaga Teste",
        "nome": "Candidato Prospect",
        "codigo_candidato": unique_code,
        "situacao_candidato": "Novo",
        "data_candidatura": "2025-07-13",
        "comentario": "Nenhum",
        "recrutador": "Recrutador Teste"
    }
    response = client.post(f"{BASE_URL}/add-candidate", json=payload)
    assert response.status_code in (200, 201), response.text
    data = response.json()
    assert "message" in data
    assert "data" in data
    prospect = data["data"]
    assert prospect.get("codigo_candidato") == payload["codigo_candidato"]

def test_update_candidate_success():
    """Teste para atualizar um prospect existente."""
    # Primeiro, cria um prospect para atualização.
    add_payload = {
        "codigo_vaga": 1,
        "titulo_vaga": "Vaga Teste",
        "nome": "Candidato Prospect",
        "codigo_candidato": 10000,  # use outro código
        "situacao_candidato": "Novo",
        "data_candidatura": "2025-07-13",
        "comentario": "Nenhum",
        "recrutador": "Recrutador Teste"
    }
    add_response = client.post(f"{BASE_URL}/add-candidate", json=add_payload)
    assert add_response.status_code in (200, 201)
    
    update_payload = {
        "codigo_vaga": add_payload["codigo_vaga"],
        "codigo_candidato": add_payload["codigo_candidato"],
        "situacao_candidato": "Atualizado",
        "comentario": "Atualização efetuada"
    }
    update_response = client.put(f"{BASE_URL}/update-candidate", json=update_payload)
    assert update_response.status_code in (200, 201, 202)
    data = update_response.json()
    assert "message" in data
    assert "data" in data
    prospect = data["data"]
    assert prospect.get("situacao_candidato") == update_payload["situacao_candidato"]
    assert prospect.get("comentario") == update_payload["comentario"]

def test_list_prospects():
    """Teste para listar os prospects."""
    response = client.get(f"{BASE_URL}/list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data
    # Se houver dados, verifica se é uma lista (pode estar vazia no início)
    assert isinstance(data["data"], list)

def test_grouped_list_prospects():
    """Teste para listar prospects agrupados por vaga."""
    response = client.get(f"{BASE_URL}/grouped-list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total_grupos" in data
    # Verifica se os grupos possuem a chave "prospects"
    for grupo in data["data"]:
        assert "prospects" in grupo

def test_update_tables_missing_file_key():
    """Teste para verificação de campo obrigatório na atualização das tabelas de prospects."""
    payload = {}  # file_key não enviado
    response = client.post(f"{BASE_URL}/update-tables", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_export_prospects():
    """Teste para exportação dos prospects via tarefa em background."""
    response = client.post(f"{BASE_URL}/export-prospects")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data