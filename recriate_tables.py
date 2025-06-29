from sqlmodel import SQLModel
from core.database import system_engine  # Certifique-se de importar seu engine
from models.candidato_model import CandidatoInfosBasicas, CandidatoInformacoesPessoais, CandidatoInformacoesProfissionais, CandidatoFormacaoEIdiomas, CandidatoCurriculos
from models.vagas_model import VagaInfosBasicas, VagaPerfil, VagaBeneficios

def recreate_tables():
    # Apagar todas as tabelas (Atenção: isso removerá todos os dados)
    SQLModel.metadata.drop_all(system_engine)
    # Criar as tabelas a partir dos modelos atuais
    SQLModel.metadata.create_all(system_engine)
    print("Tabelas recriadas com sucesso.")

if __name__ == "__main__":
    recreate_tables()