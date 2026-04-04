import json
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def visualization_agent(state: AnalystState) -> dict:
    """
    Agent 4 — Visualization Agent
    Suggests the best charts and returns structured JSON specs.
    """

    eda_results = state["eda_results"]

    eda_json = json.dumps(eda_results, indent=2, default=str)

    if len(eda_json) > 8000:
        eda_json = eda_json[:8000] + "..."

    prompt = f"""
You are a senior data visualization expert.

Based on the EDA results, recommend 3–5 highly informative charts.

Guidelines:
- Use numeric columns for scatter/line/histogram
- Use categorical columns for bar/pie charts
- Use heatmap ONLY for correlations
- Avoid redundant charts
- Prefer charts that reveal trends, distributions, or relationships

EDA Results:
{eda_json}

Return ONLY a valid JSON array:
[
  {{
    "type": "bar|line|scatter|histogram|pie|heatmap",
    "x": "...",
    "y": "...",
    "title": "..."
  }}
]
"""

    try:
        response = invoke_llm(prompt)
    except Exception as e:
        return {"charts": [], "error": str(e)}

    # Extract JSON safely
    match = re.search(r"\[.*\]", response, re.DOTALL)
    if match:
        try:
            charts = json.loads(match.group())
        except Exception:
            charts = []
    else:
        charts = []

    # Validate charts
    valid_types = {"bar", "line", "scatter", "histogram", "pie", "heatmap"}
    columns = set(eda_results.get("columns", []))

    validated_charts = []
    for chart in charts:
        if not isinstance(chart, dict):
            continue

        if chart.get("type") not in valid_types:
            continue

        x = chart.get("x")
        y = chart.get("y")

        if x and x not in columns:
            continue
        if y and y not in columns:
            continue

        validated_charts.append(chart)

    return {"charts": validated_charts}