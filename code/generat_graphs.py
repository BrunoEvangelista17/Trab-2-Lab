import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- CONFIGURAÇÃO ---
PROCESS_METRICS_FILE = './report_tables/java_repo_metrics.csv'
QUALITY_METRICS_FILE = './consolidated_metrics.csv'
# --- FIM DA CONFIGURAÇÃO ---


def load_and_prepare_data():
    """
    Carrega e prepara os dados, replicando a lógica dos scripts anteriores.
    """
    print("1. Carregando e preparando os dados...")
    try:
        df_process = pd.read_csv(PROCESS_METRICS_FILE)
        df_quality = pd.read_csv(QUALITY_METRICS_FILE)
    except FileNotFoundError as e:
        print(f"--- ERRO: Arquivo não encontrado ---")
        print(f"Verifique se o caminho do arquivo está correto: '{e.filename}'")
        return None

    quality_cols_to_agg = ['cbo', 'dit', 'lcom', 'loc']
    df_quality_agg = df_quality.groupby('repository')[quality_cols_to_agg].median().reset_index()

    df_process['repo_name_only'] = df_process['nameWithOwner'].apply(lambda x: x.split('/')[1])
    df_final = pd.merge(df_process, df_quality_agg, left_on='repo_name_only', right_on='repository', how='inner')

    df_final.rename(columns={
        'popularidade_estrelas': 'popularidade',
        'atividade_releases': 'atividade',
        'maturidade_anos': 'maturidade'
    }, inplace=True)
    
    print("Dados carregados com sucesso.")
    return df_final


def create_activity_violin_plot_log(df):
    """
    Cria um gráfico de violino com escala logarítmica para a RQ03, 
    comparando a distribuição de CBO de forma robusta a outliers.
    """
    if df is None or df.empty:
        print("DataFrame vazio. Não é possível gerar o gráfico.")
        return

    print("2. Criando grupos de atividade (Top 25% vs Bottom 25%)...")
    
    q_bottom = df['atividade'].quantile(0.25)
    q_top = df['atividade'].quantile(0.75)

    df_top = df[df['atividade'] >= q_top].copy()
    df_top['grupo_atividade'] = 'Mais Ativos (Top 25%)'

    df_bottom = df[df['atividade'] <= q_bottom].copy()
    df_bottom['grupo_atividade'] = 'Menos Ativos (Bottom 25%)'

    df_plot = pd.concat([df_top, df_bottom])

    print("3. Gerando o gráfico de violino com escala logarítmica...")

    # --- Plotagem ---
    plt.style.use('seaborn-v0_8-talk')
    fig, ax = plt.subplots(figsize=(14, 10))

    sns.violinplot(
        data=df_plot,
        x='grupo_atividade',
        y='cbo',
        ax=ax,
        palette=['#55a868', '#c44e52'], # Verde, Vermelho
        inner='box',  # <--- MOSTRA UM BOXPLOT DENTRO DO VIOLINO
        cut=0
    )

    # --- A MUDANÇA PRINCIPAL: APLICANDO ESCALA LOGARÍTMICA ---
    # Usamos 'symlog' (log simétrico) para lidar com possíveis valores de CBO = 0
    ax.set_yscale('symlog')
    
    # Títulos e legendas
    ax.set_title('Distribuição de Acoplamento (CBO) por Nível de Atividade', fontsize=20, pad=20)
    ax.set_xlabel('Grupo de Repositórios por Atividade', fontsize=16, labelpad=15)
    ax.set_ylabel('Mediana do CBO (Escala Log)', fontsize=16, labelpad=15)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    plt.tight_layout()
    output_filename = 'rq03_activity_vs_cbo_violinplot_log.png'
    plt.savefig(output_filename, dpi=300)

    print(f"\n--- SUCESSO! ---")
    print(f"Gráfico de violino aprimorado salvo como: '{output_filename}'")


if __name__ == "__main__":
    prepared_data = load_and_prepare_data()
    if prepared_data is not None:
        create_activity_violin_plot_log(prepared_data)