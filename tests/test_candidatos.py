import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE_URL = "/api/v1/candidatos"

# Testes para o endpoint de criação de candidato
def test_create_candidato_success():
    # Payload ajustado conforme esperado pela função salvar_candidato:
    # Deve conter a chave "infos_basicas". Outros campos são opcionais.
    payload = {
        "infos_basicas": {
            "nome": "Candidato Teste",
            "email": "candidato@teste.com"
            # Insira outros campos obrigatórios se houver
        },
        # "informacoes_pessoais": {...},  # opcional, se necessário
        # "informacoes_profissionais": {...},  # opcional
        # "formacao_e_idiomas": {...},  # opcional
        # "cv_pt": "Conteúdo do CV em português"  # opcional
    }
    response = client.post(f"{BASE_URL}/create", json=payload)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "codigo_candidato" in data

# Testes para o endpoint de listagem de candidatos
def test_list_candidatos():
    response = client.get(f"{BASE_URL}/list")
    assert response.status_code == 200
    data = response.json()
    # Verifica se a resposta contém os campos de listagem
    assert "data" in data
    assert "total" in data

# Testes para o endpoint de detalhes de candidato
def test_details_candidato_not_found():
    # Testa com um código que provavelmente não existe
    response = client.get(f"{BASE_URL}/details/nonexistent")
    assert response.status_code in (400, 404)

# Testes para o endpoint de atualização de tabelas sem enviar valor obrigatório
def test_update_tables_missing_file_key():
    payload = {}  # file_key não enviado
    response = client.post(f"{BASE_URL}/update-tables", json=payload)
    # Espera erro 400 devido à falta do campo obrigatório
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

# Testes para o endpoint de exportação de candidatos
def test_export_applicants():
    response = client.post(f"{BASE_URL}/export-applicants")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data