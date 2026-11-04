from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_session
from app.models import Exercise, VariantSuggestion

router = APIRouter(prefix="/api/suggestions", tags=["suggestions"])

class CreateSuggestionRequest(BaseModel):
    exercise_id: int
    student_name: Optional[str] = "Anonymous"
    suggested_answer: str

@router.post("")
def submit_suggestion(
    req: CreateSuggestionRequest,
    session: Session = Depends(get_session)
):
    """Students submit an alternative answer they believe should be accepted."""
    ans = req.suggested_answer.strip()
    if not ans:
        raise HTTPException(status_code=400, detail="Suggested answer cannot be empty.")

    ex = session.get(Exercise, req.exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    suggestion = VariantSuggestion(
        exercise_id=req.exercise_id,
        student_name=req.student_name or "Anonymous",
        suggested_answer=ans,
        status="pending",
        created_at=datetime.utcnow()
    )
    session.add(suggestion)
    session.commit()
    session.refresh(suggestion)

    return {
        "success": True,
        "message": "Suggestion submitted! The teacher/admin will review it.",
        "suggestion_id": suggestion.id
    }
