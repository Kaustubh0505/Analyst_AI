import json
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm
from memory.memory_store import format_memory_for_prompt, append_memory


def qa_agent(state: AnalystState) -> dict:
    """
    Agent 6 — Q&A Agent (Enhanced Version)
    - Better intent classification
    - Strong follow-up resolution
    - High-quality analytical answers
    """

    user_query = state.get("user_query", "")
    session_id = state.get("session_id", "default")
    insights = state.get("insights", [])
    eda_results = state.get("eda_results", {})

    # -------------------------------
    # 1. Intent Classification
    # -------------------------------
    classification_prompt = f"""
You are an intent classification system for a data analysis assistant.

Your job is to classify the user's message into ONE of the following categories:

1. question → Asking about data, insights, trends, explanations
2. manipulation → Asking to modify, filter, sort, or transform data

-------------------------
RULES:
-------------------------
Classify as "question" if:
- Asking about insights, meaning, trends, comparisons
- Asking "why", "what", "how", "which"
- Follow-ups like "What about 2022?", "And revenue?"

Classify as "manipulation" if:
- Asking to filter, group, sort, or transform data
- Asking to create new columns or recompute results

-------------------------
EDGE CASE:
If unsure → return "question"

-------------------------
User Message:
"{user_query}"

Respond with ONLY one word:
question OR manipulation
"""

    try:
        intent_raw = invoke_llm(classification_prompt, agent_id=5).strip().lower()
    except Exception:
        intent_raw = "question"

    if intent_raw not in ["question", "manipulation"]:
        query_intent = "question"
    else:
        query_intent = intent_raw

    updates = {"query_intent": query_intent}

    # -------------------------------
    # 2. Handle Question
    # -------------------------------
    if query_intent == "question":

        # -------------------------------
        # Step 1: Query Resolution
        # -------------------------------
        memory_context = format_memory_for_prompt(session_id)

        resolution_prompt = f"""
You are an intelligent assistant that converts user queries into clear, standalone analytical questions.

-------------------------
INSTRUCTIONS:
-------------------------
- If already clear → return as-is
- If follow-up → expand using history
- Preserve original intent EXACTLY
- Do NOT add assumptions

-------------------------
EXAMPLES:
-------------------------
History: "Show revenue by year"
User: "And for 2022?"
→ "What is the revenue for 2022?"

History: "Top products by sales"
User: "What about profit?"
→ "What is the profit for the top products?"

-------------------------
Conversation History:
{memory_context}

Latest User Message:
"{user_query}"

-------------------------
OUTPUT:
Return ONLY the rewritten standalone question.
"""

        try:
            resolved_query = invoke_llm(resolution_prompt, agent_id=5).strip()
            print(f"Resolved Query: {resolved_query}")
        except Exception:
            resolved_query = user_query

        # -------------------------------
        # Step 2: Answer Generation
        # -------------------------------

        # Trim memory
        if len(memory_context) > 2000:
            memory_context = memory_context[-2000:]

        # Trim EDA
        eda_json = json.dumps(eda_results, indent=2, default=str)
        if len(eda_json) > 3000:
            eda_json = eda_json[:3000] + "..."

        insights_text = "\n".join(insights)

        answer_prompt = f"""
You are a highly experienced senior data analyst.

You are answering a user's question STRICTLY based on provided dataset analysis.

-------------------------
STRICT RULES:
-------------------------
- Use ONLY the provided context (EDA + insights)
- DO NOT hallucinate
- DO NOT assume missing values
- If insufficient data → say "Not enough data available"

-------------------------
HOW TO ANSWER:
-------------------------
1. Start with a direct answer
2. Support with data (numbers, %, column names)
3. Add brief interpretation (why it matters)
4. Keep it concise (2–5 sentences)

-------------------------
CONTEXT:
-------------------------

Conversation Summary:
{memory_context}

EDA Summary:
{eda_json}

Key Insights:
{insights_text}

-------------------------
USER QUESTION:
{resolved_query}

-------------------------
OUTPUT:
Only return the final answer.
"""

        try:
            answer = invoke_llm(answer_prompt, agent_id=5)
        except Exception as e:
            answer = f"Error generating answer: {str(e)}"

        # -------------------------------
        # Step 3: Store Memory
        # -------------------------------
        append_memory(session_id, {
            "question": user_query,
            "answer": answer,
            "intent": "question"
        })

        updates["answer"] = answer

    # -------------------------------
    # 3. Handle Manipulation
    # -------------------------------
    else:
        updates["message"] = (
            "This request involves data manipulation. "
            "Please route it to the transformation agent."
        )

    return updates