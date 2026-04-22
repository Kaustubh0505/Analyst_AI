import pandas as pd
import numpy as np
import re
from state.analyst_state import AnalystState
from utils.llm_client import invoke_llm


def generate_data_profile(df: pd.DataFrame) -> str:
    """Generate a detailed profile of the data for the AI to analyze."""
    profile = []
    profile.append(f"### Dataset Summary")
    profile.append(f"- Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    profile.append(f"\n### Column Details")
    
    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isnull().sum()
        pct_null = (nulls / len(df)) * 100
        unique = df[col].nunique()
        sample = df[col].dropna().unique()[:5].tolist()
        
        col_info = (
            f"- **{col}**: type={dtype}, nulls={nulls} ({pct_null:.1f}%), "
            f"unique={unique}, samples={sample}"
        )
        profile.append(col_info)
    
    profile.append(f"\n### Head (First 5 rows)")
    profile.append(df.head().to_string())
    
    return "\n".join(profile)


def basic_cleaning_fallback(df: pd.DataFrame) -> pd.DataFrame:
    """Standard rule-based cleaning as a fallback."""
    df = df.copy()
    
    # 1. Drop columns that are entirely null
    df = df.dropna(axis=1, how="all")
    
    # 2. Drop duplicates
    df = df.drop_duplicates()
    
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(["", "nan", "None", "NULL", "null"], np.nan)
        
        # Date parsing
        if df[col].dtype == "object":
            try:
                # Be more aggressive with date conversion in fallback
                converted = pd.to_datetime(df[col], errors="coerce")
                valid_count = converted.notna().sum()
                if valid_count > 0 and (valid_count / max(1, df[col].notna().sum()) >= 0.3):
                    df[col] = converted
            except:
                pass

    # Imputation
    for col in df.columns:
        if df[col].isnull().any():
            if pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                if not pd.isna(median_val):
                    df[col] = df[col].fillna(median_val)
            else:
                mode = df[col].mode()
                if not mode.empty:
                    df[col] = df[col].fillna(mode[0])
                    
    return df.dropna()


def data_cleaner(state: AnalystState) -> dict:
    """
    Agent 1 — AI Data Cleaner
    - Analyzes data profile using LLM
    - Generates and executes cleaning code
    - Falls back to basic cleaning if AI fails
    """
    df: pd.DataFrame = state["raw_data"].copy()
    data_profile = generate_data_profile(df)

    prompt = f"""
### ROLE
You are an expert Data Scientist and Automation Engineer specializing in Data Cleaning. 
Your task is to analyze the provided dataset profile and generate high-quality Python (pandas) code to clean it.

### DATASET PROFILE
{data_profile}

### CLEANING OBJECTIVES
1.  **Standardize Column Names**: Convert to `snake_case`, remove leading/trailing spaces, and ensure no special characters except underscores.
2.  **Date/Time Conversion**: Convert columns that look like dates to `datetime64[ns]` objects.
3.  **Missing Value Imputation**:
    *   Numerical: Use median or mode based on distribution (prefer median for skewed data).
    *   Categorical: Use mode or a placeholder like 'Unknown'.
    *   Drop columns if >80% of values are missing.
4.  **Data Type Integrity**: Ensure numerical columns are actually numeric (float/int).
5.  **Deduplication**: Remove duplicate rows.
6.  **Text Standardization**: Strip whitespace and fix casing for categorical columns.

### STRICT OUTPUT FORMAT
Your response MUST follow this exact structure:
1. **Analysis**: A concise, 3-sentence summary of the cleaning strategy.
2. **Cleaning Code**: The Python code block.

### GUARDRAILS & RULES
- Use ONLY the provided `df` variable.
- DO NOT import `pandas` or `numpy` (they are pre-imported as `pd` and `np`).
- DO NOT include `df = pd.read_csv(...)` or any data loading.
- Ensure the code is production-ready and error-resistant.
- Return ONLY the analysis and the code block.

Example:
Analysis: I will standardize column names to snake_case and handle missing values in 'price' using the median. Duplicate rows will also be removed.
```python
df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(df['price'].median())
df = df.drop_duplicates()
```
"""


    try:
        response = invoke_llm(prompt, agent_id=1)
        print(f"AI Cleaning Response:\n{response}") # Debug log
        
        # Extract Analysis
        analysis_match = re.search(r"Analysis:(.*?)(?=```python|###)", response, re.S | re.I)
        analysis = analysis_match.group(1).strip() if analysis_match else "AI performed automated cleaning."
        
        # Extract Code
        code_match = re.search(r"```python\n(.*?)```", response, re.S)
        if code_match:
            cleaning_code = code_match.group(1).strip()
            
            # Execute code safely
            # Note: In a production environment, use a restricted sandbox
            namespace = {"pd": pd, "np": np, "df": df}
            exec(cleaning_code, namespace)
            cleaned_df = namespace["df"]
            
            return {
                "cleaned_data": cleaned_df,
                "cleaning_report": f"### AI Cleaning Analysis\n{analysis}"
            }
        else:
            raise ValueError("No cleaning code found in AI response.")

    except Exception as e:
        print(f"AI Cleaning failed: {e}. Falling back to basic cleaning.")
        cleaned_df = basic_cleaning_fallback(df)
        return {
            "cleaned_data": cleaned_df,
            "cleaning_report": f"### AI Cleaning Analysis (Fallback)\nAI failed to generate a plan: {str(e)}. Applied basic cleaning rules."
        }