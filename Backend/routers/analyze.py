from fastapi import APIRouter, HTTPException
from graph.workflow import analysis_graph
from routers.upload import _sessions

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("")
async def analyze(session_id: str = "default"):
    """Trigger the full LangGraph analysis pipeline and return insights + charts."""
    session = _sessions.get(session_id)
    if not session or "raw_data" not in session:
        raise HTTPException(status_code=400, detail="No data uploaded for this session.")

    state = {"raw_data": session["raw_data"], "session_id": session_id}
    result = analysis_graph.invoke(state)

    # Store results back into the session
    _sessions[session_id].update(result)

    return {
        "insights": result.get("insights", []),
        "charts": result.get("charts", []),
        "eda_summary": {
            "shape": result.get("eda_results", {}).get("shape", {}),
            "columns": result.get("eda_results", {}).get("columns", []),
        },
        "chart_data": result.get("eda_results", {}).get("data_sample", []),
    }
