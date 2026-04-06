from typing import TypedDict,List,Any


class AnalystState(TypedDict):
    raw_data:Any
    cleaned_data:Any
    manipulated_data:Any
    eda_results:dict
    insights:List[str]
    charts:List[dict]
    report:str
    memory:List[dict]
    user_query:str
    query_intent:str
    cleaning_report:str
    answer:str