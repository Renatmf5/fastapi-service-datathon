from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from core.auth import get_current_user, get_password_hash, autenticar_usuario, create_access_token, get_user
from core.database import get_auth_session
from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioBase, UsuarioCreate, UsuarioUpdate


router = APIRouter()

# GET logado
@router.get("/logado", response_model=UsuarioBase)
def get_usuario_logado(current_user: UsuarioModel = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

# POST login
@router.post("/login", response_model=str)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_auth_session)):
    usuario = autenticar_usuario(form_data.username, form_data.password, db)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": usuario.username})
    return access_token

# POST criar usuário
@router.post("/signup", response_model=UsuarioBase, status_code=status.HTTP_201_CREATED)
def create_usuario(usuario: UsuarioCreate, db: Session = Depends(get_auth_session)):
    db_usuario = UsuarioModel(
        username=usuario.username,
        password=get_password_hash(usuario.password),
        perfil=usuario.perfil
    )
    try:
        db.add(db_usuario)
        db.commit()
        db.refresh(db_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário já existe"
        )
    return db_usuario


# GET listar usuários
@router.get("/list", response_model=list[UsuarioBase])
def list_usuarios(db: Session = Depends(get_auth_session)):
    statement = select(UsuarioModel)
    usuarios = db.exec(statement).all()
    return usuarios

# PUT atualizar usuário
@router.put("/{usuario_id}", response_model=UsuarioBase, status_code=status.HTTP_202_ACCEPTED)
def update_usuario(usuario_id: int, usuario: UsuarioUpdate, db: Session = Depends(get_auth_session)):
    db_usuario = db.get(UsuarioModel, usuario_id)
    if not db_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    update_data = usuario.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        print("key", key)
        print("value", value)
        setattr(db_usuario, key, value)
        if key == "password":
            setattr(db_usuario, key, get_password_hash(value))
            print("entrei aqui no password", value, get_password_hash(value))
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    
    return db_usuario