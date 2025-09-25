import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define um estilo visual mais agradável para os gráficos
sns.set_theme(style="whitegrid")

def gerar_grafico_rq2():
    """
    Gera um gráfico de box plot 1x3 para analisar a relação entre
    a maturidade do repositório e as métricas de qualidade do código.
    """
    try:
        # Carrega o dataset a partir do ficheiro CSV local
        filepath = './final_analysis_dataset.csv'
        print(f"A carregar dados de '{filepath}'...")
        df = pd.read_csv(filepath)

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

        # --- CRIAÇÃO DOS GRUPOS DE MATURIDADE ---
        # Divide os repositórios em 3 grupos (tercis) com base na idade
        quantis = df_filtrado['maturidade_anos'].quantile([0.33, 0.66]).values
        df_filtrado['grupo_maturidade'] = pd.cut(
            df_filtrado['maturidade_anos'],
            bins=[0, quantis[0], quantis[1], df_filtrado['maturidade_anos'].max()],
            labels=['Jovens', 'Intermediários', 'Maduros'],
            include_lowest=True
        )
        print("\nRepositorios categorizados por maturidade.")
        
        # Renomeia as colunas para os gráficos ficarem mais legíveis
        df_filtrado.rename(columns={
            'cbo_median': 'CBO (Mediana)',
            'dit_median': 'DIT (Mediana)',
            'lcom_median': 'LCOM (Mediana)'
        }, inplace=True)

        print("A gerar gráfico para RQ02...")

        # --- GRÁFICO DE BOX PLOT PARA RQ02 ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('RQ02: Relação entre Maturidade e Qualidade do Código', fontsize=16, weight='bold')

        quality_metrics = ['CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)']
        
        for i, metric in enumerate(quality_metrics):
            sns.boxplot(
                x='grupo_maturidade',
                y=metric,
                data=df_filtrado,
                ax=axes[i],
                palette='viridis',
                order=['Jovens', 'Intermediários', 'Maduros'] # Garante a ordem correta
            )
            axes[i].set_title(f'Distribuição de {metric} por Maturidade')
            axes[i].set_xlabel('Grupo de Maturidade')
            axes[i].set_ylabel('Valor da Mediana')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('rq02_boxplot.png')
        plt.close()
        print("- Ficheiro 'rq02_boxplot.png' gerado com sucesso.")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{filepath}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_grafico_rq2()
