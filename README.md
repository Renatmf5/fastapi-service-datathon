# FastAPI Service Datathon

Este é um projeto desenvolvido para a disciplina de Pós-Graduação, utilizando a framework FastAPI. A API foi criada para realizar operações em dois bancos de dados distintos (um para autenticação e outro para sistema), e conta com diversos endpoints para manipulação dos dados. Além disso, a API foi preparada para deploy na AWS via ECS, utilizando o AWS CodeDeploy.

## Índice

- [Estrutura do Projeto](#estrutura-do-projeto)
- [Endpoints](#endpoints)
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
└── cache/                          
    └── ...                         # Arquivos de cache, metadados e índices
```

### Endpoints

A API possui os seguintes endpoints (localizados em `api/v1/endpoints/`):

Cada um desses endpoints utiliza a sessão do banco de dados (`db: Session = Depends(get_system_session)`) para garantir a consistência e segurança na manipulação dos dados. As operações são tratadas com atenção aos possíveis erros, retornando status adequados e mensagens informativas para facilitar o diagnóstico e uso da API.

## Endpoints de Candidatos

**/candidatos** (`candidatos.py`):  
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

### Endpoints de Inferências

**/inferencias** (`inferencias.py`):  
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

- **/prospects** (`prospects.py`):  
  _Descrição_: Endpoints para operações relacionadas aos prospects, representando os potenciais candidatos que podem ser indicados para oportunidades.  
  _Comentário_: Permite a listagem, cadastro e atualização de prospects, auxiliando na triagem de candidatos para futuras oportunidades.

- **/usuarios** (`usuarios.py`):  
  _Descrição_: Endpoints relativos à autenticação e gerenciamento de usuários que têm acesso à API.  
  _Comentário_: Essencial para operações de login, criação e gerenciamento dos dados dos usuários (por exemplo, administradores ou usuários finais).

- **/vagas** (`vagas.py`):  
  _Descrição_: Endpoints para manipulação e consulta de vagas, incluindo dados sobre informações básicas, perfil e benefícios da posição.  
  _Comentário_: Permite o cadastramento de vagas e a atualização das informações relativas às oportunidades de emprego.

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

