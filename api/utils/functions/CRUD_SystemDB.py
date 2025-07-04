from sqlmodel import Session, select, delete
from models.candidato_model import CandidatoInfosBasicas, CandidatoInformacoesPessoais, CandidatoInformacoesProfissionais, CandidatoFormacaoEIdiomas, CandidatoCurriculos
from models.vagas_model import VagaInfosBasicas, VagaPerfil, VagaBeneficios
from models.prospect_model import Prospect
from sqlalchemy import func
from datetime import datetime

import json
import os


def salvar_candidato(data: dict, db: Session):
    """
    Insere um candidato no banco de dados individualmente.
    Se o candidato já existir (baseado no código_profissional), ele será atualizado.
    
    :param data: Dicionário contendo os dados do candidato.
    :param db: Sessão do banco de dados.
    """
    # Verificar se o candidato já existe no banco
    infos_basicas = CandidatoInfosBasicas(**data["infos_basicas"])
    db.add(infos_basicas)
    db.commit()
    db.refresh(infos_basicas)
    
    if "informacoes_pessoais" in data:
        informacoes_pessoais = CandidatoInformacoesPessoais(
            codigo_profissional=infos_basicas.codigo_profissional,
            **data["informacoes_pessoais"]
        )
        db.add(informacoes_pessoais)

    if "informacoes_profissionais" in data:
        informacoes_profissionais = CandidatoInformacoesProfissionais(
            codigo_profissional=infos_basicas.codigo_profissional,
            **data["informacoes_profissionais"]
        )
        db.add(informacoes_profissionais)

    if "formacao_e_idiomas" in data:
        formacao_e_idiomas = CandidatoFormacaoEIdiomas(
            codigo_profissional=infos_basicas.codigo_profissional,
            **data["formacao_e_idiomas"]
        )
        db.add(formacao_e_idiomas)

    if "cv_pt" in data:
        curriculos = CandidatoCurriculos(
            codigo_profissional=infos_basicas.codigo_profissional,
            cv_pt=data.get("cv_pt")
        )
        db.add(curriculos)
    
    db.commit()
    
    return infos_basicas.codigo_profissional
    
def atualizar_tabelas_candidatos(json_file_path: str, db: Session):
    """
    Atualiza as tabelas de candidatos no banco de dados com base em um arquivo JSON.
    Apaga todos os dados existentes e insere os novos dados.
    
    O JSON deve ser um dicionário onde cada chave é o código do candidato.
    Será feita a conversão da chave para inteiro para o campo codigo_profissional.
    
    :param json_file_path: Caminho para o arquivo JSON.
    :param db: Sessão do banco de dados.
    """
    # Apagar todos os dados existentes nas tabelas de candidatos
    db.exec(delete(CandidatoCurriculos))
    db.exec(delete(CandidatoFormacaoEIdiomas))
    db.exec(delete(CandidatoInformacoesProfissionais))
    db.exec(delete(CandidatoInformacoesPessoais))
    db.exec(delete(CandidatoInfosBasicas))
    db.commit()

    # Ler o arquivo JSON
    with open(json_file_path, "r", encoding="utf-8") as file:
        candidatos_data = json.load(file)

    # Inserir os novos dados nas tabelas
    for codigo_profissional_str, candidato in candidatos_data.items():
        # Converter a chave para inteiro
        codigo_profissional = int(codigo_profissional_str)

        # Inserir dados em CandidatoInfosBasicas (força inclusão do código, se necessário)
        candidato["infos_basicas"]["codigo_profissional"] = codigo_profissional
        infos_basicas = CandidatoInfosBasicas(**candidato["infos_basicas"])
        db.add(infos_basicas)
        db.commit()
        db.refresh(infos_basicas)  # agora infos_basicas.codigo_profissional contém o valor gerado pelo DB

        # Inserir dados em CandidatoInformacoesPessoais
        if "informacoes_pessoais" in candidato:
            informacoes_pessoais = CandidatoInformacoesPessoais(
                codigo_profissional=codigo_profissional,
                **candidato["informacoes_pessoais"]
            )
            db.add(informacoes_pessoais)

        # Inserir dados em CandidatoInformacoesProfissionais
        if "informacoes_profissionais" in candidato:
            informacoes_profissionais = CandidatoInformacoesProfissionais(
                codigo_profissional=codigo_profissional,
                **candidato["informacoes_profissionais"]
            )
            db.add(informacoes_profissionais)

        # Inserir dados em CandidatoFormacaoEIdiomas
        if "formacao_e_idiomas" in candidato:
            formacao_e_idiomas = CandidatoFormacaoEIdiomas(
                codigo_profissional=codigo_profissional,
                **candidato["formacao_e_idiomas"]
            )
            db.add(formacao_e_idiomas)

        # Inserir currículos, se existir
        if "cv_pt" in candidato:
            curriculos = CandidatoCurriculos(
                codigo_profissional=codigo_profissional,
                cv_pt=candidato.get("cv_pt")
            )
            db.add(curriculos)

    db.commit()

