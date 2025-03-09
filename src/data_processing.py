import pandas as pd
from typing import Dict, List, Any, Optional
import json
import os

class DataProcessor:
    """Process and transform GitHub API data."""
    
    @staticmethod
    def contributors_to_dataframe(contributors: List[Dict]) -> pd.DataFrame:
        """Convert contributors data to a pandas DataFrame."""
        df = pd.DataFrame(contributors)
        if not df.empty:
            df = df[['login', 'contributions', 'html_url']].rename(
                columns={'login': 'Username', 'contributions': 'Contributions', 'html_url': 'Profile URL'}
            )
        return df
    
    @staticmethod
    def commits_to_dataframe(commits: List[Dict]) -> pd.DataFrame:
        """Convert commit history data to a pandas DataFrame."""
        data = []
        for commit in commits:
            data.append({
                'SHA': commit['sha'][:7],
                'Author': commit['commit']['author']['name'],
                'Date': commit['commit']['author']['date'],
                'Message': commit['commit']['message'].split('\n')[0],
                'URL': commit.get('html_url', '')
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def pull_requests_to_dataframe(prs: List[Dict]) -> pd.DataFrame:
        """Convert pull requests data to a pandas DataFrame."""
        data = []
        for pr in prs:
            data.append({
                'Number': pr['number'],
                'Title': pr['title'],
                'Author': pr['user']['login'],
                'Merged By': pr.get('merged_by', {}).get('login', 'N/A') if pr.get('merged_at') else 'N/A',
                'Created At': pr['created_at'],
                'Merged At': pr.get('merged_at', 'N/A'),
                'URL': pr['html_url']
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def issues_to_dataframe(issues: List[Dict]) -> pd.DataFrame:
        """Convert issues data to a pandas DataFrame."""
        data = []
        for issue in issues:
            data.append({
                'Number': issue['number'],
                'Title': issue['title'],
                'State': issue['state'],
                'Author': issue['user']['login'],
                'Created At': issue['created_at'],
                'URL': issue['html_url']
            })
        return pd.DataFrame(data)
    
    @staticmethod
    def search_results_to_dataframe(results: List[Dict], search_type: str) -> pd.DataFrame:
        """Convert search results to a pandas DataFrame."""
        if search_type == 'repositories':
            data = []
            for repo in results:
                data.append({
                    'Name': repo['name'],
                    'Owner': repo['owner']['login'],
                    'Stars': repo['stargazers_count'],
                    'Forks': repo['forks_count'],
                    'Language': repo.get('language', 'N/A'),
                    'Description': repo.get('description', 'N/A'),
                    'URL': repo['html_url']
                })
            return pd.DataFrame(data)
        elif search_type == 'issues':
            data = []
            for issue in results:
                data.append({
                    'Title': issue['title'],
                    'Repository': issue['repository_url'].split('/')[-2] + '/' + issue['repository_url'].split('/')[-1],
                    'State': issue['state'],
                    'Author': issue['user']['login'],
                    'Created At': issue['created_at'],
                    'URL': issue['html_url']
                })
            return pd.DataFrame(data)
        else:
            return pd.DataFrame()
    
    @staticmethod
    def export_to_csv(df: pd.DataFrame, filename: str) -> str:
        """Export DataFrame to CSV file."""
        # Create exports directory if it doesn't exist
        os.makedirs('exports', exist_ok=True)
        
        # Generate file path
        filepath = os.path.join('exports', f"{filename}.csv")
        
        # Export to CSV
        df.to_csv(filepath, index=False)
        
        return filepath