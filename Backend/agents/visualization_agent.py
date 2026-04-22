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
### ROLE
You are a Senior Data Visualization Expert. Your goal is to design a set of charts for an executive dashboard that reveal the most critical insights from the dataset.

### EDA CONTEXT (JSON)
{eda_json}

### DESIGN PRINCIPLES
1.  **Relevance**: Only suggest charts for columns with significant variance or important business metrics.
2.  **Clarity**: Avoid dense scatter plots if there are >500 data points; use histograms instead.
3.  **Appropriateness**:
    *   `histogram`: Price distributions, quantity ranges.
    *   `bar`: Sales by Category, Count by Region.
    *   `line`: Revenue over Time (requires date column).
    *   `scatter`: Relationship between two numeric variables (e.g., Discount vs. Profit).
    *   `pie`: ONLY for small segments (e.g., Gender, Yes/No).
    *   `heatmap`: Correlation matrix for all numeric columns.

### STRICT OUTPUT FORMAT
Return ONLY a valid JSON array of objects. No intro, no markdown blocks, no code fences.
[
  {{
    "type": "bar|line|scatter|histogram|pie|heatmap",
    "x": "column_name",
    "y": "column_name (required for bar, line, scatter)",
    "title": "A descriptive, insight-focused title"
  }}
]

### GUARDRAILS
- Use ONLY exact column names from the context.
- Maximum 6 high-quality suggestions.
- Do NOT provide an intro or outro.
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