def listar_candidatos(db: Session, offset: int = 0, limit: int = 100):
    stmt = select(CandidatoInfosBasicas).offset(offset).limit(limit)
    candidatos = db.exec(stmt).all()
    return candidatos

def listar_detalhes_candidato_por_codigo(codigo_profissional: str, db: Session):
    """
    Lista os detalhes completos de um candidato específico pelo código profissional.
    
    :param codigo_profissional: Código profissional do candidato.
    :param db: Sessão do banco de dados.
    :return: Dicionário contendo todas as informações do candidato.
    """
    # Buscar informações básicas
    stmt_infos_basicas = select(CandidatoInfosBasicas).where(CandidatoInfosBasicas.codigo_profissional == codigo_profissional)
    infos_basicas = db.exec(stmt_infos_basicas).first()

    if not infos_basicas:
        raise ValueError(f"Candidato com código {codigo_profissional} não encontrado.")

    # Buscar informações pessoais
    stmt_informacoes_pessoais = select(CandidatoInformacoesPessoais).where(CandidatoInformacoesPessoais.codigo_profissional == codigo_profissional)
    informacoes_pessoais = db.exec(stmt_informacoes_pessoais).first()

    # Buscar informações profissionais
    stmt_informacoes_profissionais = select(CandidatoInformacoesProfissionais).where(CandidatoInformacoesProfissionais.codigo_profissional == codigo_profissional)
    informacoes_profissionais = db.exec(stmt_informacoes_profissionais).first()

    # Buscar formação e idiomas
    stmt_formacao_e_idiomas = select(CandidatoFormacaoEIdiomas).where(CandidatoFormacaoEIdiomas.codigo_profissional == codigo_profissional)
    formacao_e_idiomas = db.exec(stmt_formacao_e_idiomas).first()

    # Buscar currículos
    stmt_curriculos = select(CandidatoCurriculos).where(CandidatoCurriculos.codigo_profissional == codigo_profissional)
    curriculos = db.exec(stmt_curriculos).first()

    # Estruturar os dados no formato JSON
    candidato_detalhes = {
        "infos_basicas": infos_basicas.model_dump() if infos_basicas else None,
        "informacoes_pessoais": informacoes_pessoais.model_dump() if informacoes_pessoais else None,
        "informacoes_profissionais": informacoes_profissionais.model_dump() if informacoes_profissionais else None,
        "formacao_e_idiomas": formacao_e_idiomas.model_dump() if formacao_e_idiomas else None,
        "curriculos": curriculos.model_dump() if curriculos else None,
    }

    return candidato_detalhes


def salvar_vaga(data: dict, db: Session):
    """
    Insere uma vaga no banco de dados individualmente.
    Se a vaga já existir (baseado no código_vaga), ela será atualizada.
    
    :param data: Dicionário contendo os dados da vaga.
    :param db: Sessão do banco de dados.
    """
    infos_basicas = VagaInfosBasicas(**data["infos_basicas"])
    db.add(infos_basicas)
    db.commit()
    db.refresh(infos_basicas)  # agora infos_basicas.codigo_vaga contém o valor gerado pelo DB

    # Se houver dados de perfil, associe usando o codigo gerado
    if "perfil_vaga" in data:
        perfil = VagaPerfil(
            codigo_vaga=infos_basicas.codigo_vaga,
            **data["perfil_vaga"]
        )
        db.add(perfil)
    # Se houver dados de benefícios, associe usando o codigo gerado
    if "beneficios" in data:
        beneficios = VagaBeneficios(
            codigo_vaga=infos_basicas.codigo_vaga,
            **data["beneficios"]
        )
        db.add(beneficios)

    db.commit()
    return infos_basicas.codigo_vaga   

