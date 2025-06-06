import matplotlib.pyplot as plt
import seaborn as sns
import io
from typing import Dict
import pandas as pd

def create_financial_summary_chart(summary_data: Dict[str, float]) -> bytes:
    """
    Cria um gráfico de barras com Seaborn a partir do resumo financeiro e o retorna como bytes.

    Args:
        summary_data: Um dicionário com os indicadores financeiros.

    Returns:
        A imagem do gráfico em formato PNG, como um objeto de bytes.
    """
    # Converter para DataFrame, que é o ideal para Seaborn
    df = pd.DataFrame(list(summary_data.items()), columns=['Indicador', 'Valor'])

    # Função para formatar os valores para o gráfico
    def format_value(value):
        if abs(value) >= 1e9:
            return f'R$ {value/1e9:.2f}B'
        elif abs(value) >= 1e6:
            return f'R$ {value/1e6:.2f}M'
        elif abs(value) >= 1e3:
            return f'R$ {value/1e3:.2f}k'
        return f'R$ {value:.2f}'

    # Configurar o estilo do gráfico
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 7))

    # Criar o gráfico de barras horizontal
    barplot = sns.barplot(x='Valor', y='Indicador', data=df, palette='viridis', hue='Indicador', dodge=False, legend=False)

    # Adicionar os rótulos de valor em cada barra
    for index, value in enumerate(df['Valor']):
        barplot.text(value, index, f'  {format_value(value)}', color='black', ha="left", va='center')

    # Configurações do gráfico
    plt.title('Resumo Financeiro da Empresa', fontsize=16, weight='bold')
    plt.xlabel('Valor (R$)', fontsize=12)
    plt.ylabel('') # Ocultar o rótulo do eixo y, pois os indicadores já são claros
    
    # Remover o grid do eixo y e ajustar o eixo x para não mostrar notação científica
    plt.gca().xaxis.grid(True)
    plt.gca().yaxis.grid(False)
    plt.ticklabel_format(style='plain', axis='x')


    plt.tight_layout()

    # Salvar o gráfico em um buffer de memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100) # dpi=100 para boa resolução
    
    # --- Adicionado para teste: Salvar o gráfico em um arquivo local ---
    with open("grafico_gerado.png", "wb") as f:
        f.write(buf.getvalue())
    print(">>> Gráfico de teste salvo como 'grafico_gerado.png' no diretório do backend <<<")
    # -----------------------------------------------------------------

    buf.seek(0)
    
    # Limpar a figura da memória
    plt.close()

    return buf.getvalue() 