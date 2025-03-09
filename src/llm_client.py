from typing import Dict, List, Optional, Any
import json
import openai
from .config import GROQ_API_KEY, GROQ_BASE_URL, LLM_MODEL

class LLMClient:
    """Client for interacting with Groq's Language Model APIs."""
    
    def __init__(self, api_key: str = GROQ_API_KEY, base_url: str = GROQ_BASE_URL, model: str = LLM_MODEL):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # Initialize OpenAI client with Groq's base URL
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        
    def process_query(self, query: str, conversation_history: Optional[List[Dict]] = None) -> Dict:
        """Process a natural language query and extract intent and parameters."""
        if conversation_history is None:
            conversation_history = []
        
        # Construct the system prompt
        system_prompt = """
        You are an AI assistant named Lakshmi that helps interpret natural language queries about GitHub repositories.
        Your task is to:
        1. Identify the intent of the query (e.g., get_contributors, get_commits, search_repositories)
        2. Extract relevant parameters (repository name, owner, branch, etc.)
        3. Format the response as a JSON object with 'intent' and 'parameters' fields
        
        Available intents:
        - get_contributors: Get contributors for a repository
        - get_latest_branch: Get the latest branch in a repository
        - get_commit_history: Get recent commit history
        - get_weekly_commits: Count commits from the past week
        - get_recent_merged_prs: Get recently merged pull requests
        - get_contributor_stats: Get detailed contribution statistics
        - count_issues: Count issues in a repository by state
        - search_repositories: Search for repositories across GitHub
        - search_issues: Search for issues across GitHub
        
        Return ONLY the JSON response without any additional text.
        """
        
        # Build the messages
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        
        # Add conversation history
        for message in conversation_history:
            messages.append(message)
        
        # Add the current query
        messages.append({"role": "user", "content": query})
        
        # Make the API call
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0,
        )
        
        # Extract and parse the JSON response
        try:
            response_text = response.choices[0].message.content
            # Sometimes the LLM might wrap the JSON in backticks, so we need to clean it
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "", 1)
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "", 1)
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                
            return json.loads(response_text.strip())
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            return {
                "intent": "error",
                "parameters": {"error": str(e), "raw_response": str(response)}
            }
    
    def generate_response(self, data: Dict, query: str) -> str:
        """Generate a conversational response based on query and data."""
        system_prompt = """
        You are an AI assistant that helps analyze GitHub data.
        Given the data and the user's original query, provide a concise and informative response.
        Focus on the most relevant information and insights from the data.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original query: {query}\n\nData: {json.dumps(data, indent=2)}"}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        
        return response.choices[0].message.content