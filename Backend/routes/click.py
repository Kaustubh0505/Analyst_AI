from fastapi import APIRouter, UploadFile, File, Form
import pandas as pd
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0.5
)

@router.post("/click")
async def handle_click(
    query: str = Form(...),
    file: UploadFile = File(None)
):
    csv_summary = ""

    if file:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))

        csv_summary = f"""
        Columns: {list(df.columns)}
        Shape: {df.shape}
        Head:
        {df.head().to_string()}
        """

    final_prompt = f"""
    User Query:
    {query}

    CSV Data:
    {csv_summary}
    """

    response = llm.invoke(final_prompt)

    return {
        "response": response.content
    }
