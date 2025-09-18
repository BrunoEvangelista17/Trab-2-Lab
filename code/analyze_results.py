import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import numpy as np

# --- CONFIGURAÇÃO ---
# Verifique se os nomes dos ficheiros e caminhos estão corretos.
PROCESS_METRICS_FILE = 'java_repo_metrics.csv'
QUALITY_METRICS_FILE = r'C:\Users\TI04\ResultadosCK\consolidated_metrics.csv'
# --- FIM DA CONFIGURAÇÃO ---


def analyze_repository_data():
    """
    Carrega, processa e analisa os dados dos repositórios para responder
    às questões de pesquisa do laboratório, usando os nomes de coluna corretos.
    """
    print("🚀 Iniciando a análise final dos dados...")

    # --- 1. CARREGAR OS DADOS ---
    try:
        df_process = pd.read_csv(PROCESS_METRICS_FILE)
        df_quality = pd.read_csv(QUALITY_METRICS_FILE)
    except FileNotFoundError as e:
        print(f"❌ ERRO: Ficheiro não encontrado - {e}")
        print("Verifique se os ficheiros CSV estão nos caminhos corretos na configuração do script.")
        return

    print("✅ Ficheiros carregados com sucesso.")

    # --- 2. PREPARAR E AGREGAR OS DADOS ---
    print("🔄 Agregando as métricas de qualidade por repositório (usando a mediana)...")
    
    # Colunas de qualidade a serem agregadas, conforme o laboratório
    quality_cols_to_agg = ['cbo', 'dit', 'lcom', 'loc']
    
    # Verifica se as colunas necessárias existem
    for col in quality_cols_to_agg + ['repository']:
        if col not in df_quality.columns:
            print(f"❌ ERRO: A coluna '{col}' não foi encontrada no ficheiro de métricas de qualidade.")
            return

    # Agrega usando a mediana para robustez
    df_quality_agg = df_quality.groupby('repository')[quality_cols_to_agg].median().reset_index()

    # --- CORREÇÃO DA LÓGICA DE JUNÇÃO (MERGE) ---
    # Extrai o nome do repositório da coluna 'nameWithOwner' para permitir a junção correta
    df_process['repo_name_only'] = df_process['nameWithOwner'].apply(lambda x: x.split('/')[1])
    
    df_final = pd.merge(df_process, df_quality_agg, left_on='repo_name_only', right_on='repository', how='inner')

    # Renomeia as colunas de processo para corresponder às RQs
    df_final.rename(columns={
        'popularidade_estrelas': 'popularidade',
        'atividade_releases': 'atividade',
        'maturidade_anos': 'maturidade'
    }, inplace=True)

    print(f"📊 Análise baseada em {len(df_final)} repositórios com dados completos de processo e qualidade.")
    
    # --- 3. ANÁLISE ESTATÍSTICA ---
    metrics_to_analyze = ['popularidade', 'maturidade', 'atividade', 'loc', 'cbo', 'dit', 'lcom']
    df_analysis = df_final[metrics_to_analyze].copy()
    df_analysis.dropna(inplace=True)

    print("\n--- 📊 ESTATÍSTICAS DESCRITIVAS (Média, Mediana, Desvio Padrão) ---")
    print(df_analysis.describe().loc[['mean', '50%', 'std']].rename(index={'50%': 'median'}))

    # --- 4. RESPONDER ÀS QUESTÕES DE PESQUISA (RQs) ---
    print("\n--- 📝 ANÁLISE DAS QUESTÕES DE PESQUISA (Correlação de Spearman) ---")
    
    quality_metrics = ['cbo', 'dit', 'lcom']

    # RQ01: Popularidade vs. Qualidade
    print("\n[RQ01] Relação entre POPULARIDADE e Qualidade:")
    for q_metric in quality_metrics:
        corr, p_value = spearmanr(df_analysis['popularidade'], df_analysis[q_metric])
        print(f"  - popularidade vs {q_metric}: Correlação={corr:.3f}, P-valor={p_value:.3f}")

    # RQ02: Maturidade vs. Qualidade
    print("\n[RQ02] Relação entre MATURIDADE e Qualidade:")
    for q_metric in quality_metrics:
        corr, p_value = spearmanr(df_analysis['maturidade'], df_analysis[q_metric])
        print(f"  - maturidade vs {q_metric}: Correlação={corr:.3f}, P-valor={p_value:.3f}")

    # RQ03: Atividade vs. Qualidade
    print("\n[RQ03] Relação entre ATIVIDADE (releases) e Qualidade:")
    for q_metric in quality_metrics:
        corr, p_value = spearmanr(df_analysis['atividade'], df_analysis[q_metric])
        print(f"  - atividade vs {q_metric}: Correlação={corr:.3f}, P-valor={p_value:.3f}")
        
    # RQ04: Tamanho vs. Qualidade
    print("\n[RQ04] Relação entre TAMANHO (LOC) e Qualidade:")
    for q_metric in quality_metrics:
        corr, p_value = spearmanr(df_analysis['loc'], df_analysis[q_metric])
        print(f"  - loc vs {q_metric}: Correlação={corr:.3f}, P-valor={p_value:.3f}")

    # --- 5. GERAR GRÁFICO (BÓNUS) ---
    print("\n--- 🎁 GERANDO GRÁFICO DE CORRELAÇÃO (BÓNUS) ---")
    
    try:
        correlation_matrix = df_analysis.corr(method='spearman')
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5)
        plt.title('Mapa de Calor da Correlação de Spearman entre Métricas', fontsize=16)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        output_filename = "correlation_heatmap.png"
        plt.savefig(output_filename, bbox_inches='tight', dpi=300)
        
        print(f"\n✅ SUCESSO! Mapa de calor salvo como '{output_filename}'.")
        print("Este gráfico pode ser usado diretamente no seu relatório final.")

    except Exception as e:
        print(f"\n⚠️ AVISO: Não foi possível gerar o mapa de calor. Erro: {e}")

    print("\nAnálise concluída.")


if __name__ == "__main__":
    analyze_repository_data()