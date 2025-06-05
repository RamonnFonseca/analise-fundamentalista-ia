# Lógica de negócios para interagir com o modelo de IA.
# - Enviar dados processados dos documentos CVM para a IA.
# - Receber e interpretar as análises da IA.
# - Formatar a saída da IA para ser usada na geração de relatórios. 

import json
import google.generativeai as genai
from app.core.config import settings
from typing import Dict
import pandas as pd

# Configura a biblioteca do Google com a chave de API das nossas configurações
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_financial_analysis(company_financials: Dict[str, pd.DataFrame]) -> str | None:
    """
    Usa o Google Gemini Pro para gerar uma análise financeira a partir dos dados da empresa.

    Args:
        company_financials: Um dicionário onde as chaves são os nomes das demonstrações
                            (ex: "BPA", "DRE") e os valores são DataFrames do pandas.

    Returns:
        Uma string com a análise gerada pela IA, ou None em caso de erro.
    """
    try:
        # 1. Converter os DataFrames para um formato JSON mais compacto e legível para a IA
        financial_data_json = {}
        for statement, df in company_financials.items():
            df_filtered = df.loc[df.groupby('CD_CONTA')['VERSAO'].idxmax()]
            df_filtered = df_filtered.loc[df_filtered.groupby('CD_CONTA')['DT_FIM_EXERC'].idxmax()]
            relevant_data = df_filtered[['DS_CONTA', 'VL_CONTA']].drop_duplicates(subset=['DS_CONTA'])
            financial_data_json[statement] = relevant_data.to_dict(orient='records')

        # 2. Construir o prompt para a IA
        prompt = """
        Você é um analista financeiro sênior, especializado no mercado de ações brasileiro, trabalhando para um grande banco de investimentos como o BTG Pactual ou a XP Inc.
        Seu objetivo é gerar um relatório de análise fundamentalista conciso, profissional e com insights valiosos para um cliente investidor.
        A linguagem deve ser formal, direta e clara, como a usada em relatórios de mercado.
        Baseado nos dados financeiros fornecidos em formato JSON a seguir, gere uma análise que cubra os seguintes pontos:
        1.  **Visão Geral da Empresa:** Com base nos totais do balanço e resultado, faça um breve resumo da saúde financeira da empresa no período.
        2.  **Análise do Balanço Patrimonial (BPA e BPP):** Comente sobre a estrutura de ativos e passivos. Destaque pontos importantes como níveis de caixa, endividamento (curto e longo prazo) e patrimônio líquido.
        3.  **Análise da Demonstração de Resultado (DRE):** Analise a receita líquida, o lucro bruto e o lucro líquido. Comente sobre as margens (se possível calcular) e a eficiência operacional.
        4.  **Conclusão e Pontos de Atenção:** Forneça um parágrafo final com sua conclusão sobre a situação da empresa e aponte 2-3 pontos de atenção (positivos ou negativos) que um investidor deve observar nos próximos trimestres.

        Não inclua saudações ou despedidas. Vá direto ao ponto. A resposta deve ser apenas o texto da análise.

        Dados Financeiros:
        {financial_data}
        """.format(financial_data=json.dumps(financial_data_json, indent=2, ensure_ascii=False))

        # 3. Chamar a API do Google Gemini
        print("Enviando dados para análise do Google Gemini Pro...")
        model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06')
        response = model.generate_content(prompt)
        
        analysis_content = response.text
        print("Análise recebida do Gemini com sucesso.")
        return analysis_content

    except Exception as e:
        print(f"Ocorreu um erro ao gerar a análise com o Gemini: {e}")
        return None 