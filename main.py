import requests
import time
import os
import pandas as pd
from datetime import datetime

# Pega o token de autenticação do GitHub diretamente das variáveis de ambiente
# Certifique-se de definir a variável de ambiente TOKEN antes de executar.
GITHUB_TOKEN = os.getenv("TOKEN")
GITHUB_API_URL = 'https://api.github.com/graphql'

# Query GraphQL para buscar os repositórios Java mais populares de forma paginada
GET_TOP_REPOS_PAGINATED_QUERY = """
query GetTopJavaRepos($afterCursor: String) {
  search(query: "language:Java sort:stars-desc is:public", type: REPOSITORY, first: 100, after: $afterCursor) {
    nodes {
      ... on Repository {
        owner {
          login
        }
        name
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

# Query GraphQL para buscar detalhes específicos de cada repositório
GET_REPO_DETAILS_QUERY = """
query GetRepoDetails($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    nameWithOwner
    createdAt
    releases {
      totalCount
    }
    stargazerCount
  }
}
"""

def run_graphql_query(query, variables=None):
    """
    Executa uma query GraphQL na API do GitHub.
    """
    if not GITHUB_TOKEN:
        raise Exception("Token do GitHub não encontrado. Configure a variável de ambiente TOKEN.")

    headers = {
        'Authorization': f'bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json',
    }

    request_body = {'query': query, 'variables': variables or {}}

    response = requests.post(GITHUB_API_URL, headers=headers, json=request_body, timeout=60)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query falhou com o código {response.status_code}:\n{response.text}")

def get_all_top_repos(total_to_fetch=1000):
    """
    Busca repositórios em lotes de 100 até atingir o total desejado.
    """
    all_repo_nodes = []
    after_cursor = None

    print(f"Iniciando coleta de {total_to_fetch} repositórios Java (em lotes de 100)...")

    num_to_fetch = min(total_to_fetch, 1000)

    while len(all_repo_nodes) < num_to_fetch:
        variables = {"afterCursor": after_cursor}
        result = run_graphql_query(GET_TOP_REPOS_PAGINATED_QUERY, variables)

        if 'errors' in result:
            raise Exception(f"Erro na API do GitHub: {result['errors']}")

        search_data = result['data']['search']
        new_nodes = search_data['nodes']
        page_info = search_data['pageInfo']

        all_repo_nodes.extend(new_nodes)
        after_cursor = page_info['endCursor']

        progress = (len(all_repo_nodes) / num_to_fetch) * 100
        print(f"\rColetados {len(all_repo_nodes)} de {num_to_fetch} repositórios ({progress:.1f}%)", end='', flush=True)

        if not page_info['hasNextPage']:
            print("\nNão há mais páginas para buscar. Fim da coleta.")
            break

        time.sleep(0.2)  # Pausa para evitar limites da API

    print()
    return all_repo_nodes[:num_to_fetch]

def get_repo_details(repo_list):
    """
    Busca os detalhes para cada repositório da lista.
    """
    all_repo_data = []
    total_repos = len(repo_list)

    print(f"Buscando detalhes para {total_repos} repositórios...")

    for i, repo_node in enumerate(repo_list, 1):
        owner = repo_node['owner']['login']
        name = repo_node['name']

        variables = {"owner": owner, "name": name}
        try:
            details_result = run_graphql_query(GET_REPO_DETAILS_QUERY, variables)
            if 'data' in details_result and details_result['data'].get('repository'):
                repo_details = details_result['data']['repository']
                all_repo_data.append(repo_details)
            else:
                print(f"\nAVISO: Não foi possível obter detalhes para {owner}/{name}. Resposta: {details_result}")
        except Exception as e:
            print(f"\nERRO ao buscar detalhes para {owner}/{name}: {e}")

        progress = (i / total_repos) * 100
        print(f"\rCarregando detalhes {progress:.1f}%", end='', flush=True)

        time.sleep(0.1)

    print()
    return all_repo_data

def calculate_and_save_metrics(repo_data):
    """
    Calcula as métricas de processo e salva em um arquivo CSV.
    """
    df_data = []
    for repo in repo_data:
        if not repo: continue

        created_at_str = repo.get('createdAt')
        if not created_at_str: continue

        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
        
        # Maturidade: idade em anos
        maturidade_anos = (datetime.now(created_at.tzinfo) - created_at).days / 365.25

        df_data.append({
            'nameWithOwner': repo.get('nameWithOwner'),
            'popularidade_estrelas': repo.get('stargazerCount', 0),
            'atividade_releases': repo.get('releases', {}).get('totalCount', 0),
            'maturidade_anos': round(maturidade_anos, 2),
        })

    df = pd.DataFrame(df_data)
    output_filename = "java_repo_metrics.csv"
    df.to_csv(output_filename, index=False)
    print(f"\nMétricas salvas com sucesso no arquivo: {output_filename}")
    return df

def main():
    """
    Função principal para executar o processo de coleta e salvamento de dados.
    """
    try:
        repo_nodes = get_all_top_repos(1000)
        print(f"Lista de {len(repo_nodes)} repositórios obtida com sucesso!\n")

        repo_details = get_repo_details(repo_nodes)
        print("\nDetalhes dos repositórios obtidos com sucesso!\n")

        metrics_df = calculate_and_save_metrics(repo_details)
        print("\nDataFrame com métricas dos repositórios Java:")
        print(metrics_df.head())
        
        print("\n" + "="*80)
        print("COLETA DE DADOS FINALIZADA!")
        print(f"O arquivo 'java_repo_metrics.csv' está pronto para ser usado na próxima etapa de sua análise com a ferramenta CK.")
        print("="*80)

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")

if __name__ == '__main__':
    main()