import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE_URL = "/api/v1/vagas"

def test_create_vaga_success():
    # Payload mínimo esperado para criação de uma vaga.
    # Adapte os campos conforme seu modelo VagaInfosBasicas.
    payload = {
        "infos_basicas": {
            "titulo_vaga": "Vaga Teste",
            "data_requisicao": "2025-07-13",
            "limite_esperado_para_contratacao": "N/A",
            "vaga_sap": "N/A",
            "cliente": "Cliente Teste",
            "solicitante_cliente": "Solicitante",
            "empresa_divisao": "Divisão",
            "requisitante": "Requisitante",
            "analista_responsavel": "Analista",
            "tipo_contratacao": "CLT",
            "prazo_contratacao": "2025-08-01",
            "objetivo_vaga": "Objetivo teste",
            "prioridade_vaga": "Alta",
            "origem_vaga": "Online",
            "superior_imediato": "Chefe",
            "nome": "Nome contato",
            "telefone": "12345678"
        }
    }
    response = client.post(f"{BASE_URL}/create", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "codigo_vaga" in data

def test_list_vagas():
    response = client.get(f"{BASE_URL}/list")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "total" in data

def test_details_vaga_not_found():
    # Testa com um código que provavelmente não existe.
    response = client.get(f"{BASE_URL}/details/nonexistent")
    assert response.status_code in (400, 404)

def test_update_tables_missing_file_key():
    payload = {}  # file_key não enviado
    response = client.post(f"{BASE_URL}/update-tables", json=payload)
    # Espera erro 400 devido à falta do campo obrigatório.
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_export_vagas():
    response = client.post(f"{BASE_URL}/export-vagas")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data