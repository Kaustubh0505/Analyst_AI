import json
import re
import pandas as pd
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm
from memory.memory_store import append_memory


def data_manipulator(state: AnalystState) -> dict:

    user_query = state.get("user_query", "")
    session_id = state.get("session_id", "default")

    df: pd.DataFrame = state.get("manipulated_data") or state.get("cleaned_data")
    columns = list(df.columns)

    plan_prompt = f"""
You are a data transformation assistant.

Available columns:
{columns}

User instruction:
"{user_query}"

Return ONLY valid JSON.
"""

    try:
        plan_raw = invoke_llm(plan_prompt, agent_id=6).strip()
    except Exception as e:
        return {
            "manipulated_data": df,
            "manipulation_plan": {},
            "answer": f"Error generating plan: {str(e)}"
        }

    match = re.search(r"\{.*\}", plan_raw, re.DOTALL)
    if match:
        try:
            manipulation_plan = json.loads(match.group())
        except:
            manipulation_plan = {}
    else:
        manipulation_plan = {}

    action = manipulation_plan.get("action", "")

    valid_actions = {
        "drop_columns",
        "filter_rows",
        "rename_columns",
        "fill_nulls",
        "drop_duplicates"
    }

    if action not in valid_actions:
        action = ""

    try:
        if action == "filter_rows":
            condition = manipulation_plan.get("condition", "")
            before = len(df)
            try:
                df = df.query(condition, engine="python")
                confirmation = f"Filtered rows from {before} to {len(df)}."
            except:
                confirmation = f"Invalid filter condition: {condition}"

        elif action == "fill_nulls":
            col = manipulation_plan.get("column", "")
            strategy = manipulation_plan.get("strategy", "mean")

            if col in df.columns:
                if strategy == "mean":
                    df[col] = df[col].fillna(df[col].mean())
                elif strategy == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif strategy == "mode":
                    mode = df[col].mode()
                    if not mode.empty:
                        df[col] = df[col].fillna(mode[0])
                elif strategy == "zero":
                    df[col] = df[col].fillna(0)

            confirmation = f"Filled nulls in {col} using {strategy}."

        elif action == "drop_columns":
            cols_to_drop = manipulation_plan.get("columns", [])
            valid_cols = [c for c in cols_to_drop if c in df.columns]
            df = df.drop(columns=valid_cols)
            confirmation = f"Dropped columns: {valid_cols}."

        elif action == "rename_columns":
            mapping = manipulation_plan.get("mapping", {})
            df = df.rename(columns={k: v for k, v in mapping.items() if k in df.columns})
            confirmation = f"Renamed columns: {mapping}."

        elif action == "drop_duplicates":
            before = len(df)
            df = df.drop_duplicates()
            confirmation = f"Removed {before - len(df)} duplicate rows."

        else:
            confirmation = "Could not understand the manipulation."

    except Exception as e:
        confirmation = f"Error applying transformation: {str(e)}"

    append_memory(session_id, {
        "question": user_query,
        "answer": confirmation,
        "intent": "manipulation",
        "plan": manipulation_plan,
    })

    return {
        "manipulated_data": df,
        "manipulation_plan": manipulation_plan,
        "answer": confirmation,
    }