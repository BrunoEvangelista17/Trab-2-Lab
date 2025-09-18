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
