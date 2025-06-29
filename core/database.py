from sqlmodel import create_engine, Session

from core.config import settings

auth_engine = create_engine(settings.DATABASE_URL, echo=True)

system_engine = create_engine(settings.SYSTEM_DATABASE_URL, echo=True)

# Sessão para o banco de autenticação
def get_auth_session():
    with Session(auth_engine) as session:
        yield session

# Sessão para o banco de sistema
def get_system_session():
    with Session(system_engine) as session:
        yield session