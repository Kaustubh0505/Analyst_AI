from typing import List, Dict


# In-memory store: session_id -> list of {question, answer, intent}
_store: Dict[str, List[dict]] = {}


def get_memory(session_id: str) -> List[dict]:
    return _store.get(session_id, [])


def append_memory(session_id: str, entry: dict) -> None:
    if session_id not in _store:
        _store[session_id] = []
    _store[session_id].append(entry)


def clear_memory(session_id: str) -> None:
    _store[session_id] = []


def format_memory_for_prompt(session_id: str, n: int = 5) -> str:
    """Return the last N memory entries as a formatted string for LLM context."""
    history = get_memory(session_id)[-n:]
    if not history:
        return "No prior conversation history."
    lines = []
    for entry in history:
        lines.append(f"User: {entry['question']}")
        lines.append(f"Assistant: {entry['answer']}")
    return "\n".join(lines)
    