# Backend - Análise Fundamentalista com IA

Este projeto é o backend responsável por:

1.  Coletar documentos da CVM (FRE e ITR).
2.  Processar os documentos utilizando inteligência artificial.
3.  Gerar relatórios financeiros profissionais com gráficos.

## Estrutura do Projeto (Sugestão Inicial)

```
backend/
├── app/                  # Contém a lógica principal da aplicação FastAPI
│   ├── __init__.py
│   ├── main.py           # Ponto de entrada da aplicação FastAPI
│   ├── core/             # Configurações, middlewares, etc.
│   │   ├── __init__.py
│   │   └── config.py
│   ├── api/              # Módulos da API (routers)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/  # Endpoints específicos
│   │       │   ├── __init__.py
│   │       │   ├── documents.py
│   │       │   └── reports.py
│   │       └── schemas.py    # Modelos Pydantic para validação
│   ├── services/         # Lógica de negócios
│   │   ├── __init__.py
│   │   ├── cvm_service.py
│   │   ├── ai_service.py
│   │   └── report_service.py
│   ├── models/           # Modelos de banco de dados (ex: SQLAlchemy)
│   │   └── __init__.py
│   ├── crud/             # Operações CRUD com o banco de dados
│   │   └── __init__.py
│   └── utils/            # Funções utilitárias
│       └── __init__.py
├── tests/                # Testes unitários e de integração
│   ├── __init__.py
│   └── ...
├── .env.example          # Exemplo de variáveis de ambiente
├── .gitignore
├── requirements.txt
└── README.md
```

## Como Configurar e Rodar (Exemplo)

1.  **Clone o repositório** (se aplicável)
2.  **Crie e ative um ambiente virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    .\venv\Scripts\activate    # Windows
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure as variáveis de ambiente:**
    Copie `.env.example` para `.env` e preencha os valores necessários.
5.  **Rode a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```

Acesse a API em `http://127.0.0.1:8000`.
A documentação interativa (Swagger UI) estará disponível em `http://127.0.0.1:8000/docs`. 