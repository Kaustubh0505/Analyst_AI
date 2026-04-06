import pandas as pd
import numpy as np
from agents.data_cleaner import data_cleaner

def test_cleaner():
    # Create "dirty" data
    df = pd.DataFrame({
        "dates": ["2026-01-01", "04/05/2026", "invalid", np.nan],
        "numeric": [1, 2, np.nan, 100], # median should be 2
        "cats": ["A", "B", "A", np.nan],  # mode should be A
        "all_null": [np.nan, np.nan, np.nan, np.nan],
        "mostly_null": [1, np.nan, np.nan, np.nan] # 75% null, should stay if threshold is 20%
    })
    
    state = {"raw_data": df}
    result = data_cleaner(state)
    cleaned = result["cleaned_data"]
    
    print("--- Original ---")
    print(df)
    print("\n--- Cleaned ---")
    print(cleaned)
    print("\nDtypes:\n", cleaned.dtypes)
    
    # Assertions
    assert "all_null" not in cleaned.columns, "Wholly null columns should be dropped"
    assert not cleaned.isnull().values.any(), "Cleaned dataset should have zero nulls"
    assert pd.api.types.is_datetime64_any_dtype(cleaned["dates"]), "Dates should be converted"

if __name__ == "__main__":
    test_cleaner()
