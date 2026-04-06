import json
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def report_generator(state: AnalystState) -> dict:
    """
    Agent 5 — Report Generator (Enhanced)
    Generates a professional, stakeholder-ready analytical report.
    """

    insights = state.get("insights", [])
    eda_results = state.get("eda_results", {})
    charts = state.get("charts", [])

    # -------------------------------
    # Truncate large inputs
    # -------------------------------
    eda_json = json.dumps(eda_results, indent=2, default=str)
    charts_json = json.dumps(charts, indent=2)

    if len(eda_json) > 6000:
        eda_json = eda_json[:6000] + "..."

    if len(charts_json) > 2000:
        charts_json = charts_json[:2000] + "..."

    # -------------------------------
    # Clean insights formatting
    # -------------------------------
    insight_text = "\n".join(
        f"{i+1}. {insight}" if not insight.strip().startswith(str(i+1)) else insight
        for i, insight in enumerate(insights)
    )

    # -------------------------------
    # 🔥 Enhanced Prompt
    # -------------------------------
    prompt = f"""
You are a senior data analyst preparing a professional business report for stakeholders.

Your goal is to transform raw analysis into clear, decision-oriented insights.

-------------------------
REPORT OBJECTIVE:
-------------------------
- Help stakeholders understand what is happening in the data
- Highlight key risks, opportunities, and trends
- Provide actionable recommendations

-------------------------
STRICT INSTRUCTIONS:
-------------------------
- DO NOT repeat raw JSON
- DO NOT list data blindly
- Focus on interpretation, not just observation
- Prioritize the MOST important findings
- Use numbers, percentages, and comparisons where possible

-------------------------
HOW TO WRITE:
-------------------------
- Be concise but insightful
- Use professional, business-friendly language
- Each section should add value (no fluff)
- Link findings → implications → actions

-------------------------
INPUT DATA:
-------------------------

EDA Summary:
{eda_json}

Key Insights:
{insight_text}

Suggested Visualizations:
{charts_json}

-------------------------
OUTPUT STRUCTURE:
-------------------------

1. Executive Summary
- 3–5 sentences summarizing the most critical findings
- Include major trends and key takeaway

2. Dataset Overview
- Brief description of dataset (columns, types, size if available)

3. Key Findings
- Expand top insights (NOT all)
- Combine related insights
- Include numbers and comparisons
- Highlight anomalies or unexpected patterns

4. Visualizations
- Explain WHY each chart is useful
- Link charts to insights (not just listing them)

5. Recommendations
- Provide 3–5 actionable recommendations
- Based on data (not generic advice)
- Focus on business impact

-------------------------
OUTPUT:
-------------------------
Return clean, well-structured text.
No markdown. No JSON.
"""

    # -------------------------------
    # Call LLM
    # -------------------------------
    try:
        report = invoke_llm(prompt, agent_id=4)
    except Exception as e:
        return {"report": f"Error generating report: {str(e)}"}

    return {"report": report}