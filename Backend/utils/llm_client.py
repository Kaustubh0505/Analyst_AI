from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEYS

# Cache for LLM instances by agent_id
_llm_instances = {}

def get_llm(agent_id: int = 1) -> ChatGoogleGenerativeAI:
    """Get or create an LLM instance for a specific agent index."""
    # Ensure agent_id is within bounds (1-indexed matching GEMINI_API_KEY1...)
    idx = max(0, min(agent_id - 1, len(GEMINI_API_KEYS) - 1))
    
    if idx not in _llm_instances:
        # Fallback to first key if the designated one is empty
        api_key = GEMINI_API_KEYS[idx] or GEMINI_API_KEYS[0]
        
        _llm_instances[idx] = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite",
            google_api_key=api_key,
        )
    return _llm_instances[idx]


def invoke_llm(prompt: str, agent_id: int = 1) -> str:
    """Send a prompt to Gemini using an agent-specific key and return response."""
    llm = get_llm(agent_id)
    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, str):
        return content

    # Multi-part response — extract text from each part and join
    parts = []
    for part in content:
        if isinstance(part, str):
            parts.append(part)
        elif isinstance(part, dict) and "text" in part:
            parts.append(part["text"])
    return "\n".join(parts)
