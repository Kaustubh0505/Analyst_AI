from langchain_google_genai import ChatGoogleGenerativeAI
from config import GEMINI_API_KEY

_llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    google_api_key=GEMINI_API_KEY,
)


def invoke_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response as a plain string.

    response.content can be:
      - str  → returned as-is
      - list → each element is either a str or a dict with a 'text' key;
               join all text parts into one string.
    """
    response = _llm.invoke(prompt)
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
