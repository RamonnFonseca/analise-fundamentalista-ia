import requests
from bs4 import BeautifulSoup # Adicionado para parsear HTML
import os # Adicionado para manipulação de caminhos e diretórios
import zipfile # Adicionado para manipulação de arquivos ZIP
from io import BytesIO # Adicionado para manipular o ZIP em memória
import pandas as pd # Adicionado pandas
from typing import Dict, List, Literal # Adicionado
# from ..core.config import settings # Para buscar CVM_BASE_URL de configurações

# Lógica de negócios para buscar, baixar e processar inicialmente
# os documentos FRE e ITR da CVM.
# - Interação com o site/API da CVM.
# - Extração de texto (se PDF).
# - Armazenamento inicial dos dados brutos ou semi-processados.

# Placeholder - Idealmente, viria de settings.CVM_BASE_URL que carrega do .env
# Lembre-se de adicionar CVM_BASE_URL="https://dados.cvm.gov.br/dados/" ao seu .env e .env.example
CVM_API_BASE_URL = "https://dados.cvm.gov.br/dados/" # Exemplo
DEFAULT_DOWNLOAD_PATH = os.path.join("data", "raw_cvm_files") # Caminho padrão para downloads

# Mapeamento dos nomes das demonstrações para seus arquivos correspondentes (versão CONSOLIDADA)
# Adicionaremos mais conforme necessário
STATEMENT_FILES_MAP = {
    "BPA": "{doc_type}_cia_aberta_BPA_con_{year}.csv", # Balanço Patrimonial Ativo
    "BPP": "{doc_type}_cia_aberta_BPP_con_{year}.csv", # Balanço Patrimonial Passivo
    "DRE": "{doc_type}_cia_aberta_DRE_con_{year}.csv", # Demonstração do Resultado
    "DFC_MI": "{doc_type}_cia_aberta_DFC_MI_con_{year}.csv", # Fluxo de Caixa (Método Indireto)
}

def fetch_cvm_data(endpoint: str):
    """
    Busca dados de um endpoint específico da CVM.
    Exemplo de endpoint: "CIA_ABERTA/DOC/IPE/DADOS/" para Informações Eventuais.
    Os dados de FRE e ITR geralmente são arquivos ZIP contendo CSVs.
    """
    full_url = f"{CVM_API_BASE_URL}{endpoint.lstrip('/')}"
    print(f"Buscando dados de texto/HTML de: {full_url}")
    try:
        response = requests.get(full_url, timeout=60) # Aumentado timeout para dados maiores
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ocorreu: {http_err} - URL: {full_url}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão ocorreu: {conn_err} - URL: {full_url}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout ocorreu: {timeout_err} - URL: {full_url}")
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro de requisição ocorreu: {req_err} - URL: {full_url}")
    return None

def download_cvm_file(file_url_segment: str) -> bytes | None:
    """
    Baixa o conteúdo binário de um arquivo da CVM.
    Args:
        file_url_segment: O segmento da URL do arquivo após a base_url da CVM (ex: "CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_2011.zip")
    Returns:
        Os bytes do arquivo ou None em caso de erro.
    """
    full_url = f"{CVM_API_BASE_URL}{file_url_segment.lstrip('/')}"
    print(f"Baixando arquivo de: {full_url}")
    try:
        response = requests.get(full_url, timeout=300) # Timeout maior para downloads de arquivos
        response.raise_for_status()
        return response.content
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao baixar o arquivo: {http_err} - URL: {full_url}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de Conexão ao baixar o arquivo: {conn_err} - URL: {full_url}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout ao baixar o arquivo: {timeout_err} - URL: {full_url}")
    except requests.exceptions.RequestException as req_err:
        print(f"Um erro de requisição ao baixar o arquivo ocorreu: {req_err} - URL: {full_url}")
    return None

def list_available_zip_files(document_type: str) -> list[str]:
    """
    Lista os nomes dos arquivos .zip disponíveis para um tipo de documento (ITR ou FRE).

    Args:
        document_type: "ITR" ou "FRE".

    Returns:
        Uma lista de nomes de arquivos .zip ou uma lista vazia em caso de erro.
    """
    if document_type.upper() not in ["ITR", "FRE"]:
        print(f"Tipo de documento inválido: {document_type}. Use 'ITR' ou 'FRE'.")
        return []

    endpoint = f"CIA_ABERTA/DOC/{document_type.upper()}/DADOS/"
    html_content = fetch_cvm_data(endpoint)

    if not html_content:
        print(f"Não foi possível obter o conteúdo HTML para {document_type} de {endpoint}")
        return []

    soup = BeautifulSoup(html_content, 'html.parser')
    zip_files = []
    # Os links para os arquivos .zip estão em tags <a> dentro de uma tag <pre>
    # Este seletor pode precisar de ajuste se a estrutura da página da CVM mudar.
    for a_tag in soup.find_all('a'):
        href = a_tag.get('href')
        if href and href.lower().endswith('.zip'):
            zip_files.append(href)
    
    if not zip_files:
        print(f"Nenhum arquivo .zip encontrado para {document_type} em {endpoint}")
        print("Verifique a estrutura do HTML ou o endpoint.")

    return zip_files

