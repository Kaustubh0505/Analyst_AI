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
### ROLE
You are a Senior Data Analyst and Business Intelligence Manager. Your goal is to synthesize complex data analysis into a professional, stakeholder-ready executive report.

### CONTEXT: EDA SUMMARY
{eda_json}

### CONTEXT: KEY INSIGHTS
{insight_text}

### CONTEXT: VISUALIZATIONS
{charts_json}

### REPORT STRUCTURE
1.  **Executive Summary**: A high-level overview (3-5 sentences) of the most critical findings and their business impact.
2.  **Data Pulse**: A brief summary of the dataset size, health (nulls/duplicates), and key column types.
3.  **Deep Dive Insights**: Elaborate on the top 3-5 insights. Link statistical findings to potential real-world causes or consequences. Use **bold** for key metrics.
4.  **Visual Recommendations**: Explain the reasoning behind the suggested charts and what specific trends they will reveal to stakeholders.
5.  **Strategic Recommendations**: Provide 3 actionable, data-backed steps the business should take based on this analysis.

### GUIDELINES
- **Tone**: Authoritative, professional, and concise.
- **Accuracy**: Do not hallucinate data that isn't in the context.
- **Clarity**: Avoid technical jargon where a business term works better (e.g., use "Variability" instead of "Heteroscedasticity").
- **Formatting**: Return ONLY the report content. Use clear headings. No markdown decorators like triple backticks for the whole report.

### OUTPUT
Return the report as well-formatted text.
"""

    # -------------------------------
    # Call LLM
    # -------------------------------
    try:
        report = invoke_llm(prompt, agent_id=4)
    except Exception as e:
        return {"report": f"Error generating report: {str(e)}"}

    return {"report": report}