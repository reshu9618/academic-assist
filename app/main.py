from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.api import courses, calendar, schedule, history
from app.db.database import engine, Base
from dotenv import load_dotenv
import uvicorn
import os

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EduFlow API",
    description="Academic Planning AI Assistant API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(courses.router, prefix="/api", tags=["courses"])
app.include_router(calendar.router, prefix="/api", tags=["calendar"])
app.include_router(schedule.router, prefix="/api", tags=["schedule"])
app.include_router(history.router, prefix="/api", tags=["history"])

@app.get("/")
async def root():
    return {"message": "Welcome to EduFlow API - Your Academic Planning Assistant"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)