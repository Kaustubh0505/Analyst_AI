from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from graph.workflow import query_graph
from routers.upload import _sessions

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"


@router.post("")
async def query(request: QueryRequest):
    """
    Unified Q&A + manipulation endpoint.
    Routes to answer or data transformation based on classified intent.
    """
    session = _sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=400, detail="No data uploaded for this session.")

    state = {
        **session,
        "user_query": request.question,
        "session_id": request.session_id,
    }

    result = query_graph.invoke(state)

    # Persist any manipulated data back to session
    if "manipulated_data" in result:
        _sessions[request.session_id]["manipulated_data"] = result["manipulated_data"]

    return {
        "answer": result.get("answer", ""),
        "intent": result.get("query_intent", "question"),
        "manipulation_plan": result.get("manipulation_plan"),
        "download_available": "manipulated_data" in _sessions.get(request.session_id, {}),
    }
