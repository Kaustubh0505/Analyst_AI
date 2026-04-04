from fastapi import APIRouter, HTTPException
from routers.upload import _sessions

router = APIRouter(prefix="/report", tags=["report"])


@router.get("")
async def get_report(session_id: str = "default"):
    """Return the compiled analyst report."""
    session = _sessions.get(session_id)
    if not session or "report" not in session:
        raise HTTPException(status_code=404, detail="Report not yet generated. Run /analyze first.")

    return {"report": session["report"]}
