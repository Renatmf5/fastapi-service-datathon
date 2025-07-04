from fastapi import APIRouter

from api.v1.endpoints import usuarios, candidatos, vagas, inferencias, prospects


api_router = APIRouter()

api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(candidatos.router, prefix="/candidatos", tags=["candidatos"])
api_router.include_router(vagas.router, prefix="/vagas", tags=["vagas"])
api_router.include_router(inferencias.router, prefix="/inferencias", tags=["inferencias"])
api_router.include_router(prospects.router, prefix="/prospects", tags=["prospects"])

@api_router.get("/", tags=["root"])
def read_root():
    return {"message": "API is running"}