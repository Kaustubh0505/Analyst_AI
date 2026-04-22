from langchain_groq import ChatGroq
from config import GROQ_API_KEYS

# Cache for LLM instances: agent_id -> ChatGroq
_llm_cache = {}

def get_llm(agent_id: int):
    """Get or create a Groq LLM instance for a specific agent."""
    global _llm_cache
    
    if agent_id not in _llm_cache:
        api_key = GROQ_API_KEYS.get(agent_id) or GROQ_API_KEYS.get(1)
        
        _llm_cache[agent_id] = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.1,
        )
    return _llm_cache[agent_id]


def invoke_llm(prompt: str, agent_id: int = 1) -> str:
    """
    Send a prompt to Groq using the designated API key for the given agent_id.
    """
    llm = get_llm(agent_id)
    response = llm.invoke(prompt)
    return response.content
