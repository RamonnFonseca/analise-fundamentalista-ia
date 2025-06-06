# Backend - Análise Fundamentalista com IA

Este projeto é o backend responsável por orquestrar a coleta, análise e disponibilização de dados financeiros de empresas de capital aberto no Brasil.

## Funcionalidades Principais

1.  **Coleta de Dados da CVM:** Baixa e processa automaticamente as demonstrações financeiras (ITR e DFP) diretamente do [portal de dados abertos da CVM](https://dados.cvm.gov.br/).
2.  **Análise com IA:** Utiliza o modelo de linguagem avançado do Google (Gemini) para gerar uma análise fundamentalista em texto, como se fosse redigida por um analista sênior.
3.  **Dados Estruturados:** Fornece um resumo com os principais indicadores financeiros (Receita, Lucro, Ativos, etc.) em um formato JSON limpo, pronto para ser consumido.
4.  **API RESTful:** Expõe um endpoint via FastAPI para que uma aplicação frontend possa solicitar e exibir os relatórios e os dados financeiros.

## Como Configurar e Rodar o Projeto

Siga os passos abaixo para executar o backend localmente.

### 1. Pré-requisitos

*   Python 3.9 ou superior
*   Uma chave de API para o Google Gemini. Você pode obter uma no [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Configuração do Ambiente

Primeiro, clone o repositório e navegue até a pasta do backend.

**Crie e ative um ambiente virtual:**

*   No Windows (PowerShell):
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```
*   No Linux ou macOS:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    
**Instale as dependências:**
Com o ambiente virtual ativo, instale todas as bibliotecas necessárias.
```bash
pip install -r requirements.txt
```

**Configure as variáveis de ambiente:**
Crie um arquivo chamado `.env` na pasta `backend` (você pode copiar o `.env.example`). Dentro do `.env`, adicione sua chave da API do Gemini:
