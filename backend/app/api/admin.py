import json
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Header, Query
from pydantic import BaseModel
from sqlmodel import Session, select, func, desc

from app.config import settings
from app.database import get_session
from app.models import Exercise, VariantSuggestion, Attempt, AttemptAnswer

router = APIRouter(prefix="/api/admin", tags=["admin"])

def verify_admin(x_admin_password: Optional[str] = Header(None, alias="X-Admin-Password")):
    if not x_admin_password or x_admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Incorrect admin credentials."
        )
    return True

class AdminLoginRequest(BaseModel):
    password: str

class ExerciseUpdateRequest(BaseModel):
    sentence_given: str
    keyword: str
    incomplete_phrase: str
    correct_answer: str
    acceptable_answers: List[str]
    explanation: Optional[str] = None
    is_locked: bool = False
    verified: bool = False

class ExerciseCreateRequest(BaseModel):
    book: str = "book0"
    page_identifier: str = "Custom Class Exercise"
    exercise_number: int = 1
    sentence_given: str
    keyword: str
    incomplete_phrase: str
    correct_answer: str
    acceptable_answers: Optional[List[str]] = []
    explanation: Optional[str] = None

@router.post("/login")
def admin_login(req: AdminLoginRequest):
    if req.password == settings.ADMIN_PASSWORD:
        return {"authenticated": True, "message": "Admin authenticated successfully"}
    raise HTTPException(status_code=401, detail="Invalid admin password")

@router.get("/suggestions")
def get_suggestions(
    status: str = Query("pending", description="pending | approved | rejected | all"),
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    """Lists community suggestions with associated exercise details."""
    query = select(VariantSuggestion)
    if status != "all":
        query = query.where(VariantSuggestion.status == status)
    query = query.order_by(desc(VariantSuggestion.created_at))

    suggestions = session.exec(query).all()
    results = []
    for s in suggestions:
        ex = session.get(Exercise, s.exercise_id)
        results.append({
            "id": s.id,
            "exercise_id": s.exercise_id,
            "student_name": s.student_name,
            "suggested_answer": s.suggested_answer,
            "status": s.status,
            "created_at": s.created_at.isoformat(),
            "exercise": {
                "sentence_given": ex.sentence_given if ex else "Unknown",
                "keyword": ex.keyword if ex else "Unknown",
                "incomplete_phrase": ex.incomplete_phrase if ex else "Unknown",
                "correct_answer": ex.correct_answer if ex else "Unknown",
                "acceptable_answers": ex.acceptable_answers if ex else []
            } if ex else None
        })
    return results

@router.post("/suggestions/{suggestion_id}/approve")
def approve_suggestion(
    suggestion_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    """Approves suggestion and automatically adds the variant to acceptable_answers."""
    s = session.get(VariantSuggestion, suggestion_id)
    if not s:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    ex = session.get(Exercise, s.exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Associated exercise not found")

    variants = ex.acceptable_answers
    ans = s.suggested_answer.strip()
    if ans not in variants:
        variants.append(ans)
        ex.set_acceptable_answers(variants)
        session.add(ex)

    s.status = "approved"
    session.add(s)
    session.commit()

    return {
        "success": True,
        "message": f"Approved and added '{ans}' to acceptable variants for Exercise #{ex.id}"
    }

@router.post("/suggestions/{suggestion_id}/reject")
def reject_suggestion(
    suggestion_id: int,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    s = session.get(VariantSuggestion, suggestion_id)
    if not s:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    s.status = "rejected"
    session.add(s)
    session.commit()
    return {"success": True, "message": "Suggestion rejected."}

@router.get("/exercises")
def list_exercises(
    search: Optional[str] = Query(None, description="Search keyword, sentence, or id"),
    book: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    query = select(Exercise)
    if book and book != "all":
        query = query.where(Exercise.book == book)
    
    if search:
        search_term = f"%{search.strip().lower()}%"
        try:
            ex_id = int(search.strip())
            query = query.where((Exercise.id == ex_id) | (func.lower(Exercise.keyword).like(search_term)) | (func.lower(Exercise.sentence_given).like(search_term)))
        except ValueError:
            query = query.where((func.lower(Exercise.keyword).like(search_term)) | (func.lower(Exercise.sentence_given).like(search_term)))

    total = session.exec(select(func.count(Exercise.id))).one()
    exercises = session.exec(query.offset(offset).limit(limit)).all()

    return {
        "total": total,
        "items": [
            {
                "id": ex.id,
                "book": ex.book,
                "page_identifier": ex.page_identifier,
                "exercise_number": ex.exercise_number,
                "sentence_given": ex.sentence_given,
                "keyword": ex.keyword,
                "incomplete_phrase": ex.incomplete_phrase,
                "correct_answer": ex.correct_answer,
                "acceptable_answers": ex.acceptable_answers,
                "explanation": ex.explanation,
                "is_locked": ex.is_locked,
                "verified": ex.verified
            }
            for ex in exercises
        ]
    }

@router.put("/exercises/{exercise_id}")
def update_exercise(
    exercise_id: int,
    req: ExerciseUpdateRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    ex = session.get(Exercise, exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")

    ex.sentence_given = req.sentence_given.strip()
    ex.keyword = req.keyword.strip().upper()
    ex.incomplete_phrase = req.incomplete_phrase.strip()
    ex.correct_answer = req.correct_answer.strip()
    ex.set_acceptable_answers(req.acceptable_answers)
    ex.explanation = req.explanation
    ex.is_locked = req.is_locked
    ex.verified = req.verified

    session.add(ex)
    session.commit()
    session.refresh(ex)

    return {"success": True, "exercise": ex}

@router.post("/exercises")
def create_exercise(
    req: ExerciseCreateRequest,
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    # Find next ID
    max_id = session.exec(select(func.max(Exercise.id))).one() or 0
    next_id = max_id + 1

    variants = req.acceptable_answers or []
    if req.correct_answer and req.correct_answer not in variants:
        variants.append(req.correct_answer)

    ex = Exercise(
        id=next_id,
        book=req.book,
        page_identifier=req.page_identifier,
        exercise_number=req.exercise_number,
        sentence_given=req.sentence_given.strip(),
        keyword=req.keyword.strip().upper(),
        incomplete_phrase=req.incomplete_phrase.strip(),
        correct_answer=req.correct_answer.strip(),
        explanation=req.explanation,
        verified=True,
        is_locked=False
    )
    ex.set_acceptable_answers(variants)
    session.add(ex)
    session.commit()
    session.refresh(ex)

    return {"success": True, "exercise_id": ex.id}

@router.get("/analytics")
def get_analytics(
    session: Session = Depends(get_session),
    _: bool = Depends(verify_admin)
):
    """Aggregate statistics for class and teacher view."""
    total_attempts = session.exec(select(func.count(Attempt.id))).one()
    avg_score = session.exec(select(func.avg(Attempt.total_score))).one() or 0.0

    # Group by student
    student_stats = session.exec(
        select(
            Attempt.student_name,
            func.count(Attempt.id).label("tests_taken"),
            func.avg(Attempt.total_score).label("avg_score"),
            func.max(Attempt.submitted_at).label("last_active")
        )
        .group_by(Attempt.student_name)
        .order_by(desc("tests_taken"))
    ).all()

    # Pending suggestions count
    pending_suggestions = session.exec(
        select(func.count(VariantSuggestion.id))
        .where(VariantSuggestion.status == "pending")
    ).one()

    return {
        "total_attempts": total_attempts,
        "avg_score_out_of_12": round(avg_score, 1),
        "pending_suggestions_count": pending_suggestions,
        "students": [
            {
                "name": s[0],
                "tests_taken": s[1],
                "avg_score": round(s[2], 1) if s[2] else 0.0,
                "last_active": s[3].isoformat() if s[3] else None
            }
            for s in student_stats
        ]
    }
