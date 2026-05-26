from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.db.models import ChatHistory, User

router = APIRouter()

# Pydantic models
class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class UserGamificationUpdate(BaseModel):
    points: int
    badges: List[str]

class UserGamificationResponse(BaseModel):
    points: int
    badges: List[str]

    class Config:
        from_attributes = True

@router.get("/chat_history/", response_model=List[ChatMessageResponse])
def get_chat_history(db: Session = Depends(get_db), user_id: int = 1):
    messages = db.query(ChatHistory).filter(ChatHistory.user_id == user_id).order_by(ChatHistory.timestamp.asc()).all()
    return messages

@router.post("/chat_history/", response_model=ChatMessageResponse)
def save_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db), user_id: int = 1):
    db_message = ChatHistory(
        user_id=user_id,
        role=message.role,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.delete("/chat_history/", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(db: Session = Depends(get_db), user_id: int = 1):
    db.query(ChatHistory).filter(ChatHistory.user_id == user_id).delete()
    db.commit()
    return None

@router.get("/gamification/", response_model=UserGamificationResponse)
def get_gamification_data(db: Session = Depends(get_db), user_id: int = 1):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/gamification/", response_model=UserGamificationResponse)
def update_gamification_data(data: UserGamificationUpdate, db: Session = Depends(get_db), user_id: int = 1):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.points = data.points
    user.badges = data.badges
    db.commit()
    db.refresh(user)
    return user
