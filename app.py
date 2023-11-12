from flask import Flask, render_template, redirect, url_for
from flask_caching import Cache
import requests
import pendulum
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})  # You can choose different backends

@app.route('/')
@app.route('/repo/<repo_name>/<categorisation>')
@cache.cached(timeout=300, query_string=True)  # Cache this view for 5 minutes, vary on query string
def index(repo_name=None, categorisation=None):
    org_name = os.getenv('ORG_NAME')  # Pulls the organization name from .env
    token = os.getenv('GITHUB_TOKEN')  # Pulls the GitHub token from .env
    headers = {'Authorization': f'token {token}'}

    repos_response = get_github_org_data(org_name=org_name, headers=headers)
    repos = repos_response.json()

    current_prs = {}
    aging_prs = {}
    geriatric_prs = {}
    dependabot_prs = {}

    for repo in repos:
        repo_url = repo['pulls_url'].replace('{/number}', '')
        prs_response = get_github_repo_data(repo=repo_url, headers=headers)
        prs = prs_response.json()

        dependabot_prs[repo['name']] = [{
            'title': pr['title'],
            'author': pr['user']['login'],
            'url': pr['html_url'],
            'age': calculate_age(pr['created_at']),
            'comments': pr.get('comments', 0)
        } for pr in prs if pr['user']['login'] == 'dependabot[bot]']

        current_prs[repo['name']] = [{
            'title': pr['title'],
            'author': pr['user']['login'],
            'url': pr['html_url'],
            'age': calculate_age(pr['created_at']),
            'comments': pr.get('comments', 0)
        } for pr in prs if calculate_age(pr['created_at']) < 15]

        aging_prs[repo['name']] = [{
            'title': pr['title'],
            'author': pr['user']['login'],
            'url': pr['html_url'],
            'age': calculate_age(pr['created_at']),
            'comments': pr.get('comments', 0)
        } for pr in prs if 15 <= calculate_age(pr['created_at']) <= 60]

        geriatric_prs[repo['name']] = [{
            'title': pr['title'],
            'author': pr['user']['login'],
            'url': pr['html_url'],
            'age': calculate_age(pr['created_at']),
            'comments': pr.get('comments', 0)
        } for pr in prs if calculate_age(pr['created_at']) > 60]

    repo_names = [repo['name'] for repo in repos]  # Extract repository names

    current_pr_counts = {repo: len(prs) for repo, prs in current_prs.items()}
    aging_pr_counts = {repo: len(prs) for repo, prs in aging_prs.items()}
    geriatric_pr_counts = {repo: len(prs) for repo, prs in geriatric_prs.items()}
    dependabot_pr_counts = {repo: len(prs) for repo, prs in dependabot_prs.items()}
    
    categorised_prs = {
        'current': current_prs,
        'aging': aging_prs,
        'geriatric': geriatric_prs,
        'dependabot': dependabot_prs
    }

    if repo_name and categorisation and repo_name in categorised_prs[categorisation]:
        selected_prs = categorised_prs[categorisation][repo_name]
    else:
        selected_prs = []

    print(f'Selected PRs: {selected_prs}')
    print(f'Selected Category: {categorisation}')
    print(f'Selected Repo: {repo_name}')
    print(f'Selected cpr: {categorised_prs[categorisation]}')


    return render_template(
        'index.html',
        org_name=org_name,
        repo_names=repo_names,
        current_pr_counts={k: v for k, v in current_pr_counts.items() if v},
        aging_pr_counts={k: v for k, v in aging_pr_counts.items() if v},
        geriatric_pr_counts={k: v for k, v in geriatric_pr_counts.items() if v},
        dependabot_pr_counts={k: v for k, v in dependabot_pr_counts.items() if v},
        selected_prs=selected_prs,
        selected_repo=repo_name,
        selected_category=categorisation,
        dependabot_prs=dependabot_prs,
        current_prs=current_prs,
        aging_prs=aging_prs,
        geriatric_prs=geriatric_prs
        )

@app.route('/refresh')
def refresh():
    cache.clear()  # Clear the entire cache
    return redirect(url_for('index'))  # Redirect back to the main page

def add_repo_to_category(category: dict):
    category[repo['name']] = [{
                'title': pr['title'],
                'author': pr['user']['login'],
                'url': pr['html_url'],
                'age': calculate_age(pr['created_at']),
                'comments': pr.get('comments', 0)
            } for pr in prs]

def calculate_age(created_at):
    created_at = pendulum.parse(created_at)
    return pendulum.now().diff(created_at).in_days()

def get_github_org_data(org_name: str, headers: dict):
    cache_key = f'github_data_{org_name}'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    data = requests.get(f'https://api.github.com/orgs/{org_name}/repos', headers=headers)

    cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
    return data

def get_github_repo_data(repo: str, headers: dict):
    cache_key = f'github_data_{repo}'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    data = requests.get(repo, headers=headers)

    cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
