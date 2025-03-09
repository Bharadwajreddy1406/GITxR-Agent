import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Optional, Tuple
import os
from rich.console import Console
from rich.table import Table

class Visualizer:
    """Visualize GitHub data in various formats."""
    
    def __init__(self):
        """Initialize the visualizer."""
        self.console = Console()
        
        # Set up matplotlib style
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
    
    def show_console_table(self, df: pd.DataFrame, title: str) -> None:
        """Display data as a table in the console using rich."""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        # Add columns
        for column in df.columns:
            table.add_column(column, style="dim")
        
        # Add rows
        for _, row in df.iterrows():
            table.add_row(*[str(val) for val in row.values])
        
        # Print table
        self.console.print(table)
    
    def plot_contributors(self, df: pd.DataFrame, limit: int = 10, save_path: Optional[str] = None) -> str:
        """Plot top contributors by contribution count."""
        # Take top N contributors
        if len(df) > limit:
            df = df.nlargest(limit, 'Contributions')
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Contributions', y='Username', data=df, palette=self.colors)
        plt.title('Top Contributors')
        plt.xlabel('Number of Contributions')
        plt.ylabel('Username')
        plt.tight_layout()
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def plot_commits_over_time(self, df: pd.DataFrame, save_path: Optional[str] = None) -> str:
        """Plot commits over time."""
        # Convert Date to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Count commits by date
        commits_by_date = df.groupby(df['Date'].dt.date).size().reset_index(name='Count')
        
        plt.figure(figsize=(12, 6))
        plt.plot(commits_by_date['Date'], commits_by_date['Count'], marker='o', linestyle='-', color=self.colors[0])
        plt.title('Commits Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Commits')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def plot_issue_distribution(self, issues: List[Dict], save_path: Optional[str] = None) -> str:
        """Plot distribution of issues by state."""
        # Count issues by state
        states = [issue['state'] for issue in issues]
        state_counts = pd.Series(states).value_counts()
        
        plt.figure(figsize=(8, 8))
        plt.pie(state_counts, labels=state_counts.index, autopct='%1.1f%%', colors=self.colors, startangle=90)
        plt.title('Issue Distribution by State')
        plt.axis('equal')
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def plot_prs_by_author(self, df: pd.DataFrame, limit: int = 10, save_path: Optional[str] = None) -> str:
        """Plot pull requests by author."""
        # Count PRs by author
        pr_counts = df['Author'].value_counts().nlargest(limit)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x=pr_counts.values, y=pr_counts.index, palette=self.colors)
        plt.title('Pull Requests by Author')
        plt.xlabel('Number of Pull Requests')
        plt.ylabel('Author')
        plt.tight_layout()
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            plt.show()
            return ""
    
    def plot_repository_stars(self, df: pd.DataFrame, limit: int = 10, save_path: Optional[str] = None) -> str:
        """Plot repositories by star count."""
        # Take top N repositories
        if len(df) > limit:
            df = df.nlargest(limit, 'Stars')
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x='Stars', y='Name', data=df, palette=self.colors)
        plt.title('Top Repositories by Stars')
        plt.xlabel('Number of Stars')
        plt.ylabel('Repository')
        plt.tight_layout()
        
        if save_path:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            return save_path
        else:
            plt.show()
            return ""