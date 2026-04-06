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
        response = invoke_llm(prompt, agent_id=2)
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
        # Try a more aggressive search if [ ] markers weren't found nicely
        match_alt = re.search(r"(\[.*\])", response, re.DOTALL)
        if match_alt:
            try:
                charts = json.loads(match_alt.group(1))
            except Exception:
                charts = []
        else:
            charts = []

    # Validate charts
    valid_types = {"bar", "line", "scatter", "histogram", "pie", "heatmap"}
    actual_columns = eda_results.get("columns", [])
    col_map = {c.lower(): c for c in actual_columns}

    validated_charts = []
    for chart in charts:
        if not isinstance(chart, dict):
            continue

        ctype = chart.get("type", "").lower()
        if ctype not in valid_types:
            continue
        
        # Ensure type is normalized
        chart["type"] = ctype

        x = chart.get("x")
        y = chart.get("y")

        # Support list inputs (take first item)
        if isinstance(x, list) and len(x) > 0: x = x[0]
        if isinstance(y, list) and len(y) > 0: y = y[0]

        # Case-insensitive column matching for x
        if isinstance(x, str) and x.lower() in col_map:
            chart["x"] = col_map[x.lower()]
        else:
            continue # x is mandatory

        # Use y if available, validate it case-insensitively
        if isinstance(y, str) and y.lower() in col_map:
            chart["y"] = col_map[y.lower()]
        elif ctype in ["histogram", "pie"]:
            # y can be optional for these types, we can use a count or let the UI handle it
            pass
        else:
            # If y is missing for bar/line/scatter/heatmap, it's invalid
            if ctype in ["bar", "line", "scatter", "heatmap"]:
                continue

        validated_charts.append(chart)

    return {"charts": validated_charts}