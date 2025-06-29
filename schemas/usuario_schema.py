from pydantic import BaseModel
from typing import Optional

class UsuarioBase(BaseModel):
    id: Optional[int] = None
    username: str
    perfil: str
    
    class Config:
        from_attributes = True
    
class UsuarioCreate(UsuarioBase):
    password: str
        
class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    perfil: Optional[str] = None