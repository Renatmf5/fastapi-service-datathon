from sqlmodel import SQLModel, Field
from typing import Optional

class UsuarioModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    perfil: str = Field(nullable=False)