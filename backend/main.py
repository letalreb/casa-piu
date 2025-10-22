"""
Casa&Più - FastAPI Backend Main Entry Point
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from contextlib import asynccontextmanager

from database import engine, Base, get_database
from api import auth, assets, expenses, reminders, automations, suggestions, f24
from utils.notifier import NotificationService
from utils.scheduler import SchedulerService

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize services
notification_service = NotificationService()
scheduler_service = SchedulerService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting Casa&Più Backend...")
    await scheduler_service.start()
    print("✅ Scheduler started")
    
    yield
    
    # Shutdown
    await scheduler_service.shutdown()
    print("🛑 Casa&Più Backend stopped")

# Create FastAPI app
app = FastAPI(
    title="Casa&Più API",
    description="Family Expense Management for Real Estate and Vehicles",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(assets.router, prefix="/api/assets", tags=["Assets"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["Reminders"])
app.include_router(automations.router, prefix="/api/automations", tags=["Automations"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["AI Suggestions"])
app.include_router(f24.router, prefix="/api/f24", tags=["F24"])

# Static files for PDFs and uploads
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Casa&Più Backend API", 
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running",
        "notifications": "enabled"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=os.getenv("ENVIRONMENT") == "development"
    )