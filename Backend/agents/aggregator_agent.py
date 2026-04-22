import json
import pandas as pd
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm

def aggregator_agent(state: AnalystState) -> dict:
    """
    Agent 7 — Aggregator & Insight Discovery Agent
    1. Summarizes data for suggested charts.
    2. Discovers new insights through multi-column grouping.
    """
    df: pd.DataFrame = state.get("cleaned_data")
    if df is None:
        return {"aggregated_charts": [], "grouped_insights": []}

    charts = state.get("charts", [])
    eda_results = state.get("eda_results", {})
    
    # ---------------------------------------------------------
    # 1. Insight Discovery via Grouping
    # ---------------------------------------------------------
    discovery_prompt = f"""
### ROLE
You are a Lead Data Analyst. Your task is to identify the most commercially significant groupings in this dataset.

### DATA CONTEXT (EDA)
{json.dumps(eda_results, indent=2, default=str)}

### TASK
Identify 3-5 column combinations for grouping that would reveal high-value trends (e.g., 'Category' vs 'Revenue', or 'Region' vs 'Customer_Count').

### OUTPUT FORMAT (JSON ONLY)
[
  {{
    "group_by": "column_name",
    "target": "column_name",
    "agg": "sum|mean|count",
    "reason": "Why this grouping matters"
  }}
]
"""
    discovery_findings = []
    try:
        discovery_res = invoke_llm(discovery_prompt, agent_id=7)
        # Attempt to parse
        import re
        match = re.search(r"\[.*\]", discovery_res, re.DOTALL)
        if match:
            grouping_plans = json.loads(match.group())
            for plan in grouping_plans:
                g_col = plan.get("group_by")
                t_col = plan.get("target")
                agg_func = plan.get("agg", "count")
                
                if g_col in df.columns and (t_col in df.columns or agg_func == "count"):
                    # Perform aggregation
                    if agg_func == "count":
                        agg_df = df.groupby(g_col).size().reset_index(name="count")
                    else:
                        agg_df = df.groupby(g_col).agg({t_col: agg_func}).reset_index()
                    
                    # Sort and take top 10
                    agg_df = agg_df.sort_values(by=agg_df.columns[1], ascending=False).head(10)
                    
                    # Generate a natural language insight based on the result
                    peak_val = agg_df.iloc[0, 0]
                    peak_num = agg_df.iloc[0, 1]
                    discovery_findings.append(
                        f"**{g_col.title()} Analysis**: '{peak_val}' leads with {peak_num} ({agg_func}). {plan.get('reason')}"
                    )
    except Exception as e:
        print(f"Discovery phase failed: {e}")

    # ---------------------------------------------------------
    # 2. Chart Aggregation
    # ---------------------------------------------------------
    aggregated_charts = []
    for chart in charts:
        ctype = chart.get("type")
        x = chart.get("x")
        y = chart.get("y")
        
        try:
            if ctype in ["bar", "pie"]:
                # Grouped aggregation
                if y and y in df.columns and x in df.columns:
                    # Determine agg method based on column name or default to sum
                    method = "sum" if "revenue" in y.lower() or "sales" in y.lower() or "price" in y.lower() else "mean"
                    agg_df = df.groupby(x)[y].agg(method).reset_index()
                elif x in df.columns:
                    agg_df = df.groupby(x).size().reset_index(name="Count")
                    y = "Count"
                else:
                    continue
                
                # Sort and Limit
                agg_df = agg_df.sort_values(by=y, ascending=False).head(15)
                chart_data = agg_df.to_dict(orient="records")
                
            elif ctype == "histogram":
                # Raw distribution data for histograms is usually better, 
                # but we'll send a larger sample (up to 2000) instead of current 25
                if x in df.columns:
                    chart_data = df[[x]].dropna().head(2000).to_dict(orient="records")
                else:
                    continue
                    
            elif ctype == "line":
                # Group by X (usually time) and aggregate Y
                if x in df.columns and y in df.columns:
                    agg_df = df.groupby(x)[y].mean().reset_index()
                    chart_data = agg_df.to_dict(orient="records")
                else:
                    continue
            
            elif ctype == "scatter":
                # Sample for scatter plots to keep it clean
                if x in df.columns and y in df.columns:
                    chart_data = df[[x, y]].dropna().head(1000).to_dict(orient="records")
                else:
                    continue
            
            else:
                # Fallback for heatmap etc (handled by frontend normally)
                chart_data = []

            aggregated_charts.append({
                "spec": chart,
                "data": chart_data
            })
            
        except Exception as e:
            print(f"Aggregation for chart {chart.get('title')} failed: {e}")
            aggregated_charts.append({"spec": chart, "data": []})

    return {
        "aggregated_charts": aggregated_charts,
        "grouped_insights": discovery_findings
    }
