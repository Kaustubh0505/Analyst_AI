import json
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def report_generator(state: AnalystState) -> dict:
    """
    Agent 5 — Report Generator
    Compiles insights, EDA results, and chart specs into a structured analyst report.
    """

    insights = state.get("insights", [])
    eda_results = state.get("eda_results", {})
    charts = state.get("charts", [])

    # Truncate large inputs
    eda_json = json.dumps(eda_results, indent=2, default=str)
    charts_json = json.dumps(charts, indent=2)

    if len(eda_json) > 6000:
        eda_json = eda_json[:6000] + "..."

    if len(charts_json) > 2000:
        charts_json = charts_json[:2000] + "..."

    # Clean insights formatting
    insight_text = "\n".join(
        f"{i+1}. {insight}" if not insight.strip().startswith(str(i+1)) else insight
        for i, insight in enumerate(insights)
    )

    prompt = f"""
You are a senior data analyst preparing a professional business report.

Your task is to synthesize EDA results, insights, and visualization plans into a clear, structured report.

Guidelines:
- Be concise but insightful
- Use data-backed statements
- Highlight key trends, anomalies, and correlations
- Avoid repeating raw JSON
- Write in a professional tone suitable for stakeholders

EDA Summary:
{eda_json}

Key Insights:
{insight_text}

Suggested Visualizations:
{charts_json}

Structure the report as:

1. Executive Summary
2. Dataset Overview
3. Key Findings
4. Visualizations
5. Recommendations

Return clean formatted text.
"""

    try:
        report = invoke_llm(prompt, agent_id=4)
    except Exception as e:
        return {"report": f"Error generating report: {str(e)}"}

    return {"report": report}