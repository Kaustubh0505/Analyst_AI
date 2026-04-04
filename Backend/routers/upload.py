from fastapi import APIRouter, UploadFile, File, HTTPException
from utils.file_handler import save_upload, load_csv

router = APIRouter(prefix="/upload", tags=["upload"])

# Module-level session store (session_id -> DataFrame)
# Shared across routers via import
_sessions: dict = {}


@router.post("")
async def upload_csv(file: UploadFile = File(...)):
    """Accept a CSV file, save it, and load it into session state."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    content = await file.read()
    file_path = save_upload(content, file.filename)
    df = load_csv(file_path)

    # Use a fixed session_id for now (extend to cookies/tokens for multi-user)
    session_id = "default"
    _sessions[session_id] = {"raw_data": df}

    return {
        "message": "File uploaded successfully.",
        "session_id": session_id,
        "rows": df.shape[0],
        "columns": list(df.columns),
    }
