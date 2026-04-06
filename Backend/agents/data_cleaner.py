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
You are an expert AI Data Scientist specializing in Data Cleaning. 
Your task is to analyze the provided dataset profile and generate Python (pandas) code to clean it thoroughly.

### Dataset Profile:
{data_profile}

### Cleaning Goals:
1. Standardize column names (snake_case, no spaces).
2. Handle missing values intelligently (impute numerically with median/mode, or drop if >80% null).
3. Fix data types: Ensure dates are datetime objects, numbers are numeric, and categorical strings are clean.
4. Remove outlier noise: Identify columns that are likely ID-only or have zero variance and drop them.
5. Standardize text: Trim spaces, fix casing where obvious.

### Output Format:
Your response must contain:
1. **Analysis**: A brief summary of the issues found.
2. **Cleaning Code**: A Python code block using `df` as the variable name for the dataframe. 
   - DO NOT import pandas (it's already imported as `pd`).
   - DO NOT include `df = pd.read_csv(...)`.
   - The code should modify `df` or return it.

Example:
```python
# Analysis: Found mixed casing in 'City' and 50% nulls in 'Salary'
df.columns = [c.lower().replace(' ', '_') for c in df.columns]
df['city'] = df['city'].str.title()
df['salary'] = df['salary'].fillna(df['salary'].median())
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