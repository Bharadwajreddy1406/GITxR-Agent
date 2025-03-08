import requests
import os
import subprocess
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

from .config import GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_SSH_KEY_PATH

class GitHubAPIClient:
    """Client for interacting with GitHub API and local repositories."""
    
    def __init__(self, token: str = GITHUB_TOKEN, username: str = GITHUB_USERNAME):
        self.token = token
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to the GitHub API."""
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_repository(self, owner: str, repo: str) -> Dict:
        """Get information about a specific repository."""
        return self._get(f"/repos/{owner}/{repo}")
    
    def get_repository_contributors(self, owner: str, repo: str) -> List[Dict]:
        """Get contributors for a repository."""
        return self._get(f"/repos/{owner}/{repo}/contributors")
    
    def get_repository_branches(self, owner: str, repo: str) -> List[Dict]:
        """Get branches for a repository."""
        return self._get(f"/repos/{owner}/{repo}/branches")
    
    def get_latest_branch(self, owner: str, repo: str) -> Dict:
        """Get the latest branch in a repository by activity."""
        branches = self.get_repository_branches(owner, repo)
        latest_branch = None
        latest_date = None
        
        for branch in branches:
            commit_info = self._get(f"/repos/{owner}/{repo}/commits/{branch['commit']['sha']}")
            commit_date = commit_info['commit']['author']['date']
            
            if latest_date is None or commit_date > latest_date:
                latest_date = commit_date
                latest_branch = branch
        
        return latest_branch
    
    def get_commit_history(self, owner: str, repo: str, branch: str = "main", count: int = 10) -> List[Dict]:
        """Get recent commit history for a repository."""
        return self._get(f"/repos/{owner}/{repo}/commits", {"sha": branch, "per_page": count})
    
    def get_weekly_commits(self, owner: str, repo: str) -> int:
        """Count commits from the past week."""
        commit_activity = self._get(f"/repos/{owner}/{repo}/stats/commit_activity")
        return commit_activity[0]['total'] if commit_activity else 0
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "all", count: int = 10) -> List[Dict]:
        """Get pull requests for a repository."""
        return self._get(f"/repos/{owner}/{repo}/pulls", {"state": state, "per_page": count})
    
    def get_recent_merged_prs(self, owner: str, repo: str, count: int = 10) -> List[Dict]:
        """Get recently merged pull requests with merger details."""
        merged_prs = []
        prs = self._get(f"/repos/{owner}/{repo}/pulls", {"state": "closed", "per_page": count})
        
        for pr in prs:
            if pr.get('merged_at'):
                pr_details = self._get(f"/repos/{owner}/{repo}/pulls/{pr['number']}")
                merged_prs.append(pr_details)
        
        return merged_prs
    
    def get_contributor_stats(self, owner: str, repo: str) -> List[Dict]:
        """Get detailed contribution statistics for a repository."""
        return self._get(f"/repos/{owner}/{repo}/stats/contributors")
    
    def get_issues(self, owner: str, repo: str, state: str = "all", count: int = 100) -> List[Dict]:
        """Get issues for a repository."""
        return self._get(f"/repos/{owner}/{repo}/issues", {"state": state, "per_page": count})
    
    def count_issues(self, owner: str, repo: str, state: str = "all") -> int:
        """Count issues in a repository by state."""
        issues = self.get_issues(owner, repo, state)
        return len(issues)
    
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc", count: int = 10) -> List[Dict]:
        """Search for repositories across GitHub."""
        results = self._get("/search/repositories", {"q": query, "sort": sort, "order": order, "per_page": count})
        return results
    def get_workflow_runs(self, owner: str, repo: str, workflow_id: str, count: int = 10) -> List[Dict]:
        """Get workflow runs for a specific workflow."""
        return self._get(f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs", {"per_page": count})
    
    def get_workflow_run_details(self, owner: str, repo: str, run_id: int) -> Dict:
        """Get details of a specific workflow run."""
        return self._get(f"/repos/{owner}/{repo}/actions/runs/{run_id}")