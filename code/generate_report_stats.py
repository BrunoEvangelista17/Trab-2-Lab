import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
import numpy as np
import os

# --- CONFIGURAÇÃO ---
PROCESS_METRICS_FILE = 'java_repo_metrics.csv'
QUALITY_METRICS_FILE = r'C:\Users\TI04\ResultadosCK\consolidated_metrics.csv'
OUTPUT_DIR = 'report_tables' 
# --- FIM DA CONFIGURAÇÃO ---


def generate_latex_report_data():
    """
    Executa uma análise estatística completa, gera novos gráficos e guarda
    todas as tabelas e dados para o relatório LaTeX.
    """
    print("🚀 Iniciando a geração de estatísticas e gráficos para o relatório...")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Diretório '{OUTPUT_DIR}' criado.")

    # --- 1. CARREGAR E PREPARAR OS DADOS ---
    df_process = pd.read_csv(PROCESS_METRICS_FILE)
    df_quality = pd.read_csv(QUALITY_METRICS_FILE)
    print("✅ Ficheiros carregados.")

    df_quality_agg = df_quality.groupby('repository')[['cbo', 'dit', 'lcom', 'loc']].median().reset_index()
    df_process['repo_name_only'] = df_process['nameWithOwner'].apply(lambda x: x.split('/')[1])
    df_final = pd.merge(df_process, df_quality_agg, left_on='repo_name_only', right_on='repository', how='inner')
    df_final.rename(columns={
        'popularidade_estrelas': 'popularidade',
        'atividade_releases': 'atividade',
        'maturidade_anos': 'maturidade'
    }, inplace=True)
    
    metrics_to_analyze = ['popularidade', 'maturidade', 'atividade', 'loc', 'cbo', 'dit', 'lcom']
    df_analysis = df_final[metrics_to_analyze].copy().dropna()
    print(f"📊 Análise baseada em {len(df_analysis)} repositórios.")

    # --- 2. GERAR NOVOS DADOS E GRÁFICOS ---

    # Dados para Gráfico de Pizza (Maturidade)
    print("📝 Gerando dados para o Gráfico de Pizza...")
    age_bins = [0, df_analysis['maturidade'].quantile(0.33), df_analysis['maturidade'].quantile(0.66), np.inf]
    age_labels = ['Jovem', 'Intermédio', 'Maduro']
    df_analysis['maturidade_categoria'] = pd.cut(df_analysis['maturidade'], bins=age_bins, labels=age_labels, right=False)
    maturity_distribution = df_analysis['maturidade_categoria'].value_counts()
    maturity_distribution.to_csv(os.path.join(OUTPUT_DIR, 'table_maturity_pie_distribution.csv'), header=['count'], index_label='category')

    # Gerar Box Plot (Maturidade vs CBO) como imagem
    print("📊 Gerando Gráfico Box Plot (imagem)...")
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='maturidade_categoria', y='cbo', data=df_analysis, order=age_labels)
    plt.title('Distribuição do Acoplamento (CBO) por Maturidade do Repositório', fontsize=14)
    plt.xlabel('Categoria de Maturidade', fontsize=12)
    plt.ylabel('Acoplamento (CBO)', fontsize=12)
    plt.savefig('maturity_vs_cbo_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close() # Fecha a figura para não a mostrar no ecrã

    # Dados para Gráfico de Dispersão (LOC vs CBO)
    print("📝 Gerando dados para o Gráfico de Dispersão...")
    # Usar uma amostra para o gráfico não ficar muito pesado no LaTeX
    scatter_sample = df_analysis[['loc', 'cbo']].sample(n=min(len(df_analysis), 400), random_state=42)
    scatter_sample.to_csv(os.path.join(OUTPUT_DIR, 'scatter_loc_vs_cbo.csv'), index=False)
    
    # --- 3. GERAR TABELAS DE ESTATÍSTICAS (como antes) ---
    print("📝 Gerando tabelas de estatísticas...")
    desc_stats = df_analysis[metrics_to_analyze].describe().loc[['mean', '50%', 'std', 'min', 'max']].rename(index={'50%': 'median'})
    desc_stats.to_csv(os.path.join(OUTPUT_DIR, 'table1_descriptive_stats.csv'), float_format='%.2f')

    correlation_matrix = df_analysis[metrics_to_analyze].corr(method='spearman')
    correlation_matrix.to_csv(os.path.join(OUTPUT_DIR, 'table2_correlation_matrix.csv'), float_format='%.3f')
    
    print("\n" + "="*80)
    print("✅ SUCESSO! Todas as tabelas e gráficos auxiliares foram gerados.")
    print("Pode agora compilar o ficheiro LaTeX atualizado.")
    print("="*80)

if __name__ == "__main__":
    generate_latex_report_data()