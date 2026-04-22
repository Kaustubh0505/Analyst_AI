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
### ROLE
You are an Intent Classification System for a Data Analysis Assistant.

### TASK
Classify the user's message into EXACTLY one of these categories:
- `question` → Requests for information, insights, trends, or data explanations.
- `manipulation` → Requests to filter, sort, group, transform, or modify the dataset structure.

### CLASSIFICATION CRITERIA
1. **question**:
   - "How many sales were made?"
   - "What is the average price?"
   - "Why did revenue drop in Q3?"
   - "Compare product A and B."
2. **manipulation**:
   - "Remove the ID column."
   - "Filter for values above 100."
   - "Group by city and sum sales."
   - "Rename 'col1' to 'Price'."

### EDGE CASES
- If the user asks a follow-up that implies data exploration (e.g., "And for 2023?"), classify as `question`.
- If unsure, default to `question`.

### USER MESSAGE
"{user_query}"

### OUTPUT
Return ONLY the word `question` or `manipulation`.
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
### ROLE
You are a Query Resolution Specialist. You convert conversational follow-ups into standalone, self-explanatory analytical questions.

### CONTEXT
- History helps understand pronouns (it, they, them) and implicit filters.
- Latest user message might be a fragment.

### HISTORY
{memory_context}

### LATEST USER MESSAGE
"{user_query}"

### TASK
Rewrite the latest message into a standalone question that can be understood without history. 
- Preserve the original analytical intent.
- Do NOT add new analysis.
- If it's already standalone, return it as-is.

### OUTPUT
Return ONLY the rewritten question.
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
### ROLE
You are a Senior Data Analyst providing insights directly to a CEO. Your answers must be accurate, data-driven, and business-focused.

### CONTEXT: EDA SUMMARY
{eda_json}

### CONTEXT: KEY INSIGHTS
{insights_text}

### PREVIOUS CONVERSATION
{memory_context}

### USER QUESTION
{resolved_query}

### GUIDELINES
1.  **Strict Accuracy**: Bases answers ONLY on the provided context. If the data is missing, say "I don't have enough data to answer that."
2.  **No Hallucinations**: Do not invent numbers or trends.
3.  **Specifics**: Reference specific columns and values. Use percentages or deltas if available.
4.  **Formatting**: Use bold text for key figures. Keep responses to 2-4 concise sentences.
5.  **Guardrails**: Do not provide advice outside of data analysis. Do not mention the context JSON in your response.

### OUTPUT
Return ONLY the final analytical answer.
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