import os
import pandas as pd

# --- CONFIGURE AQUI ---
# Confirme se este é o caminho para a pasta principal onde os
# seus ficheiros CSV estão salvos.
PATH_TO_OUTPUT_FOLDER = r"C:\Users\TI04\ResultadosCK"

# Nomes dos ficheiros de entrada
CK_SUMMARY_FILE = "repository_summary_metrics.csv"
METADATA_FILE = "metadata.csv"

# Nome do ficheiro de saída final
FINAL_OUTPUT_FILE = "final_analysis_dataset.csv"
# --- FIM DA CONFIGURAÇÃO ---


def merge_datasets_with_fix():
    """
    Junta os datasets corrigindo a incompatibilidade de nomes de repositório
    e lidando com erros de formatação no arquivo de metadados.
    """
    ck_file_path = os.path.join(PATH_TO_OUTPUT_FOLDER, CK_SUMMARY_FILE)
    metadata_file_path = os.path.join(PATH_TO_OUTPUT_FOLDER, METADATA_FILE)

    print("Iniciando a junção dos datasets com correção de nomes...")

    # Validação dos ficheiros de entrada
    if not os.path.exists(ck_file_path) or not os.path.exists(metadata_file_path):
        print(f"ERRO: Verifique se os arquivos '{CK_SUMMARY_FILE}' e '{METADATA_FILE}' existem na pasta.")
        return

    try:
        # Carregar os datasets
        print("Lendo os arquivos...")
        ck_df = pd.read_csv(ck_file_path)

        # --- CORREÇÃO DEFINITIVA PARA LEITURA APLICADA AQUI ---
        # Adicionado on_bad_lines='warn' para avisar sobre linhas mal formatadas em vez de falhar.
        # Mantido engine='python' para maior flexibilidade.
        print(f"Lendo metadados de '{METADATA_FILE}' (com tratamento de erros)...")
        metadata_df = pd.read_csv(metadata_file_path, engine='python', on_bad_lines='warn')

        # --- CORREÇÃO DE NOMES ---
        # Cria uma nova coluna com o nome simples do repositório para a junção.
        print("Padronizando os nomes dos repositórios para a junção...")
        metadata_df['repo_name_simple'] = metadata_df['nameWithOwner'].str.split('/', expand=True)[1]

        # --- Realizar a junção (merge) ---
        print("Realizando a junção dos dados...")
        final_df = pd.merge(
            left=ck_df,
            right=metadata_df,
            left_on='repository',
            right_on='repo_name_simple',
            how='inner'
        )

        # Limpeza do DataFrame final
        if 'repo_name_simple' in final_df.columns:
            final_df = final_df.drop(columns=['repo_name_simple'])
        if 'nameWithOwner' in final_df.columns:
            final_df = final_df.rename(columns={'nameWithOwner': 'repository_full_name'})

        # Salva o dataset final
        final_output_path = os.path.join(PATH_TO_OUTPUT_FOLDER, FINAL_OUTPUT_FILE)
        final_df.to_csv(final_output_path, index=False)

        print("\n" + "="*80)
        print("SUCESSO!")
        print(f"O dataset final para análise foi salvo em:")
        print(f"'{final_output_path}'")
        
        if len(final_df) > 0:
            print(f"Foram unificados com sucesso dados de {len(final_df)} repositórios.")
        else:
            print("AVISO: Nenhum repositório foi unificado. Verifique se os nomes nos arquivos CSV correspondem.")
        
        print("="*80)

    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o processo: {e}")


if __name__ == "__main__":
    merge_datasets_with_fix()