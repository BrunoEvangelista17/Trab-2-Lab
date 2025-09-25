import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define um estilo visual mais agradável para os gráficos
sns.set_theme(style="whitegrid")

def gerar_grafico_rq4():
    """
    Gera um gráfico de barras com barras de erro 1x3 para analisar a relação entre
    o tamanho do repositório (LOC) e as métricas de qualidade do código.
    """
    try:
        # Carrega o dataset a partir do ficheiro CSV local
        filepath = './final_analysis_dataset.csv'
        print(f"A carregar dados de '{filepath}'...")
        df = pd.read_csv(filepath)

        # Verifica se a coluna 'total_loc' existe
        if 'total_loc' not in df.columns:
            print(f"ERRO: A coluna 'total_loc' é necessária para a RQ04 e não foi encontrada em '{filepath}'.")
            return

        # --- FILTRAGEM DE OUTLIERS DAS MÉTRICAS DE QUALIDADE ---
        print(f"Número original de repositórios: {len(df)}")
        cbo_limite = df['cbo_median'].quantile(0.95)
        dit_limite = df['dit_median'].quantile(0.95)
        lcom_limite = df['lcom_median'].quantile(0.95)

        df_filtrado = df[
            (df['cbo_median'] < cbo_limite) &
            (df['dit_median'] < dit_limite) &
            (df['lcom_median'] < lcom_limite)
        ].copy()
        print(f"Número de repositórios após remover 5% dos outliers de qualidade: {len(df_filtrado)}")
        # --- FIM DA FILTRAGEM ---

        # --- CRIAÇÃO DOS GRUPOS DE TAMANHO ---
        # Divide os repositórios em 3 grupos com base no LOC total
        quantis = df_filtrado['total_loc'].quantile([0.33, 0.66]).values
        df_filtrado['grupo_tamanho'] = pd.cut(
            df_filtrado['total_loc'],
            bins=[0, quantis[0], quantis[1], df_filtrado['total_loc'].max()],
            labels=['Pequenos', 'Médios', 'Grandes'],
            include_lowest=True
        )
        print("\nRepositorios categorizados por tamanho (LOC).")
        
        # Renomeia as colunas para os gráficos ficarem mais legíveis
        df_filtrado.rename(columns={
            'cbo_median': 'CBO (Mediana)',
            'dit_median': 'DIT (Mediana)',
            'lcom_median': 'LCOM (Mediana)'
        }, inplace=True)

        print("A gerar gráfico para RQ04...")

        # --- GRÁFICO DE BARRAS PARA RQ04 ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('RQ04: Relação entre Tamanho do Repositório (LOC) e Qualidade do Código', fontsize=16, weight='bold')

        quality_metrics = ['CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)']
        
        for i, metric in enumerate(quality_metrics):
            sns.barplot(
                x='grupo_tamanho',
                y=metric,
                data=df_filtrado,
                ax=axes[i],
                palette='magma',
                order=['Pequenos', 'Médios', 'Grandes'], # Garante a ordem correta
                capsize=0.1 # Adiciona "caps" às barras de erro
            )
            axes[i].set_title(f'Média de {metric} por Tamanho')
            axes[i].set_xlabel('Grupo de Tamanho')
            axes[i].set_ylabel('Valor Médio da Mediana')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('rq04_barplot.png')
        plt.close()
        print("- Ficheiro 'rq04_barplot.png' gerado com sucesso.")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{filepath}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_grafico_rq4()

