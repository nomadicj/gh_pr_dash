# Flask GitHub PR Dashboard

## Overview

This Flask application displays open pull requests (PRs) for each repository in a specified GitHub organization. It organizes PRs into columns by repository, with each repo name as a header and the PRs listed underneath. The application also features a dark mode toggle for enhanced user experience.

The app is containerized using Docker, making it easy to build and run in any environment. Docker Compose is used for defining and running multi-container Docker applications, and a Makefile is included for simplifying Docker commands.

## Features

- Display open PRs by repository within a GitHub organization.
- View PR title, author, age, and number of comments.
- Dark mode toggle for UI.
- Containerized environment with Docker.
- Simplified command execution using Makefile.

## Prerequisites

- Docker and Docker Compose installed on your machine.
- A GitHub Personal Access Token with `public_repo` scope for public repositories or `repo` scope for private repositories.

## Setup

1. **Clone the Repository**
   
   ```bash
   git clone [repository-url]
   cd [repository-directory]```
   
2. **Create an .env File**

Create a .env file in the root directory of the project with the following content:

  ```plaintext
  GITHUB_TOKEN=your_github_token
  ORG_NAME=your_org_name
  ```

Replace your_github_token and your_org_name with your GitHub Personal Access Token and the name of the GitHub organization you want to analyze.

3. **Build and Run with Docker Compose**

Using the Makefile, you can easily build and run the application:

  ```bash
  make build
  make run
  ```

This will start the application and make it accessible at http://localhost:5000.

## Usage
- Navigate to http://localhost:5000 in your browser to view the open PRs dashboard.
- Use the "Toggle Dark Mode" button to switch between light and dark themes.

## Development Commands
- Build Docker Image: make build
- Run Application: make run
- Stop Application: make down
- Open Shell in Container: make shell
- (Optional) Run Tests: make test (Note: Set up tests in your project)

## Contributions
Contributions to this project are welcome. Please ensure to follow the best practices and coding standards.
