import os
from dotenv import load_dotenv

load_dotenv()

# Load multiple API keys for different agents
GEMINI_API_KEYS = [
    os.getenv(f"GEMINI_API_KEY{i}", "") 
    for i in range(1, 7)
]

# Fallback: ensure there's at least one key if everything is empty
if not any(GEMINI_API_KEYS):
    GEMINI_API_KEYS = [os.getenv("GEMINI_API_KEY", "")]