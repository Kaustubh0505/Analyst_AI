from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY

_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=GEMINI_API_KEY,
)


def invoke_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = _llm.invoke(prompt)
    return response.content
