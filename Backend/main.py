from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.upload import router as upload_router
from routers.analyze import router as analyze_router
from routers.query import router as query_router
from routers.report import router as report_router
from routers.export import router as export_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(upload_router)
app.include_router(analyze_router)
app.include_router(query_router)
app.include_router(report_router)
app.include_router(export_router)

@app.get("/")
def home():
    return {"message": "Backend working 🚀"}