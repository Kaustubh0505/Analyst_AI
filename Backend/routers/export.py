import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from routers.upload import _sessions

router = APIRouter(prefix="/export", tags=["export"])


@router.get("")
async def export_csv(session_id: str = "default"):
    """
    Download the current dataset as a CSV file.
    Returns manipulated_data if transformations have been applied,
    otherwise returns cleaned_data.
    """
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=400, detail="No data found for this session.")

    df = session.get("manipulated_data")
    if df is None:
        df = session.get("cleaned_data")

    # If no cleaned/manipulated data, perform a quick clean on-the-fly
    if df is None and "raw_data" in session:
        from agents.data_cleaner import data_cleaner
        cleaning_result = data_cleaner(session)
        df = cleaning_result.get("cleaned_data")

    if df is None:
        raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=exported_data.csv"},
    )
