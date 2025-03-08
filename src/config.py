import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub API credentials
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_SSH_KEY_PATH = os.getenv("GITHUB_SSH_KEY_PATH", "~/.ssh/id_rsa")

# LLM API credentials (Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.2-1b-preview")

# Application settings
DEFAULT_QUERY_TIMEOUT = int(os.getenv("DEFAULT_QUERY_TIMEOUT", "30"))
DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "console")