import os
import pandas as pd

# --- CONFIGURE AQUI ---
# Confirme se este é o caminho para a pasta que contém todos os seus
# ficheiros .csv (ex: vhrclass.csv, vespaclass.csv, etc.).
PATH_TO_OUTPUT_FOLDER = r"C:\Users\TI04\ResultadosCK"
# --- FIM DA CONFIGURAÇÃO ---


def consolidate_and_summarize_metrics():
    """
    Procura por ficheiros que terminam com 'class.csv' numa única pasta,
    extrai o nome do repositório, consolida todos os resultados e calcula
    métricas de resumo (soma de LOC, média e mediana de CBO, DIT, LCOM)
    para cada repositório.
    """
    all_metrics_dfs = []
    summary_data = []
    
    print(f"Iniciando a busca por ficheiros que terminam com 'class.csv' em: '{PATH_TO_OUTPUT_FOLDER}'...")

    if not os.path.exists(PATH_TO_OUTPUT_FOLDER):
        print(f"ERRO: O diretório especificado não foi encontrado: '{PATH_TO_OUTPUT_FOLDER}'")
        return

    # Lista todos os ficheiros na pasta e filtra aqueles que terminam com "class.csv"
    all_files_in_dir = os.listdir(PATH_TO_OUTPUT_FOLDER)
    class_files_to_process = [f for f in all_files_in_dir if f.endswith("class.csv")]

    if not class_files_to_process:
        print("ERRO: Nenhum ficheiro terminado em 'class.csv' foi encontrado no diretório.")
        return
        
    print(f"Encontrados {len(class_files_to_process)} ficheiros de classes para processar...")

    for filename in class_files_to_process:
        file_path = os.path.join(PATH_TO_OUTPUT_FOLDER, filename)
        # Extrai o nome do repositório, removendo 'class.csv' do final do nome do ficheiro
        repo_name = filename.replace("class.csv", "")

        try:
            df = pd.read_csv(file_path)
            
            if df.empty:
                print(f"  - Aviso: Ficheiro '{filename}' está vazio. A ignorar.")
                continue
            
            # Calcula as métricas de resumo para o repositório
            summary = {'repository': repo_name}
            metric_cols = ['cbo', 'dit', 'lcom', 'loc']
            
            if all(col in df.columns for col in metric_cols):
                summary['total_loc'] = df['loc'].sum()
                summary['cbo_mean'] = df['cbo'].mean()
                summary['cbo_median'] = df['cbo'].median()
                summary['cbo_std'] = df['cbo'].std()
                summary['dit_mean'] = df['dit'].mean()
                summary['dit_median'] = df['dit'].median()
                summary['dit_std'] = df['dit'].std()
                summary['lcom_mean'] = df['lcom'].mean()
                summary['lcom_median'] = df['lcom'].median()
                summary['lcom_std'] = df['lcom'].std()
                summary_data.append(summary)
            else:
                print(f"  - Aviso: Uma ou mais colunas de métricas (cbo, dit, lcom, loc) não foram encontradas em '{filename}'. A ignorar para o resumo.")

            # Adiciona a coluna do repositório para a consolidação geral
            df['repository'] = repo_name
            all_metrics_dfs.append(df)
            print(f"  - Processado: {filename} ({len(df)} linhas)")

        except Exception as e:
            print(f"  - ERRO: Não foi possível ler ou processar o ficheiro '{filename}'. Erro: {e}")

    # Consolida todas as métricas de todas as classes (funcionalidade original)
    if all_metrics_dfs:
        print(f"\nConsolidando os dados de {len(all_metrics_dfs)} relatórios...")
        
        final_df = pd.concat(all_metrics_dfs, ignore_index=True)
        final_output_path = os.path.join(PATH_TO_OUTPUT_FOLDER, "consolidated_metrics.csv")
        
        final_df.to_csv(final_output_path, index=False)
        
        print("\n" + "="*80)
        print("SUCESSO! (Consolidação Geral)")
        print(f"Os resultados foram consolidados em:\n'{final_output_path}'")
        print(f"Total de classes no relatório: {len(final_df)}")
        print("="*80)
    else:
        print("\nAVISO: Nenhum dado foi consolidado para o relatório geral.")

    # Cria e guarda o ficheiro de resumo de métricas
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        summary_output_path = os.path.join(PATH_TO_OUTPUT_FOLDER, "summary_metrics_por_repositorio.csv")
        summary_df.to_csv(summary_output_path, index=False)
        
        print("\n" + "="*80)
        print("SUCESSO! (Resumo de Métricas por Repositório)")
        print(f"O resumo de métricas por repositório foi guardado em:\n'{summary_output_path}'")
        print("="*80)
    else:
        print("\nAVISO: Nenhum dado foi processado para o ficheiro de resumo.")


if __name__ == "__main__":
    consolidate_and_summarize_metrics()

