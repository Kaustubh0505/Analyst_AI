from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.click import router as click_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 👇 include routes
app.include_router(click_router)

@app.get("/")
def home():
    return {"message": "Backend working 🚀"}

