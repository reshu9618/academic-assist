from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.db.models import Course, User

router = APIRouter()

# Pydantic models for request/response
class CourseBase(BaseModel):
    name: str
    code: str
    instructor: Optional[str] = None
    credit_hours: float
    difficulty_rating: Optional[int] = None
    start_date: datetime
    end_date: datetime
    schedule_info: dict

class CourseCreate(CourseBase):
    pass

class CourseResponse(CourseBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/courses/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db), user_id: int = 1):
    # In a real app, user_id would come from auth token
    db_course = Course(
        user_id=user_id,
        name=course.name,
        code=course.code,
        instructor=course.instructor,
        credit_hours=course.credit_hours,
        difficulty_rating=course.difficulty_rating,
        start_date=course.start_date,
        end_date=course.end_date,
        schedule_info=course.schedule_info
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

@router.get("/courses/", response_model=List[CourseResponse])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user_id: int = 1):
    # In a real app, user_id would come from auth token
    courses = db.query(Course).filter(Course.user_id == user_id).offset(skip).limit(limit).all()
    return courses

@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db), user_id: int = 1):
    # In a real app, user_id would come from auth token
    course = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db), user_id: int = 1):
    # In a real app, user_id would come from auth token
    db_course = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Update course attributes
    for key, value in course.dict().items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db), user_id: int = 1):
    # In a real app, user_id would come from auth token
    db_course = db.query(Course).filter(Course.id == course_id, Course.user_id == user_id).first()
    if db_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    
    db.delete(db_course)
    db.commit()
    return None

@router.post("/analyze_courses/", status_code=status.HTTP_200_OK)
def analyze_courses(db: Session = Depends(get_db), user_id: int = 1):
    """
    Analyze courses for workload, difficulty, and scheduling insights.
    This endpoint triggers the LangGraph agent to analyze course data.
    """
    # In a real app, user_id would come from auth token
    courses = db.query(Course).filter(Course.user_id == user_id).all()
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")
    
    # Here we would call the LangGraph agent to analyze courses
    # For now, we'll return a mock response
    return {
        "analysis": {
            "total_credit_hours": sum(course.credit_hours for course in courses),
            "average_difficulty": sum(course.difficulty_rating or 3 for course in courses) / len(courses),
            "workload_distribution": {
                "monday": 25,
                "tuesday": 15,
                "wednesday": 30,
                "thursday": 15,
                "friday": 15
            },
            "recommendations": [
                "Consider spreading out your workload more evenly throughout the week",
                "Your heaviest course days are Monday and Wednesday"
            ]
        }
    }