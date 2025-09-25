import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define um estilo visual mais agradável para os gráficos
sns.set_theme(style="whitegrid")

def gerar_grafico_rq1():
    """
    Gera um gráfico de dispersão 1x3 para analisar a relação entre
    a popularidade e as métricas de qualidade de código.
    """
    try:
        # Carrega o dataset a partir do ficheiro CSV local
        filepath = './final_analysis_dataset.csv'
        print(f"A carregar dados de '{filepath}'...")
        df = pd.read_csv(filepath)

        # --- FILTRAGEM DE OUTLIERS DAS MÉTRICAS DE QUALIDADE ---
        print(f"Número original de repositórios: {len(df)}")
        # Calcula o 95º percentil para cada métrica de qualidade para remover os 5% de outliers superiores
        cbo_limite = df['cbo_median'].quantile(0.95)
        dit_limite = df['dit_median'].quantile(0.95)
        lcom_limite = df['lcom_median'].quantile(0.95)

        df_filtrado = df[
            (df['cbo_median'] < cbo_limite) &
            (df['dit_median'] < dit_limite) &
            (df['lcom_median'] < lcom_limite)
        ].copy()
        print(f"Número de repositórios após remover os 5% de outliers de qualidade (CBO, DIT, LCOM): {len(df_filtrado)}")
        # --- FIM DA FILTRAGEM ---

        # Renomeia as colunas para os gráficos ficarem mais legíveis
        df_filtrado.rename(columns={
            'popularidade_estrelas': 'Popularidade (Estrelas)',
            'cbo_median': 'CBO (Mediana)',
            'dit_median': 'DIT (Mediana)',
            'lcom_median': 'LCOM (Mediana)'
        }, inplace=True)

        print("\nDados carregados e filtrados com sucesso. A gerar gráfico para RQ01...")

        # --- GRÁFICO DE DISPERSÃO PARA RQ01 ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
        fig.suptitle('RQ01: Relação entre Popularidade e Qualidade do Código (Excluindo 5% de Outliers de Qualidade)', fontsize=16, weight='bold')

        quality_metrics = ['CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)']
        colors = ['#377eb8', '#4daf4a', '#e41a1c'] # Azul, Verde, Vermelho

        for i, quality_metric in enumerate(quality_metrics):
            sns.regplot(
                x='Popularidade (Estrelas)',
                y=quality_metric,
                data=df_filtrado,
                ax=axes[i],
                scatter_kws={'alpha': 0.5, 'color': colors[i]},
                line_kws={'color': 'black', 'linestyle': '--'}
            )
            axes[i].set_title(f'Popularidade vs. {quality_metric}')
            
            # Adiciona o valor da correlação de Pearson (r) no gráfico
            corr_value = df_filtrado['Popularidade (Estrelas)'].corr(df_filtrado[quality_metric])
            axes[i].text(0.05, 0.95, f'r = {corr_value:.2f}',
                         transform=axes[i].transAxes,
                         fontsize=12,
                         verticalalignment='top',
                         bbox=dict(boxstyle='round,pad=0.5', fc='wheat', alpha=0.7))

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig('rq01_dispersao.png')
        plt.close()
        print("- Ficheiro 'rq01_dispersao.png' gerado com sucesso.")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{filepath}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_grafico_rq1()