def download_and_unzip_cvm_file(document_type: str, zip_file_name: str, base_extract_path: str = DEFAULT_DOWNLOAD_PATH) -> str | None:
    """
    Baixa um arquivo .zip específico da CVM e o descompacta em um diretório estruturado.

    Args:
        document_type: "ITR" ou "FRE".
        zip_file_name: O nome do arquivo .zip (ex: "itr_cia_aberta_2011.zip").
        base_extract_path: O diretório base onde os arquivos serão extraídos.
                           Padrão: "data/raw_cvm_files".

    Returns:
        O caminho para o diretório onde os arquivos foram extraídos ou None em caso de falha.
    """
    if document_type.upper() not in ["ITR", "FRE"]:
        print(f"Tipo de documento inválido: {document_type}. Use 'ITR' ou 'FRE'.")
        return None

    file_url_segment = f"CIA_ABERTA/DOC/{document_type.upper()}/DADOS/{zip_file_name}"
    zip_content = download_cvm_file(file_url_segment)

    if not zip_content:
        print(f"Falha ao baixar o arquivo {zip_file_name}.")
        return None

    # Determina o ano a partir do nome do arquivo (ex: itr_cia_aberta_2011.zip -> 2011)
    year_str = "".join(filter(str.isdigit, zip_file_name))
    if not year_str or len(year_str) < 4: # Heurística simples para pegar o ano
        print(f"Não foi possível determinar o ano a partir do nome do arquivo: {zip_file_name}")
        # Tenta pegar os 4 dígitos antes do .zip se for o caso
        name_without_ext = zip_file_name.lower().replace(".zip","")
        if name_without_ext[-4:].isdigit():
            year_str = name_without_ext[-4:]
        else:
            print("Usando 'unknown_year' como fallback para o diretório do ano.")
            year_str = "unknown_year"
    else:
        # Pega os primeiros 4 dígitos se houver mais (ex: DFP_2010_2011 -> 2010)
        year_str = year_str[:4]


    extract_to_path = os.path.join(base_extract_path, document_type.upper(), year_str)
    
    try:
        os.makedirs(extract_to_path, exist_ok=True)
        print(f"Diretório de extração criado/confirmado: {extract_to_path}")

        with zipfile.ZipFile(BytesIO(zip_content)) as zf:
            zf.extractall(extract_to_path)
        print(f"Arquivo {zip_file_name} descompactado com sucesso em {extract_to_path}")
        return extract_to_path
    except zipfile.BadZipFile:
        print(f"Erro: O arquivo {zip_file_name} não é um arquivo ZIP válido ou está corrompido.")
    except OSError as e:
        print(f"Erro de OS ao criar diretórios ou extrair arquivos: {e}")
    except Exception as e:
        print(f"Uma exceção inesperada ocorreu durante a descompactação: {e}")
    
    return None

def read_cvm_csv(csv_file_path: str) -> pd.DataFrame | None:
    """
    Lê um arquivo CSV da CVM e o carrega em um DataFrame pandas.
    Os arquivos da CVM usam encoding 'latin-1' e ';' como delimitador.

    Args:
        csv_file_path: O caminho completo para o arquivo .csv.

    Returns:
        Um DataFrame pandas com o conteúdo do CSV ou None em caso de erro.
    """
    print(f"Lendo arquivo CSV: {csv_file_path}")
    try:
        # Os arquivos da CVM geralmente são delimitados por ';' e usam encoding 'latin-1'
        df = pd.read_csv(csv_file_path, sep=';', encoding='latin-1', low_memory=False)
        print(f"Arquivo {os.path.basename(csv_file_path)} lido com sucesso.")
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em {csv_file_path}")
    except pd.errors.EmptyDataError:
        print(f"Erro: Arquivo CSV está vazio: {csv_file_path}")
    except Exception as e:
        print(f"Ocorreu um erro ao ler o arquivo CSV {csv_file_path}: {e}")
    return None

