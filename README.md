# FastAPI Service Datathon

Este é um projeto desenvolvido para a disciplina de Pós-Graduação, utilizando a framework FastAPI. A API foi criada para realizar operações em dois bancos de dados distintos (um para autenticação e outro para sistema), e conta com diversos endpoints para manipulação dos dados. Além disso, a API foi preparada para deploy na AWS via ECS, utilizando o AWS CodeDeploy.

## Índice

## Índice

- [Estrutura do Projeto](#estrutura-do-projeto)
- [Sumário de Endpoints](#sumário-de-endpoints)
- [Endpoints Detalhados](#endpoints-detalhados)
  - [Candidatos](#endpoints-de-candidatos)
  - [Inferências](#endpoints-de-inferências)
  - [Prospects](#endpoints-de-prospects)
  - [Vagas](#endpoints-de-vagas)
  - [Usuários](#endpoints-de-usuários)
- [Testes Unitários](#testes-unitários)
- [Operações com Banco de Dados](#operações-com-banco-de-dados)
- [Deploy via AWS ECS](#deploy-via-aws-ecs)
- [Instalação e Inicialização](#instalação-e-inicialização)
- [Considerações Finais](#considerações-finais)

## Estrutura do Projeto

A estrutura de pastas do projeto está organizada da seguinte forma:

```plaintext
├── appspec.yml                      # Configuração do CodeDeploy para deployment na AWS ECS  
├── Dockerfile                       # Arquivo para construção da imagem Docker  
├── main.py                          # Arquivo principal que instancia a aplicação FastAPI e inicializa os bancos de dados  
├── requirements.txt                 # Dependências do projeto  
├── api/                             # Endpoints e utilitários da API  
│   ├── v1/                        
│   │   ├── api.py                  # Agrega os endpoints e configura os routers  
│   │   └── endpoints/              
│   │       ├── candidatos.py       # Endpoints relacionados a candidatos  
│   │       ├── inferencias.py      # Endpoints para geração e consulta de inferências  
│   │       ├── prospects.py        # Endpoints voltados aos prospects  
│   │       ├── usuarios.py         # Endpoints para operações com usuários  
│   │       └── vagas.py            # Endpoints para manipulação de vagas  
│   └── utils/                     
│       └── functions/             
│           └── CRUD_SystemDB.py    # Funções para operações CRUD no banco do sistema  
├── core/                           
│   ├── config.py                   # Configurações e variáveis de ambiente  
│   ├── database.py                 # Configuração dos bancos de dados: auth e system  
│   └── auth.py                     # Autenticação e configurações relacionadas  
├── models/                         
│   ├── candidato_model.py          
│   ├── prospect_model.py           
│   ├── usuario_model.py            
│   └── vagas_model.py              
├── schemas/                        
│   ├── candidato_schema.py         
│   ├── prospect_schema.py          
│   ├── usuario_schema.py           
│   └── vagas_schema.py             
├── scripts/                        
│   ├── before_install.sh           # Script executado antes da instalação  
│   ├── after_install.sh            # Script executado após a instalação  
│   ├── start_application.sh        # Script para iniciar a aplicação  
│   └── stop_application.sh         # Script para interromper a aplicação
├── tests/                        
│   ├── test_candidatos.sh           # Testes para endpoints relacionados a candidatos. 
│   ├── test_inferencias.sh          # Testes para endpoints de inferências (match, recomendação e drift report).
│   ├── test_prospects.sh            # Testes para endpoints relacionados a prospects. 
│   └── test_vagas.sh                # Testes para endpoints relacionados a vagas.
└── cache/                          
    └── ...                         # Arquivos de cache, metadados e índices
```

### Endpoints

A API possui os seguintes endpoints (localizados em `api/v1/endpoints/`):

Cada um desses endpoints utiliza a sessão do banco de dados (`db: Session = Depends(get_system_session)`) para garantir a consistência e segurança na manipulação dos dados. As operações são tratadas com atenção aos possíveis erros, retornando status adequados e mensagens informativas para facilitar o diagnóstico e uso da API.

## Endpoints de Candidatos

### **/candidatos** (`candidatos.py`):  
  _Descrição_: Endpoints que lidam com as informações de candidatos (dados básicos, pessoais, profissionais, formação, idiomas e currículos).  
  _Comentário_: Este conjunto de endpoints é usado para cadastrar, atualizar ou consultar informações dos candidatos que estão participando dos processos de seleção.

- **POST /candidatos/create**: Cria um novo candidato no sistema.
  - **Descrição**: Este endpoint insere os dados de um candidato. Caso o candidato já exista (baseado no código profissional), os dados serão atualizados. É esperado um objeto JSON estruturado contendo informações divididas em:
    - **infos_basicas**: Dados principais do candidato (ex.: nome, cpf, código_profissional, etc.).
    - **informacoes_pessoais** (opcional): Dados pessoais, como endereço, telefone, etc.
    - **informacoes_profissionais** (opcional): Histórico e dados profissionais.
    - **formacao_e_idiomas** (opcional): Dados de formação acadêmica e idiomas.
    - **cv_pt** (opcional): Currículo em português.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "infos_basicas": {
        "codigo_profissional": 123,
        "nome": "João Silva",
        "cpf": "11122233344",
        "...": "outros dados"
      },
      "informacoes_pessoais": {
        "endereco": "Rua A, 123",
        "telefone": "11999999999"
      },
      "informacoes_profissionais": {
        "empresa": "Empresa XPTO",
        "cargo": "Desenvolvedor"
      },
      "formacao_e_idiomas": {
        "formacao": "Graduação em Ciência da Computação",
        "idiomas": ["Português", "Inglês"]
      },
      "cv_pt": "Link ou texto do currículo em português"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "message": "Candidato inserido com sucesso!",
        "codigo_candidato": 123
      }
      ```
    - **400 Bad Request**: Em caso de dados inválidos ou ausência de campos obrigatórios.
    - **500 Internal Server Error**: Em caso de erro na operação de inserção/atualização.

- **GET /candidatos/list**: Lista os candidatos com suporte à paginação.
  - **Descrição**: Este endpoint retorna uma lista simplificada de candidatos. Permite o uso de parâmetros de query para definir `offset` e `limit`, possibilitando a paginação dos resultados.
  - **Query Parameters**:
    - **offset** (opcional): Posição inicial dos registros (padrão: 0).
    - **limit** (opcional): Número máximo de registros a serem retornados (padrão: 100).
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "total": 50,
        "offset": 0,
        "limit": 100,
        "data": [
          { "codigo_profissional": 123, "nome": "João Silva", "...": "outros campos" },
          { "codigo_profissional": 124, "nome": "Maria Souza", "...": "outros campos" }
        ]
      }
      ```
    - **500 Internal Server Error**: Em caso de falha ao recuperar os dados.

- **GET /candidatos/details/{codigo_profissional}**: Retorna os detalhes completos de um candidato.
  - **Descrição**: Busca e retorna todas as informações do candidato identificado por `codigo_profissional`. São retornados os dados de:
    - Informações básicas
    - Informações pessoais
    - Informações profissionais
    - Formação e idiomas
    - Currículos  
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Parâmetros de URL**:
    - **codigo_profissional**: Código identificador do candidato.
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "infos_basicas": { "...": "dados básicos" },
        "informacoes_pessoais": { "...": "dados pessoais" },
        "informacoes_profissionais": { "...": "dados profissionais" },
        "formacao_e_idiomas": { "...": "dados de formação e idiomas" },
        "curriculos": { "...": "dados do currículo" }
      }
      ```
    - **400 Bad Request**: Se o código informado for inválido.
    - **404 Not Found**: Se nenhum candidato for encontrado com o código informado.
    - **500 Internal Server Error**: Em caso de erro na consulta.

- **POST /candidatos/update-tables**: Atualiza as tabelas de candidatos a partir de um arquivo JSON armazenado no S3.
  - **Descrição**: Este endpoint aciona uma tarefa em background para ler um arquivo JSON do S3 e atualizar completamente as tabelas de candidatos. O JSON deve conter os dados completos de cada candidato.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "file_key": "caminho/do/arquivo.json"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de atualização iniciada em background." }
      ```
    - **400 Bad Request**: Se o campo `file_key` estiver ausente.
    - **500 Internal Server Error**: Em caso de erro na inicialização da tarefa.

- **POST /candidatos/export-applicants**: Exporta os dados de candidatos para um arquivo JSON e realiza o upload para o S3, de forma assíncrona.
  - **Descrição**: Este endpoint consulta toda a base de candidatos, monta um JSON no formato necessário para exportação e envia o arquivo para um bucket S3. Todo o processo ocorre em background.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de exportação de candidatos iniciada em background." }
      ```
    - **500 Internal Server Error**: Em caso de erro ao iniciar a tarefa de exportação.

---

## Endpoints de Inferências

### **/inferencias** (`inferencias.py`):  
  _Descrição_: Endpoints voltados para a geração e consulta de inferências a partir dos dados disponíveis.  
  _Comentário_: São utilizados para executar análises ou modelos preditivos que ajudem a identificar padrões ou tendências entre os dados dos candidatos e vagas.

- **POST /inferencias/matchModel/predict**: Calcula a probabilidade de match entre o candidato e a vaga.  
  - **Descrição**:  
    Este endpoint utiliza um modelo de classificação para prever a probabilidade de um candidato ser compatível com uma vaga.  
    O modelo é carregado a partir de um arquivo .pkl (armazenado no S3 ou em cache) e o payload é convertido para um DataFrame do pandas antes da predição.  
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "sexo": "M",
      "estado_civil": "Solteiro",
      "pcd": "Não",
      "vaga_especifica_para_pcd": "Não",
      "pais_vaga": "Brasil",
      "nivel_academico": "Ensino Superior Completo",
      "tipo_contratacao": "CLT",
      "cidade": "São Paulo",
      "cidade_vaga": "São Paulo",
      "nivel_profissional": "Pleno",
      "nivel_profissional_vaga": "Pleno",
      "ingles": "Avançado",
      "espanhol": "Intermediário",
      "outros_idiomas": "Nenhum",
      "nivel_ingles_vaga": "Avançado",
      "nivel_espanhol_vaga": "Intermediário",
      "titulo_profissional": "Desenvolvedor Backend",
      "titulo_vaga": "Backend Developer",
      "conhecimentos_tecnicos": "Python, FastAPI, SQLAlchemy",
      "certificacoes": "AWS Certified",
      "outras_certificacoes": "Scrum",
      "area_atuacao": "TI",
      "areas_atuacao_vaga": "Desenvolvimento",
      "competencia_tecnicas_e_comportamentais": "Trabalho em equipe, responsabilidade",
      "cv_candidato": "https://link-para-cv.com"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "match_probability": 85.3
      }
      ```
      _Comentário_: O valor retornado representa a probabilidade (em porcentagem) de que o candidato seja considerado compatível com a vaga.
    - **500 Internal Server Error**: Em caso de erro no processamento ou na carga do modelo.

- **POST /inferencias/recommendationModel/predict**: Gera recomendações de vagas para o candidato.  
  - **Descrição**:  
    Este endpoint utiliza um modelo de recomendação para sugerir vagas que se encaixem no perfil do candidato.  
    Ele incorpora uma técnica de embedding utilizando o SentenceTransformer e utiliza um índice Annoy para encontrar os candidatos mais próximos, retornando os dados relevantes das vagas recomendadas.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "titulo_profissional": "Desenvolvedor Backend",
      "conhecimentos_tecnicos": "Python, FastAPI, SQLAlchemy",
      "certificacoes": "AWS Certified",
      "outras_certificacoes": "Scrum",
      "cidade": "São Paulo",
      "ingles": "Avançado",
      "espanhol": "Básico",
      "outros_idiomas": "Nenhum",
      "pcd": "Não",
      "cv_candidato": "https://link-para-cv.com"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "data": [
          {
            "codigo_vaga": 101,
            "titulo_vaga": "Backend Developer",
            "competencia_tecnicas_e_comportamentais": "Python, SQL, Liderança",
            "areas_atuacao_vaga": "Desenvolvimento"
          },
          {
            "codigo_vaga": 102,
            "titulo_vaga": "API Developer",
            "competencia_tecnicas_e_comportamentais": "FastAPI, Docker",
            "areas_atuacao_vaga": "Tecnologia"
          }
        ]
      }
      ```
      _Comentário_: O array retornado contém as vagas recomendadas com os principais atributos que ajudam na avaliação da recomendação.
    - **500 Internal Server Error**: Em caso de falhas ao carregar os modelos ou erros no processo de recomendação.

- **GET /inferencias/driftReport**: Retorna o relatório de drift do modelo.  
  - **Descrição**:  
    Este endpoint busca o caminho para o relatório de drift (indicativo de mudanças no desempenho/qualidade dos modelos) e retorna seu conteúdo.  
    Caso o relatório não seja encontrado, é retornado um erro 404.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "drift_report": "Conteúdo do relatório de drift..."
      }
      ```
      _Comentário_: O conteúdo retornado é uma string contendo o relatório completo, que pode ser utilizado para análise e monitoramento dos modelos.
    - **404 Not Found**: Se o relatório não for encontrado.
    - **500 Internal Server Error**: Em caso de erro ao acessar ou ler o relatório.

---

## Endpoints de Prospects

### **/prospects** (`prospects.py`):  
  _Descrição_: Endpoints para operações relacionadas aos prospects, representando os potenciais candidatos que podem ser indicados para oportunidades.  
  _Comentário_: Permite a listagem, cadastro e atualização de prospects, auxiliando na triagem de candidatos para futuras oportunidades.

- **POST /prospects/add-candidate**: Adiciona um candidato à vaga (prospect).  
  - **Descrição**:  
    Este endpoint cria um novo prospect associando um candidato a uma vaga. Se não existir nenhum prospect para a vaga, um novo registro é criado; se já existir uma combinação de `codigo_vaga` e `codigo_candidato`, uma exceção é lançada.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "codigo_vaga": 101,
      "titulo_vaga": "Backend Developer",
      "nome": "João Silva",
      "codigo_candidato": 123,
      "situacao_candidato": "Em análise",
      "data_candidatura": "2025-07-12",
      "comentario": "Candidato com experiência em Python",
      "recrutador": "Maria Oliveira"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "message": "Prospect criado com sucesso.",
        "data": {
          "id": 1,
          "codigo_vaga": 101,
          "titulo_vaga": "Backend Developer",
          "nome": "João Silva",
          "codigo_candidato": 123,
          "situacao_candidato": "Em análise",
          "data_candidatura": "2025-07-12",
          "ultima_atualizacao": "12-07-2025",
          "comentario": "Candidato com experiência em Python",
          "recrutador": "Maria Oliveira"
        }
      }
      ```
    - **400 Bad Request**: Caso haja problemas na validação ou se já existir um prospect com os mesmos dados.
  
- **PUT /prospects/update-candidate**: Atualiza informações do candidato no prospect.  
  - **Descrição**:  
    Atualiza campos específicos de um prospect (como a situação do candidato e comentários) e registra a data da última atualização.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "codigo_vaga": 101,
      "codigo_candidato": 123,
      "situacao_candidato": "Aprovado",
      "comentario": "Candidato aprovado para a próxima etapa."
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "message": "Prospect atualizado com sucesso.",
        "data": {
          "id": 1,
          "codigo_vaga": 101,
          "titulo_vaga": "Backend Developer",
          "nome": "João Silva",
          "codigo_candidato": 123,
          "situacao_candidato": "Aprovado",
          "data_candidatura": "2025-07-12",
          "ultima_atualizacao": "12-07-2025",
          "comentario": "Candidato aprovado para a próxima etapa.",
          "recrutador": "Maria Oliveira"
        }
      }
      ```
    - **400 Bad Request**: Se o prospect não for encontrado ou se os dados fornecidos forem inválidos.
  
- **GET /prospects/list**: Lista todos os prospects com suporte à paginação.  
  - **Descrição**:  
    Retorna uma lista simplificada dos prospects cadastrados, permitindo a paginação através dos parâmetros `offset` e `limit`.
  - **Query Parameters**:
    - **offset** (opcional): Posição inicial dos registros (padrão: 0).
    - **limit** (opcional): Número máximo de registros a serem retornados (padrão: 100).
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "total": 50,
        "offset": 0,
        "limit": 100,
        "data": [
          { "id": 1, "codigo_vaga": 101, "nome": "João Silva", "...": "outros campos" },
          { "id": 2, "codigo_vaga": 102, "nome": "Maria Souza", "...": "outros campos" }
        ]
      }
      ```
    - **500 Internal Server Error**: Se ocorrer um erro ao recuperar a lista de prospects.
  
- **GET /prospects/grouped-list**: Lista prospects agrupados por vaga.  
  - **Descrição**:  
    Retorna os prospects agrupados por `codigo_vaga` e `titulo_vaga`, facilitando a visualização dos candidatos por vaga.
  - **Query Parameters**:
    - **offset** (opcional): Posição inicial dos grupos (padrão: 0).
    - **limit** (opcional): Número máximo de grupos a serem retornados (padrão: 100).
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "total_grupos": 5,
        "offset": 0,
        "limit": 100,
        "data": [
          {
            "codigo_vaga": 101,
            "titulo_vaga": "Backend Developer",
            "prospects": [
              { "id": 1, "nome": "João Silva", "...": "outros campos" },
              { "id": 3, "nome": "Carlos Lima", "...": "outros campos" }
            ]
          },
          {
            "codigo_vaga": 102,
            "titulo_vaga": "Frontend Developer",
            "prospects": [
              { "id": 2, "nome": "Maria Souza", "...": "outros campos" }
            ]
          }
        ]
      }
      ```
    - **500 Internal Server Error**: Em caso de erro ao agrupar os prospects.
  
- **POST /prospects/update-tables**: Atualiza as tabelas de prospects usando um arquivo JSON armazenado no S3.  
  - **Descrição**:  
    Aciona uma tarefa em background para ler um arquivo JSON do S3 e atualizar completamente os dados dos prospects.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "file_key": "caminho/do/arquivo_prospects.json"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de atualização iniciada em background." }
      ```
    - **400 Bad Request**: Se o campo `file_key` estiver ausente.
    - **500 Internal Server Error**: Em caso de erro ao iniciar a tarefa.
  
- **POST /prospects/export-prospects**: Exporta os dados de prospects para um arquivo JSON e faz o upload para o S3 de forma assíncrona.  
  - **Descrição**:  
    Consulta toda a base de prospects, monta um JSON estruturado com os dados agrupados por vaga e faz o upload para um bucket do S3, tudo de forma assíncrona.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de exportação de prospects iniciada em background." }
      ```
    - **500 Internal Server Error**: Em caso de erro ao iniciar a tarefa de exportação.

---

## Endpoints de Vagas

### **/vagas** (`vagas.py`):  
  _Descrição_: Endpoints para manipulação e consulta de vagas, incluindo dados sobre informações básicas, perfil e benefícios da posição.  
  _Comentário_: Permite o cadastramento de vagas e a atualização das informações relativas às oportunidades de emprego.

- **POST /vagas/create**: Cria uma nova vaga no sistema.  
  - **Descrição**:  
    Este endpoint insere os dados de uma vaga no sistema. Se a vaga já existir (baseado no `codigo_vaga`), os dados serão atualizados.  
    O objeto JSON de entrada deve conter:
    - **infos_basicas**: Informações essenciais da vaga (por exemplo, título, cliente, tipo de contratação, etc.).
    - **perfil_vaga** (opcional): Detalhes sobre o perfil da vaga, como local de trabalho, requisitos, nível profissional e acadêmico, etc.
    - **beneficios** (opcional): Informações sobre benefícios oferecidos, como valores de venda e compra.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "infos_basicas": {
        "data_requisicao": "2025-07-12",
        "limite_esperado_para_contratacao": "5",
        "titulo_vaga": "Backend Developer",
        "vaga_sap": "XYZ123",
        "cliente": "Cliente A",
        "solicitante_cliente": "Solicitante A",
        "empresa_divisao": "TI",
        "requisitante": "Requisitante A",
        "analista_responsavel": "Analista X",
        "tipo_contratacao": "CLT",
        "prazo_contratacao": "30 dias",
        "objetivo_vaga": "Desenvolver APIs REST",
        "prioridade_vaga": "Alta",
        "origem_vaga": "Interna",
        "superior_imediato": "Gestor Y",
        "nome": "Vaga Backend Developer",
        "telefone": "(11) 99999-9999"
      },
      "perfil_vaga": {
        "pais": "Brasil",
        "estado": "SP",
        "cidade": "São Paulo",
        "bairro": "Centro",
        "regiao": "Sudeste",
        "local_trabalho": "Remoto",
        "vaga_especifica_para_pcd": "Não",
        "faixa_etaria": "25-35",
        "horario_trabalho": "09:00-18:00",
        "nivel_profissional": "Pleno",
        "nivel_academico": "Ensino Superior Completo",
        "nivel_ingles": "Avançado",
        "nivel_espanhol": "Intermediário",
        "outro_idioma": "",
        "areas_atuacao": "Desenvolvimento",
        "principais_atividades": "Desenvolvimento e manutenção de APIs",
        "competencia_tecnicas_e_comportamentais": "Trabalho em equipe, proatividade",
        "demais_observacoes": "Experiência com Python",
        "viagens_requeridas": "Não",
        "equipamentos_necessarios": "Laptop próprio"
      },
      "beneficios": {
        "valor_venda": "1000",
        "valor_compra_1": "800",
        "valor_compra_2": "750"
      }
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "message": "Vaga criada com sucesso!",
        "codigo_vaga": 101
      }
      ```
    - **400 Bad Request**: Em caso de dados inválidos.
    - **500 Internal Server Error**: Se ocorrer um erro durante a operação.

- **GET /vagas/list**: Lista as vagas com suporte à paginação.  
  - **Descrição**:  
    Retorna uma lista simplificada de vagas cadastradas. Permite o uso de parâmetros de query para definição de `offset` e `limit`, facilitando a paginação dos registros.
  - **Query Parameters**:
    - **offset** (opcional): Posição inicial dos registros (padrão: 0).
    - **limit** (opcional): Número máximo de registros a retornar (padrão: 100).
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "total": 50,
        "offset": 0,
        "limit": 100,
        "data": [
          { "codigo_vaga": 101, "titulo_vaga": "Backend Developer", "...": "outros campos" },
          { "codigo_vaga": 102, "titulo_vaga": "Frontend Developer", "...": "outros campos" }
        ]
      }
      ```
    - **500 Internal Server Error**: Se ocorrer algum erro durante a consulta.

- **GET /vagas/details/{codigo_vaga}**: Retorna os detalhes completos de uma determinada vaga.  
  - **Descrição**:  
    Busca e retorna todas as informações de uma vaga identificada pelo `codigo_vaga`. São retornados:
    - Dados das informações básicas.
    - Detalhes do perfil da vaga.
    - Informações sobre benefícios.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Parâmetros de URL**:
    - **codigo_vaga**: Identificador único da vaga.
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "data": {
          "infos_basicas": { "...": "dados básicos da vaga" },
          "perfil_vaga": { "...": "dados do perfil da vaga" },
          "beneficios": { "...": "dados dos benefícios" }
        }
      }
      ```
    - **404 Not Found**: Caso a vaga não seja encontrada.
    - **500 Internal Server Error**: Em caso de erro na consulta.

- **POST /vagas/update-tables**: Atualiza as tabelas de vagas a partir de um arquivo JSON armazenado no S3.  
  - **Descrição**:  
    Este endpoint aciona uma tarefa em background que lê um arquivo JSON armazenado no S3 e atualiza todas as tabelas relacionadas às vagas.  
    O arquivo JSON deve conter os dados estruturados de forma que each registro possa ser identificado e convertido adequadamente para os modelos da vaga.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "file_key": "caminho/do/arquivo_vagas.json"
    }
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de atualização iniciada em background." }
      ```
    - **400 Bad Request**: Se o campo `file_key` for omitido.
    - **500 Internal Server Error**: Se ocorrer erro na inicialização da tarefa.

- **POST /vagas/export-vagas**: Exporta os dados de vagas para um arquivo JSON e realiza o upload para o S3 de forma assíncrona.  
  - **Descrição**:  
    Consulta toda a base de vagas, monta um JSON estruturado com os dados das vagas (incluindo informações básicas, perfil e benefícios) e faz o upload para um bucket S3 na chave `"raw/vagas.json"`.  
    Todo o processo ocorre em background para não bloquear a resposta da API.
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      { "message": "Tarefa de exportação de vagas iniciada em background." }
      ```
    - **500 Internal Server Error**: Em caso de erro ao iniciar a tarefa de exportação.

---

## Endpoints de Usuários

### **/usuarios** (`usuarios.py`):  
  _Descrição_: Endpoints relativos à autenticação e gerenciamento de usuários que têm acesso à API.  
  _Comentário_: Essencial para operações de login, criação e gerenciamento dos dados dos usuários (por exemplo, administradores ou usuários finais).

- **GET /usuarios/logado**: Retorna as informações do usuário atualmente autenticado.  
  - **Descrição**:  
    Este endpoint verifica o token de autenticação enviado no cabeçalho da requisição e retorna os dados básicos do usuário autenticado.  
  - **Cabeçalho**:
    - **Authorization**: Bearer <token>
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      {
        "username": "usuario_exemplo",
        "perfil": "admin"
      }
      ```
    - **401 Unauthorized**: Caso o token seja inválido ou o usuário não esteja autenticado.

- **POST /usuarios/login**: Realiza o login do usuário e retorna um token de acesso.  
  - **Descrição**:  
    Este endpoint recebe os dados de login (username e password) usando o padrão OAuth2PasswordRequestForm e, se as credenciais forem válidas, gera e retorna um token JWT para autenticação das próximas requisições.  
  - **Cabeçalho**:
    - **Content-Type**: application/x-www-form-urlencoded
  - **Exemplo de Corpo (form-data)**:
    ```
    username=usuario_exemplo
    password=senha123
    ```
  - **Resposta**:
    - **200 OK**:  
      ```json
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      ```
    - **401 Unauthorized**: Se as credenciais forem inválidas.

- **POST /usuarios/signup**: Cria um novo usuário no sistema.  
  - **Descrição**:  
    Este endpoint cadastra um novo usuário, recebendo um payload JSON com as informações necessárias (username, password e perfil).  
    A senha é hashada antes de ser armazenada e, em caso de tentativa de cadastro de um usuário já existente, um erro apropriado é retornado.  
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "username": "novo_usuario",
      "password": "senha_supersecreta",
      "perfil": "usuario"
    }
    ```
  - **Resposta**:
    - **201 Created**:  
      ```json
      {
        "username": "novo_usuario",
        "perfil": "usuario"
      }
      ```
    - **400 Bad Request**: Se o usuário já existir.

- **GET /usuarios/list**: Lista todos os usuários cadastrados.  
  - **Descrição**:  
    Este endpoint retorna uma lista de usuários do sistema com os dados básicos de cada um.  
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Resposta**:
    - **200 OK**:  
      ```json
      [
        {
          "username": "usuario1",
          "perfil": "admin"
        },
        {
          "username": "usuario2",
          "perfil": "usuario"
        }
      ]
      ```
    - **500 Internal Server Error**: Em caso de erro na recuperação dos dados.

- **PUT /usuarios/{usuario_id}**: Atualiza os dados de um usuário específico.  
  - **Descrição**:  
    Este endpoint permite atualizar parcialmente os dados de um usuário identificado pelo `usuario_id`.  
    Se o campo `password` for atualizado, a nova senha é hashada antes de ser salva.  
  - **Cabeçalho**:
    - **Content-Type**: application/json
  - **Parâmetros de URL**:
    - **usuario_id**: Identificador único do usuário.
  - **Exemplo de Corpo da Requisição**:
    ```json
    {
      "username": "usuario_atualizado",
      "password": "nova_senha",
      "perfil": "admin"
    }
    ```
  - **Resposta**:
    - **202 Accepted**:  
      ```json
      {
        "username": "usuario_atualizado",
        "perfil": "admin"
      }
      ```
    - **404 Not Found**: Se o usuário com o `usuario_id` informado não existir.
    - **400 Bad Request**: Em caso de dados inválidos.


## Testes Unitários

Foram desenvolvidos testes unitários para garantir a integridade dos principais componentes do sistema. Utilizamos o framework [pytest](https://docs.pytest.org/) pela sua simplicidade e eficácia. A abordagem inclui:

- **Organização dos testes:** Os testes estão organizados em arquivos dedicados, alinhados com as funcionalidades testadas.
- **Ferramentas de apoio:** 
  - [pytest](https://docs.pytest.org/) para execução e gerenciamento dos testes.
  - [coverage.py](https://coverage.readthedocs.io/) para análise de cobertura de código.

- Foram criados testes unitários para validar os principais comportamentos da API. A estrutura dos testes está organizada na pasta `tests/`, onde cada módulo de teste contém testes para um domínio da aplicação, por exemplo:

- `tests/test_candidatos.py`: Testes para endpoints relacionados a candidatos.
- `tests/test_vagas.py`: Testes para endpoints relacionados a vagas.
- `tests/test_prospects.py`: Testes para endpoints relacionados a prospects.
- `tests/test_inferencias.py`: Testes para endpoints de inferências (match, recomendação e drift report).

- **Como executar:**  
  Para executar os testes, utilize o pytest. No terminal, certifique-se de que o ambiente virtual esteja ativado e execute:

  ```bash
  pytest --maxfail=1 --disable-warnings -q


## Operações com Banco de Dados

A API trabalha com duas bases de dados distintas, implementadas utilizando SQLModel:

- **Banco de Autenticação (authDB.db)**:  
  Realiza operações CRUD (criação, leitura, atualização e deleção) para gerenciar os usuários da aplicação. As tabelas são criadas a partir do modelo definido em `models/usuario_model.py`.

- **Banco do Sistema (systemDB.db)**:  
  Armazena dados de candidatos, vagas, prospects, entre outros. As tabelas são criadas a partir dos modelos definidos em:
  - Candidato: `models/candidato_model.py` (dividido em informações básicas, pessoais, profissionais, formação, idiomas e currículos)
  - Vagas: `models/vagas_model.py` (informações básicas, perfil, benefícios)
  - Prospect: `models/prospect_model.py`  
  Durante o startup da aplicação (no arquivo `main.py`), as funções `create_auth_db_and_tables()` e `create_system_db_and_tables()` são executadas para garantir que as tabelas necessárias existam.

## Deploy via AWS ECS

A aplicação foi implementada para deployment na AWS utilizando ECS (Elastic Container Service). Os principais pontos deste processo são:

- **Docker e Containerização**:  
  A aplicação é empacotada como um container Docker, conforme definido no `Dockerfile`. O Dockerfile configura o ambiente, instala as dependências e define o comando de inicialização da API.

- **CodeDeploy e appspec.yml**:  
  O arquivo `appspec.yml` contém a configuração do CodeDeploy, especificando os hooks para os diferentes estágios do deploy:
  - **BeforeInstall**: Executa o script `scripts/before_install.sh` para preparar o ambiente.
  - **AfterInstall**: Executa o script `scripts/after_install.sh` para pós-instalação.
  - **ApplicationStop**: Executa o script `scripts/stop_application.sh` para interromper a aplicação de forma segura.
  - **ApplicationStart**: Executa o script `scripts/start_application.sh` para iniciar a aplicação.
  
  Esses scripts permitem uma atualização controlada e minimizam o downtime durante o deploy.

- **ECS Task Definitions**:  
  No `appspec.yml` há um placeholder para o `TaskDefinition` que é substituído automaticamente durante o deploy, definindo a configuração dos containers no ECS.

## Instalação e Inicialização

Para clonar e executar o projeto localmente, siga os passos abaixo:

1. **Clonagem do repositório**:
   ```bash
   git clone https://github.com/seu-usuario/fastapi-service-datathon.git
   cd fastapi-service-datathon

2. **Criar um ambiente virtual (opcional, mas recomendado)**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
    
3. **Instalar as dependências**:
  ```bash
  pip install -r requirements.txt
  ```

4. **Execução da aplicação**
  - Para ambiente de produção a aplicação rodará na porta 80.:
  ```bash
  python main.py
  ```
 - Para desenvolvimento (com reload automático) a aplicação será executada na porta 8000.:
  ```bash
  export ENV=development
  python main.py
  ```
  
## Considerações Finais
Esta documentação detalha a estrutura, os endpoints e aspectos importantes do projeto. O objetivo é fornecer um panorama completo e profissional, facilitando a compreensão tanto para a entrega acadêmica quanto para eventuais colaboradores que queiram utilizar ou contribuir com o projeto.

Caso haja dúvidas ou necessidade de melhorias, colabore através de issues ou pull requests.