# Função para atualizar todas as vagas a partir de um JSON (remoção total e inserção dos novos dados)
def atualizar_tabelas_vagas(json_file_path: str, db: Session):
    """
    Atualiza as tabelas de vagas no banco de dados com base em um arquivo JSON.
    Apaga todos os dados existentes e insere os novos dados.
    
    O JSON deve ser uma lista com 3 dicionários:
      - O primeiro dicionário contém as informações de "informacoes_basicas";
      - O segundo dicionário contém os dados de "perfil_vaga";
      - O terceiro dicionário contém os dados de "beneficios".
    
    Cada dicionário utiliza o código da vaga (como chave) que deverá ser convertido para inteiro.
    
    :param json_file_path: Caminho para o arquivo JSON.
    :param db: Sessão do banco de dados.
    """
    # Remover os registros existentes
    db.exec(delete(VagaBeneficios))
    db.exec(delete(VagaPerfil))
    db.exec(delete(VagaInfosBasicas))
    db.commit()

    # Ler o arquivo JSON
    with open(json_file_path, "r", encoding="utf-8") as file:
        vagas_data = json.load(file)

    # Iterar sobre cada código presente nas informações básicas
    for codigo_vaga_str, vagas in vagas_data.items():
        # Converter o código da vaga para inteiro e incluir nos dados
        codigo_vaga = int(codigo_vaga_str)
        
        
        #Inserir dados em VagasInformaçõesBasicas
        vagas["informacoes_basicas"]["codigo_vaga"] = codigo_vaga
        infos_basicas = VagaInfosBasicas(**vagas["informacoes_basicas"])
        db.add(infos_basicas)
        db.commit()
        db.refresh(infos_basicas)
        
        # Inserir dados em VagaPerfil, se existir
        if "perfil_vaga" in vagas:
            perfil = VagaPerfil(
                codigo_vaga=infos_basicas.codigo_vaga,
                **vagas["perfil_vaga"]
            )
            db.add(perfil)
            
        # Inserir dados em VagaBeneficios, se existir
        if "beneficios" in vagas:
            beneficios = VagaBeneficios(
                codigo_vaga=infos_basicas.codigo_vaga,
                **vagas["beneficios"]
            )
            db.add(beneficios)
        
    db.commit()

# Função para listar vagas com paginação (ex.: 100 por página)
def listar_vagas(db: Session, offset: int = 0, limit: int = 100):
    stmt = select(VagaInfosBasicas).offset(offset).limit(limit)
    vagas = db.exec(stmt).all()
    return vagas

# Função para retornar os detalhes completos de uma vaga pelo código gerado
def listar_detalhes_vaga_por_codigo(codigo_vaga: str, db: Session):
    """
    Lista os detalhes completos de uma vaga a partir do seu código.
    
    :param codigo_vaga: Código da vaga.
    :param db: Sessão do banco de dados.
    :return: Dicionário com "infos_basicas", "perfil" e "beneficios".
    """
    stmt_infos = select(VagaInfosBasicas).where(VagaInfosBasicas.codigo_vaga == codigo_vaga)
    infos_basicas = db.exec(stmt_infos).first()
    if not infos_basicas:
        raise ValueError(f"Vaga com código {codigo_vaga} não encontrada.")
    
    stmt_perfil = select(VagaPerfil).where(VagaPerfil.codigo_vaga == codigo_vaga)
    perfil = db.exec(stmt_perfil).first()
    
    stmt_beneficios = select(VagaBeneficios).where(VagaBeneficios.codigo_vaga == codigo_vaga)
    beneficios = db.exec(stmt_beneficios).first()
    
    vaga_detalhes = {
        "infos_basicas": infos_basicas.model_dump() if infos_basicas else None,
        "perfil": perfil.model_dump() if perfil else None,
        "beneficios": beneficios.model_dump() if beneficios else None,
    }
    
    return vaga_detalhes

def atualizar_tabelas_prospects(json_file_path: str, db: Session):
    """
    Atualiza as tabelas de prospects no banco de dados com base em um arquivo JSON.
    Apaga todos os dados existentes e insere os novos dados.

    O JSON deve ser um dicionário onde cada chave é o código da vaga, e o valor contém
    as informações da vaga e uma lista de prospects associados.

    :param json_file_path: Caminho para o arquivo JSON.
    :param db: Sessão do banco de dados.
    """
    # Remover os registros existentes
    db.exec(delete(Prospect))
    db.commit()

    # Ler o arquivo JSON
    with open(json_file_path, "r", encoding="utf-8") as file:
        prospects_data = json.load(file)

    # Processar cada vaga e seus prospects
    for codigo_vaga_str, vaga_data in prospects_data.items():
        codigo_vaga = int(codigo_vaga_str)

        # Processar cada prospect associado à vaga
        for prospect_data in vaga_data.get("prospects", []):
            # Criar o objeto Prospect
            prospect = Prospect(
                codigo_vaga=codigo_vaga,
                titulo_vaga=vaga_data["titulo"],
                nome=prospect_data["nome"],
                codigo_candidato=int(prospect_data["codigo"]),
                situacao_candidato=prospect_data["situacao_candidado"],
                data_candidatura=prospect_data["data_candidatura"],
                ultima_atualizacao=prospect_data["ultima_atualizacao"],
                comentario=prospect_data.get("comentario", None),
                recrutador=prospect_data["recrutador"]
            )
            db.add(prospect)

    db.commit()
    
    
