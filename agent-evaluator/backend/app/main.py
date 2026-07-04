from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import runs, evals, metrics
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agent Evaluator API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(evals.router)
app.include_router(metrics.router)


@app.get("/health")
def health():
    return {"status": "ok"}
