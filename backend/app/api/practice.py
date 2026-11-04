import random
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, func

from app.database import get_session
from app.models import Exercise
from app.engine import grade_answer

router = APIRouter(prefix="/api/practice", tags=["practice"])

BOOK_LABELS = {
    "libro_clase": "Libro que usamos en clase",
    "book0": "Libro que usamos en clase",
    "book1": "Libro que usamos en clase",
    "book2": "Book 2 — ENG Exam Tests",
    "ENG Exam": "Book 2 — ENG Exam Tests",
    "book3": "Book 3 — Flo-Joe Collection",
    "Flo-Joe": "Book 3 — Flo-Joe Collection",
    "book4": "Book 4 — ESL Lounge Worksheets",
    "ESL Lounge": "Book 4 — ESL Lounge Worksheets",
    "handbook": "Cambridge Official Handbook",
    "ENG XAM": "Cambridge Official Handbook",
}

class CheckAnswerRequest(BaseModel):
    exercise_id: int
    user_answer: str
    student_name: Optional[str] = "Anonymous"
    student_device_id: Optional[str] = "local"

@router.get("/books")
def list_books(session: Session = Depends(get_session)):
    """Returns available books and exercise count for each."""
    counts = session.exec(
        select(Exercise.book, func.count(Exercise.id)).group_by(Exercise.book)
    ).all()
    
    books_data = []
    total = 0
    for book_key, count in counts:
        total += count
        books_data.append({
            "key": book_key,
            "title": BOOK_LABELS.get(book_key, book_key.capitalize()),
            "count": count
        })
    
    # Sort with book0, book1, book2, book3, book4, handbook
    def sort_key(b):
        k = b["key"]
        return ("0" if k in ("libro_clase", "book0") else
                "1" if k == "book1" else
                "2" if k == "book2" else
                "3" if k == "book3" else
                "4" if k == "book4" else
                "5" if k == "handbook" else "9")

    books_data.sort(key=sort_key)
    
    return {
        "total_exercises": total,
        "books": books_data
    }

@router.get("/random")
def get_random_exercise(
    book: str = Query("all", description="book filter or 'all'"),
    exclude_ids: str = Query("", description="comma-separated IDs to avoid duplicates"),
    session: Session = Depends(get_session)
):
    """Fetches a random exercise without leaking the answer."""
    query = select(Exercise)
    if book and book != "all":
        query = query.where(Exercise.book == book)
    
    if exclude_ids:
        try:
            ids = [int(i.strip()) for i in exclude_ids.split(",") if i.strip()]
            if ids:
                query = query.where(Exercise.id.not_in(ids))
        except ValueError:
            pass

    exercises = session.exec(query).all()
    if not exercises:
        # Fallback to any if all excluded
        query_fallback = select(Exercise)
        if book and book != "all":
            query_fallback = query_fallback.where(Exercise.book == book)
        exercises = session.exec(query_fallback).all()
        if not exercises:
            raise HTTPException(status_code=404, detail="No exercises found for this filter.")

    ex = random.choice(exercises)
    return {
        "id": ex.id,
        "book": ex.book,
        "book_label": BOOK_LABELS.get(ex.book, ex.book),
        "page_identifier": ex.page_identifier,
        "page": ex.page,
        "exercise_number": ex.exercise_number,
        "sentence_given": ex.sentence_given,
        "keyword": ex.keyword,
        "incomplete_phrase": ex.incomplete_phrase,
        "verified": ex.verified,
        "is_locked": ex.is_locked
    }

@router.post("/check")
def check_practice_answer(
    req: CheckAnswerRequest,
    session: Session = Depends(get_session)
):
    """Evaluates an answer with full explanation and official key."""
    ex = session.get(Exercise, req.exercise_id)
    if not ex:
        raise HTTPException(status_code=404, detail="Exercise not found")

    result = grade_answer(
        user_ans=req.user_answer,
        correct_ans=ex.correct_answer,
        keyword=ex.keyword,
        acceptable_answers=ex.acceptable_answers
    )

    return {
        "exercise_id": ex.id,
        "is_exact": result["is_exact"],
        "score": result["score"],
        "max_score": result["max"],
        "feedback": result["feedback"],
        "correct_answer": ex.correct_answer,
        "acceptable_answers": ex.acceptable_answers,
        "explanation": ex.explanation
    }
