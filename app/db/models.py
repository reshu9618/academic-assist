from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    courses = relationship("Course", back_populates="user")
    tasks = relationship("Task", back_populates="user")
    schedules = relationship("Schedule", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    code = Column(String)
    instructor = Column(String)
    credit_hours = Column(Float)
    difficulty_rating = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    schedule_info = Column(JSON)  # Days, times, location
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="courses")
    tasks = relationship("Task", back_populates="course")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime)
    priority = Column(Integer)  # 1-5 scale
    estimated_hours = Column(Float)
    completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    task_type = Column(String)  # assignment, exam, reading, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    course = relationship("Course", back_populates="tasks")
    study_blocks = relationship("StudyBlock", back_populates="task")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, index=True)
    schedule_data = Column(JSON)  # Full day schedule
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="schedules")
    study_blocks = relationship("StudyBlock", back_populates="schedule")

class StudyBlock(Base):
    __tablename__ = "study_blocks"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    completed = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    schedule = relationship("Schedule", back_populates="study_blocks")
    task = relationship("Task", back_populates="study_blocks")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    study_preferences = Column(JSON)  # Preferred study times, break intervals
    productivity_data = Column(JSON, nullable=True)  # Historical productivity data
    calendar_sync = Column(Boolean, default=False)
    notification_settings = Column(JSON)  # Notification preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String, nullable=True)
    event_type = Column(String)  # class, personal, etc.
    external_id = Column(String, nullable=True)  # ID from external calendar
    created_at = Column(DateTime, default=datetime.utcnow)

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    insight_type = Column(String)  # productivity, time_management, etc.
    content = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)