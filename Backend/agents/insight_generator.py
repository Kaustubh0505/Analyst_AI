import json
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def insight_generator(state: AnalystState) -> dict:
    """
    Agent 3 — Insight Generator
    Calls Gemini to generate human-readable analyst insights from EDA results.
    """

    eda_results = state["eda_results"]

    eda_json = json.dumps(eda_results, indent=2, default=str)

    # Prevent token overflow
    if len(eda_json) > 8000:
        eda_json = eda_json[:8000] + "..."

    prompt = f"""
You are a senior data analyst.

Analyze the following EDA results and generate 5–7 high-quality insights.

Guidelines:
- Be specific and reference column names
- Include numbers, percentages, or trends
- Highlight anomalies, correlations, and distributions
- Avoid generic statements

EDA Results:
{eda_json}

Return ONLY a numbered list:
1. ...
2. ...
"""

    try:
        response = invoke_llm(prompt, agent_id=3)
    except Exception as e:
        return {"insights": [f"LLM Error: {str(e)}"]}

    # Robust parsing
    lines = [
        line.strip()
        for line in response.strip().split("\n")
        if re.match(r"^\d+[\).\-\s]", line.strip())
    ]

    insights = lines if lines else [response.strip()]

    return {"insights": insights}