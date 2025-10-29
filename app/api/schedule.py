from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, date
from app.db.database import get_db
from app.db.models import Schedule, Task, Course, StudyBlock
from app.agent.agent_graph import run_eduflow_agent

router = APIRouter()

# Pydantic models
class ScheduleRequest(BaseModel):
    start_date: date
    end_date: date
    preferences: Optional[Dict[str, Any]] = None

class ScheduleResponse(BaseModel):
    date: date
    schedule_data: Dict[str, Any]
    
    class Config:
        orm_mode = True

@router.post("/generate_schedule/", response_model=Dict[str, Any])
def generate_schedule(request: ScheduleRequest, db: Session = Depends(get_db), user_id: int = 1):
    """
    Generate an optimized schedule based on courses, tasks, and calendar events.
    This endpoint uses the LangGraph agent to create an intelligent schedule.
    """
    # Get user's courses
    courses = db.query(Course).filter(Course.user_id == user_id).all()
    courses_data = [
        {
            "id": course.id,
            "name": course.name,
            "code": course.code,
            "credit_hours": course.credit_hours,
            "difficulty_rating": course.difficulty_rating,
            "schedule_info": course.schedule_info
        }
        for course in courses
    ]
    
    # Get user's tasks
    tasks = db.query(Task).filter(
        Task.user_id == user_id,
        Task.due_date >= request.start_date,
        Task.completed == False
    ).all()
    tasks_data = [
        {
            "id": task.id,
            "title": task.title,
            "course_id": task.course_id,
            "due_date": task.due_date.isoformat(),
            "priority": task.priority,
            "estimated_hours": task.estimated_hours,
            "task_type": task.task_type
        }
        for task in tasks
    ]
    
    # Get calendar events
    # In a real app, we would also fetch from external calendars
    calendar_events = []
    
    # Mock student data (in a real app, this would come from the user's profile)
    student_data = {
        "id": user_id,
        "preferences": request.preferences or {
            "preferred_study_times": ["morning", "evening"],
            "break_frequency": 50,  # minutes
            "break_duration": 10,  # minutes
            "max_daily_study_hours": 6
        }
    }
    
    # Run the EduFlow agent to generate schedule
    result = run_eduflow_agent(
        student_data=student_data,
        courses=courses_data,
        tasks=tasks_data,
        calendar_events=calendar_events
    )
    
    # Save the generated schedule to the database
    for day, blocks in result["schedule"]["weekly_plan"].items():
        day_date = datetime.fromisoformat(day)
        
        # Check if a schedule already exists for this date
        existing_schedule = db.query(Schedule).filter(
            Schedule.user_id == user_id,
            Schedule.date == day_date
        ).first()
        
        if existing_schedule:
            # Update existing schedule
            existing_schedule.schedule_data = {"blocks": blocks}
            db.commit()
        else:
            # Create new schedule
            new_schedule = Schedule(
                user_id=user_id,
                date=day_date,
                schedule_data={"blocks": blocks}
            )
            db.add(new_schedule)
            db.commit()
            db.refresh(new_schedule)
    
    return result

@router.get("/schedules/", response_model=List[ScheduleResponse])
def get_schedules(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Get user's schedules within a date range"""
    query = db.query(Schedule).filter(Schedule.user_id == user_id)
    
    if start_date:
        query = query.filter(Schedule.date >= start_date)
    if end_date:
        query = query.filter(Schedule.date <= end_date)
    
    schedules = query.all()
    return schedules

@router.get("/schedules/{date}", response_model=ScheduleResponse)
def get_schedule_by_date(date: date, db: Session = Depends(get_db), user_id: int = 1):
    """Get user's schedule for a specific date"""
    schedule = db.query(Schedule).filter(
        Schedule.user_id == user_id,
        Schedule.date == date
    ).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found for this date")
    
    return schedule