# Ficheiro: .github/scripts/update_last_project.py
# Objetivo: Atualizar a secção "Último Projeto Trabalhado" no README

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


def get_last_commit_info():
    """
    Busca o último commit do utilizador em todos os repositórios (públicos e privados).
    Retorna as informações do repositório e do commit mais recente.
    """
    # Buscar todos os repositórios do utilizador
    repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
    repos_response = requests.get(repos_url, headers=headers)
    repos = repos_response.json()

    last_commit = None
    last_repo = None

    for repo in repos:
        repo_name = repo["name"]
        repo_full_name = repo["full_name"]
        
        # Ignorar o repositório especial (Shega-PT/Shega-PT)
        if repo_full_name == f"{GITHUB_USERNAME}/{GITHUB_USERNAME}":
            continue

        # Buscar o último commit do repositório
        commits_url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=1"
        commits_response = requests.get(commits_url, headers=headers)
        commits = commits_response.json()
        
        if not commits:
            continue
        
        commit = commits[0]
        commit_date = commit["commit"]["committer"]["date"]
        commit_date_obj = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")
        
        # Atualizar se este commit for mais recente
        if last_commit is None or commit_date_obj > last_commit["date"]:
            last_commit = {
                "date": commit_date_obj,
                "repo_name": repo_name,
                "repo_url": repo["html_url"],
                "language": repo.get("language", "N/A"),
                "commit_msg": commit["commit"]["message"].split("\n")[0],
                "commit_date": commit_date[:10],
                "description": repo.get("description", "Sem descrição definida.")
            }

    return last_commit


def update_readme(last_commit_info):
    """
    Atualiza o README.md com as informações do último commit.
    """
    if not last_commit_info:
        print("Nenhum commit encontrado.")
        return

    # Formatar o conteúdo da secção
    card_content = f"""
### 🛠️ Último Projeto Ativo: [{last_commit_info['repo_name']}]({last_commit_info['repo_url']})
* **Linguagem:** `{last_commit_info['language']}` | **Data:** {last_commit_info['commit_date']}
* **Último Commit:** `{last_commit_info['commit_msg']}`
> **Descrição:** {last_commit_info['description']}
"""

    # Ler o README atual
    with open("README.md", "r", encoding="utf-8") as file:
        readme_content = file.read()

    # Substituir a secção entre os marcadores
    start_tag = "<!-- START_SECTION:last_project -->"
    end_tag = "<!-- END_SECTION:last_project -->"
    
    start_index = readme_content.find(start_tag)
    end_index = readme_content.find(end_tag)

    if start_index == -1 or end_index == -1:
        print("Marcadores START_SECTION ou END_SECTION não encontrados no README.")
        return

    new_readme = (
        readme_content[:start_index] +
        start_tag + "\n" + card_content + "\n" + end_tag +
        readme_content[end_index + len(end_tag):]
    )

    # Escrever o novo README
    with open("README.md", "w", encoding="utf-8") as file:
        file.write(new_readme)

    print(f"README atualizado! Último projeto: {last_commit_info['repo_name']}")


if __name__ == "__main__":
    last_commit_info = get_last_commit_info()
    if last_commit_info:
        update_readme(last_commit_info)
    else:
        print("Não foi possível obter informações do último commit.")
