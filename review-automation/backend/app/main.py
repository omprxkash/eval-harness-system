from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import reviews, analytics
from app.database import engine, Base
import app.models  # noqa: F401 — ensures models are registered before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Review Automation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reviews.router)
app.include_router(analytics.router)


@app.on_event("startup")
async def on_startup():
    pass


@app.get("/health")
def health():
    return {"status": "ok"}
