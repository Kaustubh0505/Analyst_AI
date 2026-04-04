import json
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm
from memory.memory_store import format_memory_for_prompt, append_memory


def qa_agent(state: AnalystState) -> dict:
    """
    Agent 6 — Q&A Agent
    """

    user_query = state.get("user_query", "")
    session_id = state.get("session_id", "default")
    insights = state.get("insights", [])
    eda_results = state.get("eda_results", {})


    classification_prompt = f"""
Classify the following user message into one of two categories:
- question
- manipulation

User message: "{user_query}"

Respond with ONLY one word.
"""

    try:
        intent_raw = invoke_llm(classification_prompt).strip().lower()
    except Exception:
        intent_raw = "question"

    if intent_raw not in ["question", "manipulation"]:
        query_intent = "question"
    else:
        query_intent = intent_raw

    updates = {"query_intent": query_intent}

    # --- Handle Question ---
    if query_intent == "question":

        memory_context = format_memory_for_prompt(session_id)
        if len(memory_context) > 2000:
            memory_context = memory_context[-2000:]

        eda_json = json.dumps(eda_results, indent=2, default=str)
        if len(eda_json) > 3000:
            eda_json = eda_json[:3000] + "..."

        answer_prompt = f"""
You are a senior data analyst answering questions about a dataset.

Use ONLY the provided context. Do not hallucinate.

Guidelines:
- Be concise and precise
- Reference column names and values where possible
- If unsure, say so clearly

Conversation History:
{memory_context}

EDA Summary:
{eda_json}

Key Insights:
{chr(10).join(insights)}

User Question:
{user_query}

Answer:
"""

        try:
            answer = invoke_llm(answer_prompt)
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"

        append_memory(session_id, {
            "question": user_query,
            "answer": answer,
            "intent": "question"
        })

        updates["answer"] = answer

    else:
        updates["message"] = "This request involves data manipulation. Route to transformation agent."

    return updates