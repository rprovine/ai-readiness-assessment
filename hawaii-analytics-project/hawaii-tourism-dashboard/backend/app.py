from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from routes import dashboard, analytics, leads
from services.data_collector import DataCollector
from config.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Hawaii Tourism Analytics Dashboard...")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Hawaii Tourism Analytics API",
    description="Real-time tourism data and predictive analytics for Hawaii businesses",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])

@app.get("/")
async def root():
    return {
        "message": "Hawaii Tourism Analytics Dashboard API",
        "endpoints": {
            "dashboard": "/api/dashboard",
            "analytics": "/api/analytics",
            "leads": "/api/leads",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "hawaii-tourism-analytics"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)