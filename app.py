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
def index():
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

    return render_template('index.html', org_name=org_name, prs_by_repo=prs_by_repo)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
