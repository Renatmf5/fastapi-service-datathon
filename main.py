from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.api import api_router
from core.config import settings
from sqlmodel import SQLModel
from core.database import auth_engine, system_engine
from models.usuario_model import UsuarioModel  # Modelos do banco de autenticação
from models.candidato_model import CandidatoInfosBasicas, CandidatoInformacoesPessoais, CandidatoInformacoesProfissionais, CandidatoFormacaoEIdiomas ,CandidatoCurriculos 
from models.vagas_model import VagaInfosBasicas, VagaPerfil, VagaBeneficios  # Modelos do banco de sistema
from models.prospect_model import Prospect  # Modelo de prospects
#from models.vaga_model import VagaModel  # Outros modelos do banco de sistema
import os

def create_auth_db_and_tables():
    """Cria as tabelas no banco de autenticação."""
    SQLModel.metadata.create_all(auth_engine, tables=[UsuarioModel.__table__])
    

def create_system_db_and_tables():
    """Cria as tabelas no banco de sistema."""
    SQLModel.metadata.create_all(system_engine, tables=[
        CandidatoInfosBasicas.__table__,
        CandidatoInformacoesPessoais.__table__,
        CandidatoInformacoesProfissionais.__table__,
        CandidatoFormacaoEIdiomas.__table__,
        CandidatoCurriculos.__table__,
        Prospect.__table__,
        VagaInfosBasicas.__table__,
        VagaPerfil.__table__,
        VagaBeneficios.__table__,
    ])

def get_application() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        # Criação de tabelas separadas
        create_auth_db_and_tables()
        create_system_db_and_tables()

    @app.get("/")
    def read_root():
        return {"message": "API is running"}

    return app

app = get_application()

if __name__ == "__main__":
    import uvicorn
    env = settings.ENV
    print(f"Running in {env} mode")
    if env == "production":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=settings.LOG_LEVEL)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level=settings.LOG_LEVEL, reload=True)