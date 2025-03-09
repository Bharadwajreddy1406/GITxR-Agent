import sys
from typing import Optional, List, Dict, Set, Any
from rich.console import Console
import argparse
import pandas as pd
import json
import traceback

from .github_api import GitHubAPIClient
from .llm_client import LLMClient
from .data_processing import DataProcessor
from .visualization import Visualizer

class GitXRCLI:
    """Command-line interface for the GITxR agent."""
    
    def __init__(self):
        self.console = Console()
        self.github_client = GitHubAPIClient()
        self.llm_client = LLMClient()
        self.data_processor = DataProcessor()
        self.visualizer = Visualizer()
        self.conversation_history = []
        
    def get_required_params(self, intent: str) -> Dict[str, str]:
        """Get required parameters for a specific intent."""
        # Dictionary mapping intents to their required parameters with description
        intent_params = {
            'get_contributors': {'owner': 'repository owner/organization', 'repo': 'repository name'},
            'get_commit_history': {'owner': 'repository owner/organization', 'repo': 'repository name'},
            'get_recent_merged_prs': {'owner': 'repository owner/organization', 'repo': 'repository name'},
            'list_user_repositories': {'username': 'GitHub username'},
            'get_user_repositories': {'username': 'GitHub username'},
            'get_repositories': {'username': 'GitHub username'},  # Added this to handle "get repositories" intent
            'search_repositories': {'query': 'search term'},
            'unknown': {},  # Handle unknown intent gracefully
        }
        
        return intent_params.get(intent, {})
    
    def validate_and_complete_params(self, intent: str, params: Any) -> Dict:
        """Check if all required parameters are present and prompt for missing ones."""
        required_params = self.get_required_params(intent)
        
        # Convert params to dictionary if it's not already (handles lists or other unexpected types)
        if not isinstance(params, dict):
            self.console.print(f"[bold yellow]Warning:[/bold yellow] Expected parameters as dictionary but got {type(params)}. Converting to empty dict.")
            updated_params = {}
        else:
            updated_params = params.copy()
        
        # Check for missing required parameters
        for param_name, param_desc in required_params.items():
            if param_name not in updated_params or not updated_params.get(param_name):
                self.console.print(f"[bold yellow]Missing required parameter:[/bold yellow] {param_desc}")
                param_value = self.console.input(f"Please provide the {param_name} ({param_desc}): ")
                updated_params[param_name] = param_value
                
                # Update conversation history to include this parameter
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": f"Could you please provide the {param_name} ({param_desc})?"
                })
                self.conversation_history.append({
                    "role": "user", 
                    "content": param_value
                })
        
        return updated_params
    
    def process_query(self, query: str) -> None:
        """Process a natural language query about GitHub repositories."""
        self.console.print(f"[bold blue]Processing query:[/bold blue] {query}")
        
        try:
            # First try direct pattern matching to avoid LLM failures for common queries
            if self.is_list_repos_query(query):
                intent_data = self.fallback_intent_detection(query)
                self.console.print("[blue]Using direct pattern matching for repository listing query[/blue]")
            else:
                # Use LLM to understand the query intent and extract parameters
                try:
                    intent_data = self.llm_client.process_query(query, self.conversation_history)
                    
                    # Ensure intent_data is a dictionary
                    if not isinstance(intent_data, dict):
                        self.console.print(f"[bold yellow]Warning:[/bold yellow] LLM returned non-dictionary: {intent_data}")
                        # Fallback to pattern matching
                        intent_data = self.fallback_intent_detection(query)
                        self.console.print("[blue]Using fallback pattern matching for intent detection[/blue]")
                except Exception as e:
                    self.console.print(f"[bold yellow]LLM processing failed: {str(e)}[/bold yellow]")
                    # Fallback to pattern matching
                    intent_data = self.fallback_intent_detection(query)
                    self.console.print("[blue]Using fallback pattern matching due to LLM failure[/blue]")
            
            if intent_data.get('intent') == 'error':
                self.console.print(f"[bold red]Error:[/bold red] {intent_data.get('parameters', {}).get('error', 'Unknown error')}")
                return
            
            # Log the detected intent
            self.console.print(f"[blue]Detected intent:[/blue] {intent_data.get('intent', 'unknown')}")
            
            # Store the conversation
            self.conversation_history.append({"role": "user", "content": query})
            
            # Validate and complete any missing parameters through conversation
            intent = intent_data.get('intent')
            params = self.validate_and_complete_params(intent, intent_data.get('parameters', {}))
            
            # Update the intent_data with the completed parameters
            intent_data['parameters'] = params
            
            # Execute the appropriate GitHub API call based on intent
            result = self.execute_intent(intent_data)
            
            # Generate a response based on the data and original query
            if result:
                try:
                    response = self.llm_client.generate_response(result, query)
                    self.console.print(f"[bold green]Response:[/bold green] {response}")
                    self.conversation_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    self.console.print(f"[bold yellow]Could not generate response: {str(e)}[/bold yellow]")
                    self.console.print("[green]Data was processed successfully but couldn't generate a narrative response.[/green]")
            
        except Exception as e:
            self.console.print(f"[bold red]Error processing query:[/bold red] {str(e)}")
            traceback.print_exc()
    
    def is_list_repos_query(self, query: str) -> bool:
        """Check if query is asking for repository listing."""
        query = query.lower()
        repo_terms = ["repo", "repos", "repositories", "repository"]
        action_terms = ["list", "show", "get", "find", "display", "tell"]
        
        # Check if query contains both repo terms and action terms
        has_repo_term = any(term in query for term in repo_terms)
        has_action_term = any(term in query for term in action_terms)
        
        # Check if the query mentions "of username" pattern
        has_of_pattern = "of " in query
        
        return (has_repo_term and has_action_term) or (has_repo_term and has_of_pattern)
    
    def fallback_intent_detection(self, query: str) -> Dict:
        """Fallback method to detect intent when LLM fails."""
        query = query.lower()
        
        # Extract username if present in query
        username = None
        if "of " in query:
            # Try to extract username after "of"
            parts = query.split("of ", 1)
            if len(parts) > 1:
                username = parts[1].strip()
        
        repo_terms = ["repo", "repos", "repositories", "repository"]
        if any(x in query for x in ["list", "show", "get", "find", "display", "tell"]) and any(x in query for x in repo_terms):
            if username:
                return {
                    "intent": "list_user_repositories",
                    "parameters": {"username": username}
                }
            else:
                return {
                    "intent": "list_user_repositories",
                    "parameters": {}
                }
                
        elif any(x in query for x in ["search", "find"]) and any(x in query for x in repo_terms):
            return {
                "intent": "search_repositories",
                "parameters": {"query": query.replace("search", "").replace("find", "").replace("repos", "").replace("repositories", "").strip()}
            }
        
        # Default intent
        return {
            "intent": "unknown",
            "parameters": {}
        }
    
    def execute_intent(self, intent_data: Dict) -> Optional[Dict]:
        """Execute the appropriate action based on the intent."""
        intent = intent_data.get('intent')
        params = intent_data.get('parameters', {})
        
        # Map similar intents to canonical handlers
        if intent in ['get_repositories', 'get_repos']:
            intent = 'list_user_repositories'
        
        try:
            if intent == 'get_contributors':
                data = self.github_client.get_repository_contributors(params.get('owner'), params.get('repo'))
                df = self.data_processor.contributors_to_dataframe(data)
                self.visualizer.show_console_table(df, f"Contributors for {params.get('owner')}/{params.get('repo')}")
                return {"contributors": data}
            
            elif intent == 'get_commit_history':
                branch = params.get('branch', 'main')
                count = int(params.get('count', 10))
                data = self.github_client.get_commit_history(params.get('owner'), params.get('repo'), branch, count)
                df = self.data_processor.commits_to_dataframe(data)
                self.visualizer.show_console_table(df, f"Commit history for {params.get('owner')}/{params.get('repo')}")
                return {"commits": data}
            
            elif intent == 'get_recent_merged_prs':
                count = int(params.get('count', 10))
                data = self.github_client.get_recent_merged_prs(params.get('owner'), params.get('repo'), count)
                df = self.data_processor.pull_requests_to_dataframe(data)
                self.visualizer.show_console_table(df, f"Recent merged PRs for {params.get('owner')}/{params.get('repo')}")
                return {"pull_requests": data}
                
            elif intent == 'list_user_repositories' or intent == 'get_user_repositories':
                username = params.get('username')
                if not username:
                    self.console.print("[bold red]Error: No username provided for repository listing[/bold red]")
                    return {"error": "No username provided"}
                
                self.console.print(f"[blue]Fetching repositories for user: {username}[/blue]")
                try:
                    data = self.github_client.get_user_repositories(username)
                    if not data:
                        self.console.print(f"[yellow]No repositories found for user: {username}[/yellow]")
                        return {"repositories": [], "message": f"No repositories found for {username}"}
                    
                    if isinstance(data, list):
                        # Create a simplified format for display
                        repos_data = []
                        for repo in data:
                            repos_data.append({
                                'Name': repo['name'],
                                'Description': repo.get('description', 'No description'),
                                'Stars': repo['stargazers_count'],
                                'Forks': repo['forks_count'],
                                'Last Updated': repo['updated_at'],
                                'URL': repo['html_url']
                            })
                        df = pd.DataFrame(repos_data)
                        self.visualizer.show_console_table(df, f"Repositories for user '{username}'")
                        return {"repositories": data}
                    else:
                        self.console.print(f"[bold yellow]Warning:[/bold yellow] Unexpected data format: {type(data)}")
                        return {"error": f"Unexpected data format: {type(data)}"}
                except Exception as e:
                    self.console.print(f"[bold red]Error fetching repositories:[/bold red] {str(e)}")
                    return {"error": str(e)}
            
            elif intent == 'search_repositories':
                data = self.github_client.search_repositories(params.get('query'), params.get('sort', 'stars'))
                # Fix: Check if data is a dict (API response) or list (items directly)
                items = data.get('items', []) if isinstance(data, dict) else data
                df = self.data_processor.search_results_to_dataframe(items, 'repositories')
                self.visualizer.show_console_table(df, f"Repository search results for '{params.get('query')}'")
                return {"search_results": data}
            
            elif intent == 'unknown':
                self.console.print("[bold yellow]Could not determine specific intent. Please try rephrasing your query.[/bold yellow]")
                return {"error": "Unknown intent", "query": intent_data.get('query', '')}
                
            else:
                self.console.print(f"[bold yellow]Unhandled intent:[/bold yellow] {intent}")
                return {"error": f"Unhandled intent: {intent}"}
                
        except Exception as e:
            self.console.print(f"[bold red]Error executing intent:[/bold red] {str(e)}")
            traceback.print_exc()  # Print the full stack trace for debugging
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="GITxR Agent - GitHub Explainer CLI")
    parser.add_argument("query", nargs="*", help="Natural language query about GitHub repositories")
    
    args = parser.parse_args()
    cli = GitXRCLI()
    
    if args.query:
        # Process the command-line query
        cli.process_query(" ".join(args.query))
    else:
        # Interactive mode
        console = Console()
        console.print("[bold green]GITxR Agent[/bold green] - Ask me anything about GitHub repositories!")
        console.print("Type 'exit' or 'quit' to exit.")
        
        while True:
            query = console.input("\n[bold blue]Query:[/bold blue] ")
            if query.lower() in ('exit', 'quit'):
                break
            cli.process_query(query)

if __name__ == "__main__":
    main()
