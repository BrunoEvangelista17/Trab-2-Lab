import os
import pandas as pd

# --- CONFIGURE AQUI ---
# Confirme se este é o caminho correto para a pasta principal onde os
# resultados individuais de cada repositório foram salvos.
PATH_TO_OUTPUT_FOLDER = r"C:\Users\TI04\ResultadosCK"
# --- FIM DA CONFIGURAÇÃO ---


def consolidate_all_results():
    """
    Procura recursivamente por todos os ficheiros 'class.csv' na pasta de saída,
    junta todos os dados e salva num único ficheiro consolidado.
    """
    all_metrics_dfs = []
    
    print(f"Iniciando a busca por ficheiros 'class.csv' dentro de: '{PATH_TO_OUTPUT_FOLDER}'...")

    # Verifica se a pasta de saída principal existe
    if not os.path.exists(PATH_TO_OUTPUT_FOLDER):
        print(f"ERRO: O diretório especificado não foi encontrado: '{PATH_TO_OUTPUT_FOLDER}'")
        print("Por favor, verifique o caminho na configuração do script.")
        return

    # Procura recursivamente por todos os ficheiros 'class.csv'
    for root, dirs, files in os.walk(PATH_TO_OUTPUT_FOLDER):
        if "class.csv" in files:
            class_metrics_file = os.path.join(root, "class.csv")
            # O nome do repositório é o nome da pasta onde o 'class.csv' foi encontrado
            repo_name = os.path.basename(root)

            try:
                df = pd.read_csv(class_metrics_file)
                
                # Se o ficheiro estiver vazio, pula para o próximo
                if df.empty:
                    print(f"  - Aviso: Ficheiro 'class.csv' para '{repo_name}' está vazio. A ignorar.")
                    continue
                
                df['repository'] = repo_name
                all_metrics_dfs.append(df)
                print(f"  - Encontrado e processado: {repo_name} ({len(df)} linhas)")

            except Exception as e:
                print(f"  - ERRO: Não foi possível ler ou processar o ficheiro '{class_metrics_file}'. Erro: {e}")

    # Se encontrámos algum resultado, junta tudo e salva
    if all_metrics_dfs:
        print(f"\nConsolidando os dados de {len(all_metrics_dfs)} repositórios...")
        
        final_df = pd.concat(all_metrics_dfs, ignore_index=True)
        final_output_path = os.path.join(PATH_TO_OUTPUT_FOLDER, "consolidated_metrics.csv")
        
        final_df.to_csv(final_output_path, index=False)
        
        print("\n" + "="*80)
        print("SUCESSO!")
        print(f"Os resultados foram consolidados em:")
        print(f"'{final_output_path}'")
        print(f"Total de classes analisadas: {len(final_df)}")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("AVISO: Nenhum resultado encontrado para consolidar.")
        print("Verifique se os ficheiros 'class.csv' realmente existem dentro das subpastas")
        print(f"em '{PATH_TO_OUTPUT_FOLDER}'.")
        print("="*80)


if __name__ == "__main__":
    consolidate_all_results()