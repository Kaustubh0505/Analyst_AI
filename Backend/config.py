import os
from dotenv import load_dotenv

load_dotenv()

# List of API keys for different agents
GROQ_API_KEYS = {
    1: os.getenv("GROQ_API_KEY1", ""),
    2: os.getenv("GROQ_API_KEY2", ""),
    3: os.getenv("GROQ_API_KEY3", ""),
    4: os.getenv("GROQ_API_KEY4", ""),
    5: os.getenv("GROQ_API_KEY5", ""),
    6: os.getenv("GROQ_API_KEY6", ""),
    7: os.getenv("GROQ_API_KEY7", ""),
}

# Fallback/Default key
GROQ_API_KEY = GROQ_API_KEYS[1] or os.getenv("GROQ_API_KEY", "")