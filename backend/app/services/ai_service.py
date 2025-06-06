# Lógica de negócios para interagir com o modelo de IA.
# - Enviar dados processados dos documentos CVM para a IA.
# - Receber e interpretar as análises da IA.
# - Formatar a saída da IA para ser usada na geração de relatórios. 

import json
import re
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from app.core.config import settings
from typing import Dict, Any
import pandas as pd

# Configura a biblioteca do Google com a chave de API das nossas configurações
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_financial_analysis(company_financials: Dict[str, pd.DataFrame]) -> Dict[str, Any] | None:
    """
    Usa o Google Gemini Pro para gerar uma análise financeira a partir dos dados da empresa.

    Args:
        company_financials: Um dicionário onde as chaves são os nomes das demonstrações
                            (ex: "BPA", "DRE") e os valores são DataFrames do pandas.

    Returns:
        Um dicionário com a análise gerada pela IA e dados financeiros, ou None em caso de erro.
    """
    try:
        # 1. Converter os DataFrames para um formato JSON legível para a IA
        financial_data_json = {}
        for statement, df in company_financials.items():
            df_filtered = df.loc[df.groupby('CD_CONTA')['VERSAO'].idxmax()]
            df_filtered = df_filtered.loc[df_filtered.groupby('CD_CONTA')['DT_FIM_EXERC'].idxmax()]
            relevant_data = df_filtered[['DS_CONTA', 'VL_CONTA']].drop_duplicates(subset=['DS_CONTA'])
            financial_data_json[statement] = relevant_data.to_dict(orient='records')

        # 2. Construir o prompt para a IA
        prompt = """
        Você é um analista financeiro sênior, especializado no mercado de ações brasileiro.
        Seu trabalho é analisar dados financeiros e gerar um relatório conciso para investidores.
        A linguagem deve ser formal, direta e clara.

        **Tarefa:**
        Baseado nos dados financeiros em JSON fornecidos, gere uma resposta JSON contendo DUAS chaves:
        1. "report": Uma string com a análise textual fundamentalista, seguindo a estrutura abaixo.
        2. "financial_summary": Um objeto JSON com os valores numéricos exatos para os principais indicadores financeiros extraídos diretamente dos dados.

        **Estrutura do Relatório Textual ("report"):**
        1.  **Visão Geral da Empresa:** Resumo da saúde financeira.
        2.  **Análise do Balanço Patrimonial (BPA e BPP):** Comente sobre ativos, passivos, endividamento e patrimônio líquido.
        3.  **Análise da Demonstração de Resultado (DRE):** Analise receita líquida, lucro bruto e lucro líquido.
        4.  **Conclusão e Pontos de Atenção:** Conclusão final e 2-3 pontos de atenção (positivos ou negativos).

        **Estrutura do Resumo Financeiro ("financial_summary"):**
        Extraia os seguintes valores dos dados e coloque-os neste objeto. Se um valor não estiver disponível, use 0.
        - "Receita Liquida": valor
        - "Lucro Bruto": valor
        - "Lucro Liquido": valor
        - "Ativo Total": valor
        - "Passivo Total": valor
        - "Patrimonio Liquido": valor

        **Dados Financeiros:**
        {financial_data}
        """.format(financial_data=json.dumps(financial_data_json, indent=2, ensure_ascii=False))

        # 3. Chamar a API do Google Gemini com configuração para JSON
        print("Enviando dados para análise do Google Gemini Pro (modo JSON)...")
        model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        
        # Forçar a saída em JSON de forma explícita
        generation_config = GenerationConfig(response_mime_type="application/json")
        
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # 4. Parsear a resposta JSON
        # Com response_mime_type="application/json", response.text já é uma string JSON limpa
        print("--- Gemini Response (JSON mode) ---")
        print(response.text)
        print("-----------------------------------")
        
        analysis_data = json.loads(response.text)
        
        print("Análise recebida e processada do Gemini com sucesso.")
        return analysis_data

    except json.JSONDecodeError as e:
        print(f"Erro de decodificação JSON. A resposta da IA não é um JSON válido: {e}")
        # 'response' pode não existir se o erro for anterior, então usamos locals().get
        raw_response = locals().get("response", None)
        if raw_response:
            print("--- Resposta da IA que causou o erro ---")
            print(raw_response.text)
            print("--------------------------------------")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao gerar a análise com o Gemini: {e}")
        # Capturar e imprimir informações de 'response' se existirem, como 'prompt_feedback'
        response_obj = locals().get("response", None)
        if response_obj and hasattr(response_obj, 'prompt_feedback'):
             print(f"Prompt Feedback: {response_obj.prompt_feedback}")
        return None 