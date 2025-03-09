# import os
# import requests


# def list_repositories(username):
#     # Optionally use a GitHub token for authenticated requests
#     token = os.getenv("GITHUB_TOKEN")
#     headers = {"Authorization": f"token {token}"} if token else {}

#     # GitHub API endpoint to list user repositories
#     url = f"https://api.github.com/users/{username}/repos"
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         repos_data = response.json()
#         # Extract repository names dynamically
#         # print(repos_data)  be shocked if u un comment and run this
#         repos = [repo['name'] for repo in repos_data]
#         return repos
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return []


# if __name__ == "__main__":
#     # Prompt the user for a GitHub username
#     username = input("Enter a GitHub username: ").strip()
#     repositories = list_repositories(username)

#     if repositories:
#         print(f"\nRepositories for user '{username}':")
#         for repo in repositories:
#             print(f"- {repo}")
#     else:
#         print("No repositories found or an error occurred.")

from src.github_api import GitHubAPIClient
from src.data_processing import DataProcessor


client = GitHubAPIClient()
data_guy = DataProcessor()
res = client.get_recent_merged_prs(owner="Bharadwajreddy1406",repo="TypeScript-shadcn-components")
tables = data_guy.pull_requests_to_dataframe(res)
print(tables)
