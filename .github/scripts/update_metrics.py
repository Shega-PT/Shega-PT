# Ficheiro: .github/scripts/update_metrics.py
# Objetivo: Atualizar a tabela de métricas em "Métricas de Projetos" no README

import os
import requests
from datetime import datetime

# Variáveis de ambiente
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")

# Headers para a API do GitHub
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Lista de repositórios públicos a incluir na tabela (ajusta conforme necessário)
REPOS_TO_INCLUDE = ["AERUS", "PilotOne", "Bythos", "TELLUS", "AstroFrame-Py"]


def get_repo_metrics(repo_name):
    """
    Busca métricas de um repositório: linguagem, LOC, último commit, licença.
    """
    repo_full_name = f"{GITHUB_USERNAME}/{repo_name}"
    
    # Buscar dados do repositório
    repo_url = f"https://api.github.com/repos/{repo_full_name}"
    repo_response = requests.get(repo_url, headers=headers)
    repo_data = repo_response.json()
    
    # Buscar último commit
    commits_url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=1"
    commits_response = requests.get(commits_url, headers=headers)
    commits_data = commits_response.json()
    last_commit_date = commits_data[0]["commit"]["committer"]["date"][:10] if commits_data else "N/A"
    
    # Buscar linguagens (para LOC)
    languages_url = f"https://api.github.com/repos/{repo_full_name}/languages"
    languages_response = requests.get(languages_url, headers=headers)
    languages_data = languages_response.json()
    total_loc = sum(languages_data.values()) if languages_data else 0
    
    # Dados do repositório
    language = repo_data.get("language", "N/A")
    license_key = repo_data.get("license", {}).get("key", "N/A")
    
    return {
        "name": repo_name,
        "url": repo_data["html_url"],
        "language": language,
        "loc": total_loc,
        "last_commit": last_commit_date,
        "license": license_key
    }


def generate_metrics_table():
    """
    Gera a tabela de métricas em Markdown.
    """
    table_header = """
| **Projeto** | **Linguagem Principal** | **Linhas de Código** | **Último Commit** | **Licença** |
|------------|------------------------|----------------------|-------------------|-------------|
"""
    
    table_rows = []
    for repo_name in REPOS_TO_INCLUDE:
        metrics = get_repo_metrics(repo_name)
        language_badge = f"![{metrics['language']}](https://img.shields.io/badge/{metrics['language']}-00599C?style=flat-square)" if metrics['language'] != "N/A" else "N/A"
        loc_badge = f"![LOC](https://img.shields.io/badge/LOC-{metrics['loc']}-blue?style=flat-square)"
        last_commit_badge = f"![Último Commit](https://img.shields.io/badge/Último%20Commit-{metrics['last_commit']}-green?style=flat-square)"
        license_badge = f"![Licença](https://img.shields.io/badge/Licença-{metrics['license']}-lightgrey?style=flat-square)"
        
        row = f"| [{metrics['name']}]({metrics['url']}) | {language_badge} | {loc_badge} | {last_commit_badge} | {license_badge} |"
        table_rows.append(row)
    
    return table_header + "\n".join(table_rows)


def update_readme():
    """
    Atualiza o README com a tabela de métricas.
    """
    new_table = generate_metrics_table()
    
    with open("README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()
    
    # Marcadores para a tabela de métricas
    start_marker = "| **Projeto** | **Linguagem Principal** | **Linhas de Código** | **Último Commit** | **Licença** |"
    end_marker = "</div>"
    
    # Encontrar a secção a substituir
    start_index = readme_content.find(start_marker)
    if start_index == -1:
        print("Marcador de início da tabela de métricas não encontrado.")
        return
    
    # Encontrar o fim da tabela (próxima linha </div>)
    end_index = readme_content.find(end_marker, start_index)
    if end_index == -1:
        print("Marcador de fim da tabela de métricas não encontrado.")
        return
    
    # Substituir a tabela
    new_readme = (
        readme_content[:start_index] +
        new_table + "\n" +
        readme_content[end_index:]
    )
    
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(new_readme)
    
    print("README atualizado com sucesso!")


if __name__ == "__main__":
    update_readme()
