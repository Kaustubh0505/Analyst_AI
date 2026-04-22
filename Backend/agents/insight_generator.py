import json
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm

def insight_generator(state: AnalystState) -> dict:
    """
    Agent 3 — Insight Generator
    Enhanced prompt with persona-driven reasoning and structured analytical layers.
    """
    eda_results = state["eda_results"]
    eda_json = json.dumps(eda_results, indent=2, default=str)

    # Prevent token overflow while maintaining data integrity
    if len(eda_json) > 12000: # Increased slightly if model window allows
        eda_json = eda_json[:12000] + "\n... [Data Truncated]"

    prompt = f"""
### ROLE
You are a Lead Data Scientist and Strategic Business Consultant. Your task is to extract hidden patterns, anomalies, and strategic opportunities from Exploratory Data Analysis (EDA) results.

### INPUT DATA (JSON)
{eda_json}

### ANALYTICAL FRAMEWORK
1.  **Macro Trends**: What is the "big picture" story the data is telling?
2.  **Anomalies & Risks**: Identify unexpected nulls, extreme outliers, or suspicious zeros that could invalidate analysis.
3.  **Segment Behavior**: Look for concentration risk (e.g., 80/20 rule) in distributions or categorical counts.
4.  **Actionable Intelligence**: Translate every statistical finding into a "So What?" for a business owner.

### CONSTRAINTS
- **Quantification**: Use exact numbers from the EDA. Do not guess.
- **Precision**: Reference column names in **bold**.
- **Tone**: Critical, professional, and insight-dense.
- **Structure**: Return a numbered list of 5-7 high-quality insights.
- **Guardrails**: Return ONLY the list. No introduction or concluding remarks.

### OUTPUT EXAMPLE
1. **Revenue** is highly skewed (Skew: 4.2), with 75% of total sales coming from the 'North' region, indicating a heavy geographical dependency.
2. The **conversion_rate** shows a negative correlation (-0.45) with **page_load_time**, suggesting technical performance is directly impacting sales.
"""

    try:
        response = invoke_llm(prompt, agent_id=3)
    except Exception as e:
        return {"insights": [f"LLM Error: {str(e)}"]}

    # Parsing logic
    lines = [
        line.strip()
        for line in response.strip().split("\n")
        if re.match(r"^\d+[\).\-\s]", line.strip())
    ]

    insights = lines if lines else [response.strip()]
    return {"insights": insights}