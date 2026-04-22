from typing import TypedDict, List, Any


class AnalystState(TypedDict):
    raw_data: Any
    cleaned_data: Any
    manipulated_data: Any
    eda_results: dict
    insights: List[str]
    charts: List[dict]
    aggregated_charts: List[dict]  # New: Aggregated data for each chart
    grouped_insights: List[str]    # New: Insights discovered through grouping
    report: str
    memory: List[dict]
    user_query: str
    query_intent: str
    cleaning_report: str
    answer: str