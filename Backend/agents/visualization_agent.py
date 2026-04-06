import json
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def visualization_agent(state: AnalystState) -> dict:
    """
    Agent 4 — Visualization Agent (Enhanced)
    Generates high-quality, valid chart suggestions.
    """

    eda_results = state["eda_results"]

    # -------------------------------
    # Prepare EDA JSON (trim if large)
    # -------------------------------
    eda_json = json.dumps(eda_results, indent=2, default=str)

    if len(eda_json) > 8000:
        eda_json = eda_json[:8000] + "..."

    # -------------------------------
    # 🔥 Improved Prompt
    # -------------------------------
    prompt = f"""
You are a senior data visualization expert designing charts for a data analyst dashboard.

Your goal is to recommend the MOST INSIGHTFUL charts based on the dataset.

-------------------------
STRICT THINKING PROCESS:
-------------------------
For each chart:
1. Identify column types (numerical, categorical, datetime)
2. Choose ONLY meaningful column combinations
3. Ensure the chart reveals trends, patterns, or comparisons
4. Avoid random or meaningless pairings

-------------------------
CHART RULES:
-------------------------
- histogram → distribution of a numeric column
- bar → categorical vs numeric comparison
- line → trends over time (requires datetime)
- scatter → relationship between two numeric columns
- pie → proportions (ONLY if categories < 6)
- heatmap → correlation matrix (numeric columns only)

-------------------------
STRICT CONSTRAINTS:
-------------------------
- ONLY use existing column names
- DO NOT hallucinate columns
- DO NOT repeat similar charts
- Each chart must provide UNIQUE insight
- Prefer high-variance or important columns

-------------------------
EDA RESULTS:
-------------------------
{eda_json}

-------------------------
OUTPUT FORMAT (STRICT JSON ONLY):
-------------------------
[
  {{
    "type": "bar|line|scatter|histogram|pie|heatmap",
    "x": "column_name",
    "y": "column_name (if applicable)",
    "title": "Insightful chart title"
  }}
]

Return ONLY JSON. No explanation.
"""

    # -------------------------------
    # Call LLM
    # -------------------------------
    try:
        response = invoke_llm(prompt, agent_id=2)
        # Debug (optional)
        # print("RAW RESPONSE:\n", response)
    except Exception as e:
        return {"charts": [], "error": str(e)}

    # -------------------------------
    # Extract JSON safely
    # -------------------------------
    charts = []

    try:
        # Try direct parse
        charts = json.loads(response)
    except Exception:
        # Fallback regex extraction
        match = re.search(r"\[.*\]", response, re.DOTALL)
        if match:
            try:
                charts = json.loads(match.group())
            except Exception:
                charts = []
        else:
            charts = []

    # -------------------------------
    # Validation
    # -------------------------------
    valid_types = {"bar", "line", "scatter", "histogram", "pie", "heatmap"}
    actual_columns = eda_results.get("columns", [])

    # Case-insensitive mapping
    col_map = {c.lower(): c for c in actual_columns}

    validated_charts = []
    seen = set()

    for chart in charts:
        if not isinstance(chart, dict):
            continue

        ctype = chart.get("type", "").lower()

        if ctype not in valid_types:
            continue

        x = chart.get("x")
        y = chart.get("y")

        # Normalize x
        if isinstance(x, list) and x:
            x = x[0]

        if not isinstance(x, str) or x.lower() not in col_map:
            continue

        x = col_map[x.lower()]

        # Normalize y
        if isinstance(y, list) and y:
            y = y[0]

        if isinstance(y, str) and y.lower() in col_map:
            y = col_map[y.lower()]
        else:
            y = None

        # Chart-specific validation
        if ctype in ["bar", "line", "scatter"]:
            if not y:
                continue

        if ctype == "heatmap":
            # Allow heatmap without x/y (UI can handle correlation matrix)
            x, y = None, None

        if ctype in ["histogram", "pie"]:
            # y optional
            pass

        # Avoid duplicates
        key = (ctype, x, y)
        if key in seen:
            continue
        seen.add(key)

        validated_charts.append({
            "type": ctype,
            "x": x,
            "y": y,
            "title": chart.get("title", f"{ctype.title()} Chart")
        })

    return {"charts": validated_charts}