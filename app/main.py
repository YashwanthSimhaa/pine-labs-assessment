from fastapi import FastAPI
from app.router import router
from app.core.database import engine, Base
from contextlib import asynccontextmanager

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield

app = FastAPI(
    title="PineLabs Assessment APIs", 
    description="Backend service for payment event ingestion and reconciliation",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Service is running"}

app.include_router(router)
