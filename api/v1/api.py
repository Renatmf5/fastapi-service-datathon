from fastapi import APIRouter

from api.v1.endpoints import usuarios, candidatos, vagas

api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(candidatos.router, prefix="/candidatos", tags=["candidatos"])
api_router.include_router(vagas.router, prefix="/vagas", tags=["vagas"])

@api_router.get("/", tags=["root"])
def read_root():
    return {"message": "API is running"}