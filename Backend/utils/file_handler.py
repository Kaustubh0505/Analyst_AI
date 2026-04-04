import os
import uuid
import pandas as pd

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(file_bytes: bytes, filename: str) -> str:
    """Save uploaded file bytes and return the saved file path."""
    file_id = uuid.uuid4().hex
    ext = os.path.splitext(filename)[1]
    save_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    return save_path


def load_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame."""
    return pd.read_csv(file_path)
