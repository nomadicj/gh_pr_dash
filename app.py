from flask import Flask, render_template
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def calculate_age(created_at):
    created_date = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
    return (datetime.utcnow() - created_date).days

@app.route('/')
@app.route('/repo/<repo_name>')
def index(repo_name=None):
    org_name = os.getenv('ORG_NAME')  # Pulls the organization name from .env
    token = os.getenv('GITHUB_TOKEN')  # Pulls the GitHub token from .env

    headers = {'Authorization': f'token {token}'}
    repos_response = requests.get(f'https://api.github.com/orgs/{org_name}/repos', headers=headers)
    repos = repos_response.json()

    prs_by_repo = {}
    for repo in repos:
        prs_response = requests.get(repo['pulls_url'].replace('{/number}', ''), headers=headers)
        prs = prs_response.json()

        if prs:
            prs_by_repo[repo['name']] = [{
                'title': pr['title'],
                'author': pr['user']['login'],
                'url': pr['html_url'],
                'age': calculate_age(pr['created_at']),
                'comments': pr.get('comments', 0)
            } for pr in prs]

    repo_names = [repo['name'] for repo in repos]  # Extract repository names

    repo_pr_counts = {repo: len(prs) for repo, prs in prs_by_repo.items()}

    if repo_name and repo_name in prs_by_repo:
        selected_prs = prs_by_repo[repo_name]
    else:
        selected_prs = []

    return render_template(
        'index.html',
        org_name=org_name,
        prs_by_repo=prs_by_repo,
        repo_names=repo_names,
        repo_pr_counts=repo_pr_counts,
        selected_prs=selected_prs,
        selected_repo=repo_name
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
