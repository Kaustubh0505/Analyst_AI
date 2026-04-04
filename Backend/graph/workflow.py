from langgraph.graph import StateGraph, END
from state.analyst_state import AnalystState
from agents.data_cleaner import data_cleaner
from agents.eda_analyzer import eda_analyzer
from agents.insight_generator import insight_generator
from agents.visualization_agent import visualization_agent
from agents.report_generator import report_generator
from agents.qa_agent import qa_agent
from agents.data_manipulator import data_manipulator

def route_query(state: AnalystState) -> str:
    """Conditional router: after qa_agent classifies intent, decide next node."""
    intent = state.get("query_intent", "question")
    if intent == "manipulation":
        return "data_manipulator"
    return END



def build_analysis_graph():
    """Build the full analysis pipeline graph (upload → report)."""
    graph = StateGraph(AnalystState)

    graph.add_node("data_cleaner", data_cleaner)
    graph.add_node("eda_analyzer", eda_analyzer)
    graph.add_node("insight_generator", insight_generator)
    graph.add_node("visualization_agent", visualization_agent)
    graph.add_node("report_generator", report_generator)

    graph.set_entry_point("data_cleaner")
    graph.add_edge("data_cleaner", "eda_analyzer")
    graph.add_edge("eda_analyzer", "insight_generator")
    graph.add_edge("insight_generator", "visualization_agent")
    graph.add_edge("visualization_agent", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()



def build_query_graph():
    """Build the query pipeline graph (user_query → answer or manipulation)."""
    graph = StateGraph(AnalystState)

    graph.add_node("qa_agent",qa_agent)
    graph.add_node("data_manipulator", data_manipulator)

    graph.set_entry_point("qa_agent")
    graph.add_conditional_edges("qa_agent", route_query)
    graph.add_edge("data_manipulator", END)

    return graph.compile()


analysis_graph = build_analysis_graph()
query_graph = build_query_graph()
