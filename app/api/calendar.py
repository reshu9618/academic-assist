from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.db.models import CalendarEvent

router = APIRouter()

# Pydantic models
class CalendarEventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: str
    external_id: Optional[str] = None

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventResponse(CalendarEventBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class CalendarSyncRequest(BaseModel):
    calendar_type: str  # "google" or "outlook"
    auth_code: Optional[str] = None
    refresh_token: Optional[str] = None

@router.post("/sync_calendar/", status_code=status.HTTP_200_OK)
def sync_calendar(request: CalendarSyncRequest, db: Session = Depends(get_db), user_id: int = 1):
    """
    Sync events from external calendar (Google Calendar or Outlook)
    """
    # In a real app, this would use OAuth to connect to the calendar API
    # For now, we'll return a mock response
    
    # Mock successful sync
    return {
        "status": "success",
        "message": f"Successfully synced {request.calendar_type} calendar",
        "events_synced": 15
    }

@router.get("/calendar_events/", response_model=List[CalendarEventResponse])
def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Get user's calendar events within a date range"""
    query = db.query(CalendarEvent).filter(CalendarEvent.user_id == user_id)
    
    if start_date:
        query = query.filter(CalendarEvent.start_time >= start_date)
    if end_date:
        query = query.filter(CalendarEvent.end_time <= end_date)
    
    events = query.all()
    return events

@router.post("/calendar_events/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
def create_calendar_event(event: CalendarEventCreate, db: Session = Depends(get_db), user_id: int = 1):
    """Create a new calendar event"""
    db_event = CalendarEvent(
        user_id=user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        location=event.location,
        event_type=event.event_type,
        external_id=event.external_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event