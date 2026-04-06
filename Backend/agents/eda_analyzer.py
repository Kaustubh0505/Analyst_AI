import pandas as pd
from state.analyst_state import AnalystState


def eda_analyzer(state:AnalystState) -> dict:
    """
    Agent 2 — EDA Analyzer
    Computes descriptive stats, correlations, value counts, and skewness.
    """

    df:pd.DataFrame = state["cleaned_data"]

    numeric_df = df.select_dtypes(include=["number"])

    eda_results = {
        "shape":{"rows":df.shape[0],"cols":df.shape[1]},
        "columns":list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "describe": numeric_df.describe().to_dict() if not numeric_df.empty else {},
        "null_counts": df.isnull().sum().to_dict(),
        "correlation": (
            numeric_df.corr().to_dict() if numeric_df.shape[1] > 1 else {}
        ),
        "skewness": numeric_df.skew().to_dict() if not numeric_df.empty else {},
        "value_counts": {
            col: df[col].value_counts().head(10).to_dict()
            for col in df.select_dtypes(include="object").columns
        },
        "data_sample": df.head(25).to_dict(orient="records"),
    }

    return {"eda_results": eda_results}
