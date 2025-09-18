import os
import pandas as pd

# --- CONFIGURE AQUI ---
# Confirme se este é o caminho para a pasta que contém todos os seus
# ficheiros .csv (ex: vhrclass.csv, vespaclass.csv, etc.).
PATH_TO_OUTPUT_FOLDER = r"C:\Users\TI04\ResultadosCK"
# --- FIM DA CONFIGURAÇÃO ---


def consolidate_flat_results():
    """
    Procura por ficheiros que terminam com 'class.csv' numa única pasta,
    extrai o nome do repositório do nome do ficheiro e consolida os resultados.
    """
    all_metrics_dfs = []
    
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
            
            df['repository'] = repo_name
            all_metrics_dfs.append(df)
            print(f"  - Processado: {filename} ({len(df)} linhas)")

        except Exception as e:
            print(f"  - ERRO: Não foi possível ler ou processar o ficheiro '{filename}'. Erro: {e}")

    if all_metrics_dfs:
        print(f"\nConsolidando os dados de {len(all_metrics_dfs)} relatórios...")
        
        final_df = pd.concat(all_metrics_dfs, ignore_index=True)
        final_output_path = os.path.join(PATH_TO_OUTPUT_FOLDER, "consolidated_metrics.csv")
        
        final_df.to_csv(final_output_path, index=False)
        
        print("\n" + "="*80)
        print("SUCESSO!")
        print(f"Os resultados foram consolidados em:")
        print(f"'{final_output_path}'")
        print(f"Total de classes no relatório: {len(final_df)}")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("AVISO: Nenhum dado foi consolidado. Todos os ficheiros encontrados estavam vazios ou continham erros.")
        print("="*80)


if __name__ == "__main__":
    consolidate_flat_results()