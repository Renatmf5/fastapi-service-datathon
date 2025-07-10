import json
import boto3
from collections import OrderedDict
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from core.database import get_system_session
from core.config import settings
from api.utils.functions.CRUD_SystemDB import (
    salvar_vaga,
    listar_vagas,
    listar_detalhes_vaga_por_codigo,
    listar_vagas_eager
)
from core.services.fetch_S3_files import read_vagas_json_from_s3
from fastapi import BackgroundTasks 

router = APIRouter()

@router.post("/create", summary="Criar Vaga")
def criar_vaga(data: dict, db: Session = Depends(get_system_session)):
    try:
        codigo = salvar_vaga(data, db)
        return {"message": "Vaga criada com sucesso!", "codigo_vaga": codigo}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao criar vaga.")

@router.get("/list", summary="Listar Vagas")
def listar_todas_vagas(offset: int = 0, limit: int = 100, db: Session = Depends(get_system_session)):
    try:
        vagas = listar_vagas(db, offset, limit)
        return {"total": len(vagas), "offset": offset, "limit": limit, "data": [vaga.model_dump() for vaga in vagas]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao listar vagas.")

@router.get("/details/{codigo_vaga}", summary="Detalhes da Vaga")
def detalhes_vaga(codigo_vaga: str, db: Session = Depends(get_system_session)):
    try:
        vaga_detalhes = listar_detalhes_vaga_por_codigo(codigo_vaga, db)
        if not vaga_detalhes:
            raise HTTPException(status_code=404, detail="Vaga não encontrada.")
        return {"data": vaga_detalhes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao buscar detalhes da vaga.")



@router.post("/update-tables", summary="Atualizar Tabelas de Vagas")
def atualizar_tabelas_vagas_endpoint(data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
    try:
        file_key = data.get("file_key")
        if not file_key:
            raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")
        
        # Adiciona a tarefa em background para ler o JSON e atualizar o BD
        background_tasks.add_task(read_vagas_json_from_s3, file_key)
        
        return {"message": "Tarefa de atualização iniciada em background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def do_export_vagas(db: Session):
    try:
        chunk_size = 1000  # ajuste conforme necessário
        offset = 0
        export_data = OrderedDict()
        s3_client = boto3.client("s3")
        
        while True:
            # Busca as vagas com eager loading
            vagas = listar_vagas_eager(db, offset=offset, limit=chunk_size)
            if not vagas:
                break

            for vaga in vagas:
                codigo = str(vaga.codigo_vaga)
                ordered_entry = OrderedDict()
                
                # Informações básicas – mantendo a ordem dos campos conforme o exemplo
                # Definindo a ordem desejada:
                ib = vaga.model_dump(exclude={"perfil_vaga", "beneficios"})
                infos_order = [
                    "data_requisicao",
                    "limite_esperado_para_contratacao",
                    "titulo_vaga",
                    "vaga_sap",
                    "cliente",
                    "solicitante_cliente",
                    "empresa_divisao",
                    "requisitante",
                    "analista_responsavel",
                    "tipo_contratacao",
                    "prazo_contratacao",
                    "objetivo_vaga",
                    "prioridade_vaga",
                    "origem_vaga",
                    "superior_imediato",
                    "nome",
                    "telefone"
                ]
                informacoes_basicas = OrderedDict()
                for key in infos_order:
                    informacoes_basicas[key] = ib.get(key) or ""
                ordered_entry["informacoes_basicas"] = informacoes_basicas
                
                # Perfil da vaga – mantendo ordem dos campos
                perfil = OrderedDict()
                perfil_keys = [
                    "pais", "estado", "cidade", "bairro", "regiao", "local_trabalho",
                    "vaga_especifica_para_pcd", "faixa_etaria", "horario_trabalho",
                    "nivel profissional", "nivel_academico", "nivel_ingles", "nivel_espanhol",
                    "outro_idioma", "areas_atuacao", "principais_atividades",
                    "competencia_tecnicas_e_comportamentais", "demais_observacoes",
                    "viagens_requeridas", "equipamentos_necessarios"
                ]
                if vaga.perfil_vaga:
                    pb = vaga.perfil_vaga.model_dump() if hasattr(vaga.perfil_vaga, "model_dump") else vaga.perfil_vaga
                    for key in perfil_keys:
                        perfil[key] = pb.get(key) or ""
                ordered_entry["perfil_vaga"] = perfil
                
                # Benefícios – mantendo ordem dos campos
                beneficios = OrderedDict()
                beneficios_keys = ["valor_venda", "valor_compra_1", "valor_compra_2"]
                if vaga.beneficios:
                    bb = vaga.beneficios.model_dump() if hasattr(vaga.beneficios, "model_dump") else vaga.beneficios
                    for key in beneficios_keys:
                        beneficios[key] = bb.get(key) or ""
                ordered_entry["beneficios"] = beneficios

                export_data[codigo] = ordered_entry

            offset += chunk_size
        
        json_payload = json.dumps(export_data, ensure_ascii=False, indent=4)
        s3_key = "raw/vagas.json"
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=s3_key,
            Body=json_payload.encode("utf-8")
        )
    except Exception as e:
        print(f"Erro na exportação de vagas: {str(e)}")

@router.post("/export-vagas", summary="Exportar Vagas para S3 (Background)")
def export_vagas(background_tasks: BackgroundTasks, db: Session = Depends(get_system_session)):
    """
    Consulta toda a base de vagas, monta um JSON no formato necessário e faz o upload
    do arquivo no bucket S3 na chave "raw/vagas.json".
    
    Exemplo de saída:
    {
        "5185": {
            "informacoes_basicas": { ... },
            "perfil_vaga": { ... },
            "beneficios": { ... }
        },
        "5184": { ... }
    }
    """
    background_tasks.add_task(do_export_vagas, db)
    return {"message": "Tarefa de exportação de vagas iniciada em background."}