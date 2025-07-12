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
    └── ...                         # Arquivos de cache, metadados

## Endpoints

A API possui os seguintes endpoints (localizados em `api/v1/endpoints/`):

- **/candidatos** (`candidatos.py`):  
  _Descrição_: Endpoints que lidam com as informações de candidatos (dados básicos, pessoais, profissionais, formação, idiomas e currículos).  
  _Comentário_: Este conjunto de endpoints é usado para cadastrar, atualizar ou consultar informações dos candidatos que estão participando dos processos de seleção.

- **/inferencias** (`inferencias.py`):  
  _Descrição_: Endpoints voltados para a geração e consulta de inferências a partir dos dados disponíveis.  
  _Comentário_: São utilizados para executar análises ou modelos preditivos que ajudem a identificar padrões ou tendências entre os dados dos candidatos e vagas.

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

