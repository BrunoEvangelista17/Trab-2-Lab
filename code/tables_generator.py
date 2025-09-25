import pandas as pd

def gerar_tabela_resumo():
    """
    Carrega o dataset, calcula as médias gerais e por grupo para cada RQ,
    e gera uma tabela de resumo em formato CSV e LaTeX.
    """
    try:
        # Carrega o dataset a partir do ficheiro CSV local
        filepath = './final_analysis_dataset.csv'
        print(f"A carregar dados de '{filepath}'...")
        df = pd.read_csv(filepath)

        # Verifica se a coluna 'total_loc' existe
        if 'total_loc' not in df.columns:
            print(f"AVISO: A coluna 'total_loc' não foi encontrada. A análise da RQ04 será ignorada.")

        # --- 1. CÁLCULO DAS MÉDIAS GERAIS ---
        metricas_qualidade = ['cbo_median', 'dit_median', 'lcom_median']
        metricas_processo = ['popularidade_estrelas', 'maturidade_anos', 'atividade_releases']
        if 'total_loc' in df.columns:
            metricas_processo.append('total_loc')
            
        # Calcula a média geral para todas as métricas relevantes
        media_geral = df[metricas_qualidade + metricas_processo].mean().to_frame().T
        media_geral.index = pd.MultiIndex.from_tuples([('Análise Geral', 'Todos')])
        
        # Lista para armazenar os resultados
        all_summaries = [media_geral]

        # --- 2. CÁLCULO DAS MÉDIAS POR GRUPO (RQs) ---
        
        # Dicionário para configurar as análises de cada RQ
        rq_configs = {
            'Maturidade (RQ02)': {'col': 'maturidade_anos', 'labels': ['Jovens', 'Intermediários', 'Maduros']},
            'Atividade (RQ03)': {'col': 'atividade_releases', 'labels': ['Baixa', 'Moderada', 'Alta']},
        }
        if 'total_loc' in df.columns:
            rq_configs['Tamanho (RQ04)'] = {'col': 'total_loc', 'labels': ['Pequenos', 'Médios', 'Grandes']}

        for rq_name, config in rq_configs.items():
            col = config['col']
            labels = config['labels']
            
            # Cria os grupos usando tercis (quantis 0.33 e 0.66)
            quantis = df[col].quantile([0.33, 0.66]).values
            bins = [-float('inf'), quantis[0], quantis[1], float('inf')]
            
            df['grupo'] = pd.cut(df[col], bins=bins, labels=labels)
            
            # Calcula a média das métricas de qualidade para cada grupo
            resumo_grupo = df.groupby('grupo')[metricas_qualidade].mean()
            resumo_grupo.index = pd.MultiIndex.from_product([[rq_name], resumo_grupo.index])
            all_summaries.append(resumo_grupo)

        # --- 3. MONTAGEM E EXPORTAÇÃO DA TABELA FINAL ---
        
        # Concatena todos os resumos numa única tabela
        tabela_final = pd.concat(all_summaries)

        # Renomeia as colunas para um formato mais legível
        tabela_final.rename(columns={
            'cbo_median': 'CBO (Mediana)',
            'dit_median': 'DIT (Mediana)',
            'lcom_median': 'LCOM (Mediana)',
            'popularidade_estrelas': 'Popularidade',
            'maturidade_anos': 'Maturidade',
            'atividade_releases': 'Atividade',
            'total_loc': 'LOC Total'
        }, inplace=True)
        
        # Arredonda os valores para 2 casas decimais
        tabela_final = tabela_final.round(2)
        
        print("\n" + "="*80)
        print("Tabela de Resumo Geral Gerada:")
        print(tabela_final.to_string())
        print("="*80)

        # Guarda a tabela em CSV
        csv_output_path = 'tabela_resumo_geral.csv'
        tabela_final.to_csv(csv_output_path)
        print(f"\nTabela guardada em formato CSV em: '{csv_output_path}'")
        
        # Guarda a tabela em formato LaTeX
        latex_output_path = 'tabela_resumo_geral.tex'
        tabela_final.to_latex(latex_output_path, booktabs=True, multirow=True, longtable=False)
        print(f"Tabela guardada em formato LaTeX em: '{latex_output_path}'")
        
        print("\nAnálise concluída com sucesso!")

    except FileNotFoundError:
        print(f"ERRO: O ficheiro '{filepath}' não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    gerar_tabela_resumo()
