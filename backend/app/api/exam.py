import uuid
import random
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, desc

from app.database import get_session
from app.models import Exercise, Attempt, AttemptAnswer
from app.engine import grade_answer
from app.api.practice import BOOK_LABELS

router = APIRouter(prefix="/api/exam", tags=["exam"])

class StartExamRequest(BaseModel):
    book: Optional[str] = "all"
    student_name: Optional[str] = "Anonymous"
    student_device_id: Optional[str] = "local"

class SubmittedAnswer(BaseModel):
    exercise_id: int
    user_answer: str

class SubmitExamRequest(BaseModel):
    exam_id: str
    student_name: str
    student_device_id: str
    book_filter: Optional[str] = "all"
    time_taken_seconds: int = 0
    answers: List[SubmittedAnswer]

@router.post("/start")
def start_exam(
    req: StartExamRequest,
    session: Session = Depends(get_session)
):
    """Draws 6 random exercises for a Cambridge B2 First Part 4 mock simulation."""
    query = select(Exercise)
    if req.book and req.book != "all":
        query = query.where(Exercise.book == req.book)
    
    exercises = session.exec(query).all()
    if len(exercises) < 6:
        # Fallback to all if selected book has fewer than 6
        exercises = session.exec(select(Exercise)).all()
        if len(exercises) < 6:
            raise HTTPException(status_code=400, detail="Not enough exercises in database.")

    selected = random.sample(exercises, 6)
    exam_id = str(uuid.uuid4())

    return {
        "exam_id": exam_id,
        "total_questions": 6,
        "max_score": 12,
        "time_limit_seconds": 600,  # 10 minutes
        "book_filter": req.book or "all",
        "book_label": BOOK_LABELS.get(req.book, req.book) if req.book and req.book != "all" else "All sources",
        "exercises": [
            {
                "id": ex.id,
                "book": ex.book,
                "book_label": BOOK_LABELS.get(ex.book, ex.book),
                "page_identifier": ex.page_identifier,
                "sentence_given": ex.sentence_given,
                "keyword": ex.keyword,
                "incomplete_phrase": ex.incomplete_phrase,
            }
            for ex in selected
        ]
    }

@router.post("/submit")
def submit_exam(
    req: SubmitExamRequest,
    session: Session = Depends(get_session)
):
    """Grades all 6 questions and records the attempt."""
    if not req.answers:
        raise HTTPException(status_code=400, detail="No answers provided.")

    total_score = 0
    results_detail = []

    for ans in req.answers:
        ex = session.get(Exercise, ans.exercise_id)
        if not ex:
            continue

        eval_res = grade_answer(
            user_ans=ans.user_answer,
            correct_ans=ex.correct_answer,
            keyword=ex.keyword,
            acceptable_answers=ex.acceptable_answers
        )

        total_score += eval_res["score"]

        results_detail.append({
            "exercise_id": ex.id,
            "sentence_given": ex.sentence_given,
            "keyword": ex.keyword,
            "incomplete_phrase": ex.incomplete_phrase,
            "user_answer": ans.user_answer,
            "correct_answer": ex.correct_answer,
            "acceptable_answers": ex.acceptable_answers,
            "explanation": ex.explanation,
            "score_awarded": eval_res["score"],
            "max_score": 2,
            "is_exact": eval_res["is_exact"],
            "feedback": eval_res["feedback"]
        })

    # Save to database
    attempt = Attempt(
        id=req.exam_id,
        student_name=req.student_name,
        student_device_id=req.student_device_id,
        mode="exam",
        book_filter=req.book_filter or "all",
        total_score=total_score,
        max_score=12,
        time_taken_seconds=req.time_taken_seconds,
        submitted_at=datetime.utcnow()
    )
    session.add(attempt)

    for r in results_detail:
        aa = AttemptAnswer(
            attempt_id=req.exam_id,
            exercise_id=r["exercise_id"],
            sentence_given=r["sentence_given"],
            keyword=r["keyword"],
            incomplete_phrase=r["incomplete_phrase"],
            correct_answer=r["correct_answer"],
            user_submitted=r["user_answer"],
            score_awarded=r["score_awarded"],
            is_exact=r["is_exact"]
        )
        session.add(aa)

    session.commit()

    percentage = round((total_score / 12) * 100, 1)
    passed = total_score >= 8  # Cambridge 60%+ pass threshold

    return {
        "exam_id": req.exam_id,
        "book_filter": req.book_filter or "all",
        "book_label": BOOK_LABELS.get(req.book_filter, req.book_filter) if req.book_filter and req.book_filter != "all" else "All sources",
        "total_score": total_score,
        "max_score": 12,
        "percentage": percentage,
        "passed": passed,
        "time_taken_seconds": req.time_taken_seconds,
        "results": results_detail
    }

@router.get("/history")
def get_student_history(
    student_device_id: str = Query(..., description="Student browser device UUID"),
    session: Session = Depends(get_session)
):
    """Returns past attempts for this student."""
    attempts = session.exec(
        select(Attempt)
        .where(Attempt.student_device_id == student_device_id)
        .order_by(desc(Attempt.submitted_at))
        .limit(20)
    ).all()

    return [
        {
            "id": att.id,
            "student_name": att.student_name,
            "mode": att.mode,
            "book_filter": att.book_filter,
            "book_label": BOOK_LABELS.get(att.book_filter, att.book_filter) if att.book_filter and att.book_filter != "all" else "All sources",
            "total_score": att.total_score,
            "max_score": att.max_score,
            "percentage": round((att.total_score / att.max_score) * 100, 1) if att.max_score else 0,
            "time_taken_seconds": att.time_taken_seconds,
            "submitted_at": att.submitted_at.isoformat()
        }
        for att in attempts
    ]
