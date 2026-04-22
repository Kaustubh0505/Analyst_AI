from langchain_groq import ChatGroq
from config import GROQ_API_KEY

_llm = None

def get_llm():
    """Get or create the Groq LLM instance."""
    global _llm
    if _llm is None:
        _llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=GROQ_API_KEY,
            temperature=0.1,
        )
    return _llm


def invoke_llm(prompt: str, agent_id: int = 1) -> str:
    """
    Send a prompt to Groq and return the response.
    agent_id is kept for backward compatibility but ignored.
    """
    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content
