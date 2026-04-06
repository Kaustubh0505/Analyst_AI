import pandas as pd
import numpy as np
from state.analyst_state import AnalystState


def data_cleaner(state: AnalystState) -> dict:
    """
    Agent 1 — Data Cleaner
    - Drop duplicate rows
    - Fill or drop missing values
    - Fix column data types
    """

    df: pd.DataFrame = state["raw_data"].copy()

    # 1. Basic Cleaning
    df = df.drop_duplicates()

    # 2. String Sanitization
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
        # Replace empty strings with NaN for imputation
        df[col] = df[col].replace("", np.nan)

    # 3. Robust Date Parsing
    for col in df.select_dtypes(include=["object"]).columns:
        # Try to convert to datetime - only if it actually looks like a date
        # (check if more than 50% can be converted to something that isn't NaT)
        converted = pd.to_datetime(df[col], errors="coerce")
        if not converted.isna().all() and (converted.notna().sum() / len(df) > 0.5):
            df[col] = converted

    # 4. Drop sparse columns (>80% null)
    df = df.dropna(axis=1, thresh=int(0.2 * len(df)))

    # 5. Smart Imputation
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                # Fill numeric with median
                df[col] = df[col].fillna(df[col].median())
            else:
                # Fill categorical/object with mode
                mode = df[col].mode()
                if not mode.empty:
                    df[col] = df[col].fillna(mode[0])

    # 6. Final Polish - drop any remaining rows with nulls (safety catch)
    df = df.dropna()

    return {"cleaned_data": df}