"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# Native API keys for each provider
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Council members - now using native API model identifiers
COUNCIL_MODELS = [
    "openai/gpt-4o",  # OpenAI GPT-4o
    "google/gemini-2.0-flash-exp",  # Google Gemini
    "anthropic/claude-3-5-sonnet-20241022",  # Anthropic Claude 3.5 Sonnet
]

# Chairman model - synthesizes final response
CHAIRMAN_MODEL = "google/gemini-2.0-flash-exp"

# API endpoints
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
GOOGLE_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
