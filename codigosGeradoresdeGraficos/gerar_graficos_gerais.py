import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define um estilo visual mais agradável para os gráficos
sns.set_theme(style="whitegrid")

def gerar_graficos_analise_geral():
    """
    Carrega o dataset, realiza uma análise estatística geral e gera
    gráficos de distribuição, boxplots e um mapa de calor.
    """
    try:
        # Carrega o dataset a partir do ficheiro CSV local
        filepath = './final_analysis_dataset.csv'
        print(f"A carregar dados de '{filepath}'...")
        df = pd.read_csv(filepath)
        
        # --- FILTRAGEM DE OUTLIERS EXTREMOS ---
        print(f"Número original de repositórios: {len(df)}")
        
        # Define os quantis para remover os outliers mais extremos (o 1% superior)
        popularidade_limite = df['popularidade_estrelas'].quantile(0.99)
        atividade_limite = df['atividade_releases'].quantile(0.99)
        lcom_limite = df['lcom_median'].quantile(0.99)

        # Constrói a lista de condições para a filtragem
        condicoes = [
            (df['popularidade_estrelas'] < popularidade_limite),
            (df['atividade_releases'] < atividade_limite),
            (df['lcom_median'] < lcom_limite)
        ]
        
        # Verifica se a coluna 'total_loc' existe para a incluir na filtragem
        if 'total_loc' in df.columns:
            loc_limite = df['total_loc'].quantile(0.99)
            condicoes.append(df['total_loc'] < loc_limite)
        else:
            print("Aviso: Coluna 'total_loc' não encontrada. A filtragem continuará sem ela.")

        # Aplica todas as condições de uma vez
        df_filtrado = df[pd.concat(condicoes, axis=1).all(axis=1)].copy()
        
        print(f"Número de repositórios após remover outliers: {len(df_filtrado)}")
        print(f"Foram removidos {len(df) - len(df_filtrado)} repositórios.")
        # --- FIM DA FILTRAGEM ---

        # Renomeia as colunas para os gráficos ficarem mais legíveis
        df_filtrado.rename(columns={
            'popularidade_estrelas': 'Popularidade (Estrelas)',
            'maturidade_anos': 'Maturidade (Anos)',
            'atividade_releases': 'Atividade (Releases)',
            'total_loc': 'Tamanho (LOC Total)',
            'cbo_median': 'CBO (Mediana)',
            'dit_median': 'DIT (Mediana)',
            'lcom_median': 'LCOM (Mediana)'
        }, inplace=True)

        print("\nDados carregados e filtrados com sucesso. A gerar gráficos...")

        # --- 1. GRÁFICO: DISTRIBUIÇÃO DAS MÉTRICAS DE PROCESSO E TAMANHO ---
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Distribuição das Métricas de Processo e Tamanho (Sem Outliers Extremos)', fontsize=16, weight='bold')
        
        sns.histplot(df_filtrado['Popularidade (Estrelas)'], kde=True, ax=axes[0, 0], color='skyblue')
        axes[0, 0].set_title('Popularidade dos Repositórios')
        
        sns.histplot(df_filtrado['Maturidade (Anos)'], kde=True, ax=axes[0, 1], color='olive')
        axes[0, 1].set_title('Maturidade dos Repositórios')
        
        sns.histplot(df_filtrado['Atividade (Releases)'], kde=True, ax=axes[1, 0], color='gold')
        axes[1, 0].set_title('Atividade dos Repositórios')

        # Adiciona o gráfico de distribuição para LOC Total se a coluna existir
        if 'Tamanho (LOC Total)' in df_filtrado.columns:
            sns.histplot(df_filtrado['Tamanho (LOC Total)'], kde=True, ax=axes[1, 1], color='salmon')
            axes[1, 1].set_title('Tamanho dos Repositórios (LOC)')
        else:
            # Se a coluna não existir, desativa o eixo para um visual limpo
            axes[1, 1].axis('off')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('distribuicao_metricas_processo_e_tamanho.png')
        plt.close()
        print("- Ficheiro 'distribuicao_metricas_processo_e_tamanho.png' gerado.")

        # --- 2. GRÁFICO: DISTRIBUIÇÃO DAS MÉTRICAS DE QUALIDADE ---
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        fig.suptitle('Distribuição das Métricas de Qualidade (Medianas)', fontsize=16, weight='bold')

        sns.histplot(df_filtrado['CBO (Mediana)'], kde=True, ax=axes[0], color='teal')
        axes[0].set_title('Distribuição do CBO')

        sns.histplot(df_filtrado['DIT (Mediana)'], kde=True, ax=axes[1], color='darkorange')
        axes[1].set_title('Distribuição do DIT')

        sns.histplot(df_filtrado['LCOM (Mediana)'], kde=True, ax=axes[2], color='darkviolet')
        axes[2].set_title('Distribuição do LCOM')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('distribuicao_metricas_qualidade.png')
        plt.close()
        print("- Ficheiro 'distribuicao_metricas_qualidade.png' gerado.")

        # --- 3. GRÁFICO: BOXPLOTS DAS MÉTRICAS DE QUALIDADE ---
        plt.figure(figsize=(12, 7))
        quality_metrics = df_filtrado[['CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)']]
        sns.boxplot(data=quality_metrics, palette="Set2")
        plt.title('Dispersão das Métricas de Qualidade', fontsize=16, weight='bold')
        plt.ylabel('Valores da Mediana')
        plt.savefig('boxplots_metricas_qualidade.png')
        plt.close()
        print("- Ficheiro 'boxplots_metricas_qualidade.png' gerado.")

        # --- 4. GRÁFICO: MATRIZ DE CORRELAÇÃO ---
        cols_interesse = [
            'Popularidade (Estrelas)', 'Maturidade (Anos)', 'Atividade (Releases)',
            'CBO (Mediana)', 'DIT (Mediana)', 'LCOM (Mediana)'
        ]
        if 'Tamanho (LOC Total)' in df_filtrado.columns:
            cols_interesse.insert(3, 'Tamanho (LOC Total)') # Insere o LOC na lista

        plt.figure(figsize=(10, 8))
        correlation_matrix = df_filtrado[cols_interesse].corr(method='pearson')
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title('Matriz de Correlação de Pearson (Sem Outliers Extremos)', fontsize=16, weight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig('correlation_heatmap_geral.png')
        plt.close()
        print("- Ficheiro 'correlation_heatmap_geral.png' gerado.")
        
        print("\nAnálise concluída com sucesso!")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{filepath}' não foi encontrado.")
        print("Por favor, certifique-se de que o ficheiro está no mesmo diretório que o script.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_graficos_analise_geral()