def get_financial_statements(
    doc_type: Literal["ITR", "FRE"],
    year: int,
    cnpj: str,
    statements: List[str] = None
) -> Dict[str, pd.DataFrame]:
    """
    Busca e processa as demonstrações financeiras de uma empresa específica.

    Args:
        doc_type: "ITR" ou "FRE".
        year: Ano do relatório.
        cnpj: CNPJ da empresa (formatado: "XX.XXX.XXX/XXXX-XX").
        statements: Lista de demonstrações a serem buscadas (ex: ["BPA", "DRE"]).
                    Se None, busca todas as mapeadas em STATEMENT_FILES_MAP.

    Returns:
        Um dicionário onde as chaves são os nomes das demonstrações (ex: "BPA")
        e os valores são os DataFrames do pandas com os dados da empresa.
    """
    print(f"Buscando demonstrações para CNPJ {cnpj}, Ano {year}, Tipo {doc_type}")

    # Garante que os arquivos para o ano/tipo existem, se não, baixa-os.
    doc_type_lower = doc_type.lower()
    year_path = os.path.join(DEFAULT_DOWNLOAD_PATH, doc_type, str(year))
    if not os.path.exists(year_path):
        print(f"Dados para {doc_type}/{year} não encontrados localmente. Tentando baixar...")
        # Lógica para encontrar o nome do zip e baixar (simplificado por enquanto)
        available_files = list_available_zip_files(doc_type)
        zip_to_download = next((f for f in available_files if str(year) in f), None)
        if not zip_to_download:
            print(f"Não foi possível encontrar o arquivo .zip para {doc_type}/{year} no site da CVM.")
            return {}
        
        download_and_unzip_cvm_file(doc_type, zip_to_download)

    if statements is None:
        statements_to_fetch = list(STATEMENT_FILES_MAP.keys())
    else:
        statements_to_fetch = statements

    company_statements = {}

    for stmt_key in statements_to_fetch:
        if stmt_key not in STATEMENT_FILES_MAP:
            print(f"Aviso: Demonstração '{stmt_key}' não é conhecida. Ignorando.")
            continue

        file_pattern = STATEMENT_FILES_MAP[stmt_key]
        csv_filename = file_pattern.format(doc_type=doc_type_lower, year=year)
        csv_path = os.path.join(year_path, csv_filename)

        if not os.path.exists(csv_path):
            print(f"Aviso: Arquivo {csv_filename} não encontrado em {year_path}. Ignorando demonstração '{stmt_key}'.")
            continue

        # Ler o CSV completo
        full_df = read_cvm_csv(csv_path)
        if full_df is None:
            continue

        # Filtrar pelo CNPJ da empresa
        # O CNPJ do usuário (validado pela API) é comparado diretamente com a coluna do CSV.
        company_df = full_df[full_df['CNPJ_CIA'] == cnpj].copy()
        
        if company_df.empty:
            print(f"Nenhum dado encontrado para o CNPJ {cnpj} no arquivo {csv_filename}.")
            continue

        # TODO: Adicionar lógica mais sofisticada de filtragem
        # - Pegar a última VERSAO
        # - Tratar as datas (DT_FIM_EXERC)
        # - Pivotar a tabela para um formato mais legível

        print(f"Dados para a demonstração '{stmt_key}' encontrados. {len(company_df)} linhas.")
        company_statements[stmt_key] = company_df

    return company_statements

# Exemplo de como poderia ser usado (para teste local):
# if __name__ == '__main__':
#     # Teste 1: Listar arquivos ITR
#     print("\n--- Testando list_available_zip_files para ITR ---")
#     itr_zip_files = list_available_zip_files("ITR")
#     if itr_zip_files:
#         print(f"Arquivos ITR .zip encontrados ({len(itr_zip_files)}):")
#         print(f"  Primeiros 2: {itr_zip_files[:2]}...")
#     else:
#         print("Nenhum arquivo ITR .zip encontrado.")

#     # Teste 2: Baixar e descompactar o primeiro arquivo ITR listado (se houver)
#     extracted_path_for_csv_test = None
#     if itr_zip_files:
#         first_itr_zip = itr_zip_files[0] # Pega o mais antigo
#         print(f"\n--- Testando download_and_unzip_cvm_file para: {first_itr_zip} ---")
#         extracted_path_for_csv_test = download_and_unzip_cvm_file("ITR", first_itr_zip)
#         if extracted_path_for_csv_test:
#             print(f"Arquivos de {first_itr_zip} extraídos para: {extracted_path_for_csv_test}")
#         else:
#             print(f"Falha ao baixar e descompactar {first_itr_zip}.")
#     else:
#         print("\nSkipping download test: Nenhum arquivo ITR encontrado para baixar.")

#     # Teste 3: Ler um arquivo CSV específico do diretório extraído
#     if extracted_path_for_csv_test:
#         year_from_zip = "".join(filter(str.isdigit, first_itr_zip))[:4] if itr_zip_files else "unknown_year"
#         target_csv_name = f"itr_cia_aberta_BPA_con_{year_from_zip}.csv"
#         full_csv_path = os.path.join(extracted_path_for_csv_test, target_csv_name)

#         print(f"\n--- Testando read_cvm_csv para: {full_csv_path} ---")
#         df_cvm = read_cvm_csv(full_csv_path)

#         if df_cvm is not None:
#             print(f"\nInformações sobre o DataFrame de {target_csv_name}:")
#             df_cvm.info()
#             print(f"\nPrimeiras 5 linhas do DataFrame de {target_csv_name}:")
#             print(df_cvm.head())
#         else:
#             print(f"Falha ao ler o arquivo CSV: {target_csv_name}")
#     else:
#         print("\nSkipping CSV reading test: Caminho de extração não disponível ou falha no download/unzip.") 