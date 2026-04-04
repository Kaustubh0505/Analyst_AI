import pandas as pd
from state.analyst_state import AnalystState


def data_cleaner(state: AnalystState) -> dict:
    """
    Agent 1 — Data Cleaner
    - Drop duplicate rows
    - Fill or drop missing values
    - Fix column data types
    """

    df: pd.DataFrame = state["raw_data"]

    df = df.drop_duplicates()

    df = df.dropna(axis=1, how="all")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            mode = df[col].mode()
            if not mode.empty:
                df[col] = df[col].fillna(mode[0])

    for col in df.select_dtypes(include="object").columns:
        try:
            df[col] = pd.to_datetime(df[col], errors="ignore")
        except Exception:
            pass

    return {"cleaned_data": df}