def listar_prospects(db: Session, offset: int = 0, limit: int = 100):
    """
    Lista todos os prospects com paginação.
    
    :param db: Sessão do banco de dados.
    :param offset: Posição inicial para a paginação.
    :param limit: Número máximo de registros a serem retornados.
    :return: Lista de prospects.
    """
    stmt = select(Prospect).offset(offset).limit(limit)
    prospects = db.exec(stmt).all()
    return prospects

def add_candidate_to_prospect(data: dict, db: Session):
    """
    Adiciona um candidato a um prospect. 
    Se não existir nenhum prospect para a vaga, cria um novo registro com os dados.
    Se já existir um prospect com a mesma combinação de codigo_vaga e codigo_candidato, lança exceção.
    Espera-se que o dicionário 'data' contenha:
      - codigo_vaga
      - titulo_vaga
      - nome
      - codigo_candidato
      - situacao_candidato
      - data_candidatura
      - comentario (opcional)
      - recrutador
    """
    # Converte código_candidato se for string
    codigo_candidato = int(data["codigo_candidato"])
    stmt = select(Prospect).where(
        Prospect.codigo_vaga == data["codigo_vaga"],
        Prospect.codigo_candidato == codigo_candidato
    )
    prospect_existente = db.exec(stmt).first()
    if prospect_existente:
        raise Exception("O candidato já está associado a esta vaga.")
    
    novo_prospect = Prospect(
        codigo_vaga = data["codigo_vaga"],
        titulo_vaga = data["titulo_vaga"],
        nome = data["nome"],
        codigo_candidato = codigo_candidato,
        situacao_candidato = data["situacao_candidato"],
        data_candidatura = data["data_candidatura"],
        ultima_atualizacao = datetime.now().strftime("%d-%m-%Y"),
        comentario = data.get("comentario", ""),
        recrutador = data["recrutador"]
    )
    db.add(novo_prospect)
    db.commit()
    db.refresh(novo_prospect)
    return novo_prospect

def update_candidate_in_prospect(data: dict, db: Session):
    """
    Atualiza um candidato dentro de um prospect.
    O payload deve conter codigo_vaga, codigo_candidato, e os campos a atualizar (por ex. situacao_candidato, comentario).
    Atualiza a 'ultima_atualizacao' para a data atual.
    """
    codigo_candidato = int(data["codigo_candidato"])
    stmt = select(Prospect).where(
        Prospect.codigo_vaga == data["codigo_vaga"],
        Prospect.codigo_candidato == codigo_candidato
    )
    prospect_existente = db.exec(stmt).first()
    if not prospect_existente:
        raise Exception("Prospect não encontrado para os códigos informados.")
    
    if "situacao_candidato" in data and data["situacao_candidato"]:
        prospect_existente.situacao_candidato = data["situacao_candidato"]
    if "comentario" in data:
        prospect_existente.comentario = data["comentario"]
    
    prospect_existente.ultima_atualizacao = datetime.now().strftime("%d-%m-%Y")
    db.add(prospect_existente)
    db.commit()
    db.refresh(prospect_existente)
    return prospect_existente

def listar_prospects_group(db: Session, offset: int = 0, limit: int = 100):
    """
    Retorna os prospects agrupados por codigo_vaga, aplicando paginação nos grupos.
    Para cada grupo (vaga), busca os prospects associados.
    """
    # Consulta para obter os grupos distintos (chave e título da vaga, por exemplo)
    stmt_groups = (
        select(Prospect.codigo_vaga, Prospect.titulo_vaga)
        .group_by(Prospect.codigo_vaga, Prospect.titulo_vaga)
        .order_by(Prospect.codigo_vaga)
        .offset(offset)
        .limit(limit)
    )
    grupos = db.exec(stmt_groups).all()
    
    result = []
    for grupo in grupos:
        codigo_vaga, titulo_vaga = grupo
        # Consulta para obter os prospects da vaga
        stmt_prospects = select(Prospect).where(Prospect.codigo_vaga == codigo_vaga)
        prospects = db.exec(stmt_prospects).all()
        result.append({
            "codigo_vaga": codigo_vaga,
            "titulo_vaga": titulo_vaga,
            "modalidade": "",  # Caso tenha, insira a informação ou deixe vazio
            "prospects": prospects
        })
    return result