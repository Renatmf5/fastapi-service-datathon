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
    listar_detalhes_vaga_por_codigo
)
from core.services.fetch_S3_files import read_vagas_json_from_s3 

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
def atualizar_tabelas_vagas_endpoint(data: dict, db: Session = Depends(get_system_session)):
    try:
        file_key = data.get("file_key")
        if not file_key:
            raise HTTPException(status_code=400, detail="O campo 'file_key' é obrigatório.")

        response = read_vagas_json_from_s3(file_key)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/export-vagas", summary="Exportar Vagas para S3")
def export_vagas(db: Session = Depends(get_system_session)):
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
    try:
        # Recupera todas as vagas (ajuste o limite conforme o volume)
        vagas = listar_vagas(db, offset=0, limit=10)
        export_data = OrderedDict()

        for vaga in vagas:
            codigo = str(vaga.codigo_vaga)
            detalhes = listar_detalhes_vaga_por_codigo(codigo, db)
            if not detalhes:
                continue

            # Definir os dicionários ordenados conforme o formato de saída
            # OBS: Renomeamos "data_requisicao" para "data_requicisao", conforme o exemplo
            informacoes_basicas = OrderedDict()
            ib = detalhes.get("infos_basicas", {})
            informacoes_basicas["data_requicisao"] = ib.get("data_requisicao") or ""
            informacoes_basicas["limite_esperado_para_contratacao"] = ib.get("limite_esperado_para_contratacao") or ""
            informacoes_basicas["titulo_vaga"] = ib.get("titulo_vaga") or ""
            informacoes_basicas["vaga_sap"] = ib.get("vaga_sap") or ""
            informacoes_basicas["cliente"] = ib.get("cliente") or ""
            informacoes_basicas["solicitante_cliente"] = ib.get("solicitante_cliente") or ""
            informacoes_basicas["empresa_divisao"] = ib.get("empresa_divisao") or ""
            informacoes_basicas["requisitante"] = ib.get("requisitante") or ""
            informacoes_basicas["analista_responsavel"] = ib.get("analista_responsavel") or ""
            informacoes_basicas["tipo_contratacao"] = ib.get("tipo_contratacao") or ""
            informacoes_basicas["prazo_contratacao"] = ib.get("prazo_contratacao") or ""
            informacoes_basicas["objetivo_vaga"] = ib.get("objetivo_vaga") or ""
            informacoes_basicas["prioridade_vaga"] = ib.get("prioridade_vaga") or ""
            informacoes_basicas["origem_vaga"] = ib.get("origem_vaga") or ""
            informacoes_basicas["superior_imediato"] = ib.get("superior_imediato") or ""
            informacoes_basicas["nome"] = ib.get("nome") or ""
            informacoes_basicas["telefone"] = ib.get("telefone") or ""

            # Perfil da vaga
            perfil_vaga = {}
            if detalhes.get("perfil"):
                pb = detalhes.get("perfil")
                perfil_vaga = {
                    "pais": pb.get("pais") or "",
                    "estado": pb.get("estado") or "",
                    "cidade": pb.get("cidade") or "",
                    "bairro": pb.get("bairro") or "",
                    "regiao": pb.get("regiao") or "",
                    "local_trabalho": pb.get("local_trabalho") or "",
                    "vaga_especifica_para_pcd": pb.get("vaga_especifica_para_pcd") or "",
                    "faixa_etaria": pb.get("faixa_etaria") or "",
                    "horario_trabalho": pb.get("horario_trabalho") or "",
                    "nivel profissional": pb.get("nivel_profissional") or "",
                    "nivel_academico": pb.get("nivel_academico") or "",
                    "nivel_ingles": pb.get("nivel_ingles") or "",
                    "nivel_espanhol": pb.get("nivel_espanhol") or "",
                    "outro_idioma": pb.get("outro_idioma") or "",
                    "areas_atuacao": pb.get("areas_atuacao") or "",
                    "principais_atividades": pb.get("principais_atividades") or "",
                    "competencia_tecnicas_e_comportamentais": pb.get("competencia_tecnicas_e_comportamentais") or "",
                    "demais_observacoes": pb.get("demais_observacoes") or "",
                    "viagens_requeridas": pb.get("viagens_requeridas") or "",
                    "equipamentos_necessarios": pb.get("equipamentos_necessarios") or ""
                }
            
            # Benefícios da vaga
            beneficios = {}
            if detalhes.get("beneficios"):
                bb = detalhes.get("beneficios")
                beneficios = {
                    "valor_venda": bb.get("valor_venda") or "",
                    "valor_compra_1": bb.get("valor_compra_1") or "",
                    "valor_compra_2": bb.get("valor_compra_2") or ""
                }

            export_data[codigo] = OrderedDict({
                "informacoes_basicas": informacoes_basicas,
                "perfil_vaga": perfil_vaga,
                "beneficios": beneficios
            })
        
        json_payload = json.dumps(export_data, ensure_ascii=False, indent=4)
        
        # Envia o JSON para o S3 utilizando o bucket configurado
        s3_client = boto3.client("s3")
        s3_key = "raw/vagas.json"
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=s3_key,
            Body=json_payload.encode("utf-8")
        )
        
        return {"message": "Exportação de vagas concluída com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na exportação de vagas: {str(e)}")