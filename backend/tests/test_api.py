import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.main import app
from app.database import engine
from app.models import Exercise
from app.engine import grade_answer

client = TestClient(app)

def test_engine_grading():
    # 1. Exact match
    res = grade_answer(
        user_ans="has difficulty in expressing",
        correct_ans="has difficulty in expressing",
        keyword="DIFFICULTY"
    )
    assert res["is_exact"] is True
    assert res["score"] == 2

    # 2. Contraction normalization (didn't == did not)
    res2 = grade_answer(
        user_ans="didn't let him go",
        correct_ans="did not let him go",
        keyword="LET"
    )
    assert res2["is_exact"] is True
    assert res2["score"] == 2

    # 3. Missing keyword -> 0 marks
    res3 = grade_answer(
        user_ans="did not allow him to leave",
        correct_ans="did not let him go",
        keyword="LET"
    )
    assert res3["is_exact"] is False
    assert res3["score"] == 0

    # 4. Acceptable variant match
    res4 = grade_answer(
        user_ans="has difficulty expressing",
        correct_ans="has difficulty in expressing",
        keyword="DIFFICULTY",
        acceptable_answers=["has difficulty expressing"]
    )
    assert res4["is_exact"] is True
    assert res4["score"] == 2

def test_api_books():
    response = client.get("/api/practice/books")
    assert response.status_code == 200
    data = response.json()
    assert data["total_exercises"] >= 800
    assert len(data["books"]) >= 5

def test_api_random_and_check():
    # Random exercise
    res = client.get("/api/practice/random?book=all")
    assert res.status_code == 200
    ex = res.json()
    assert "id" in ex
    assert "keyword" in ex
    assert "sentence_given" in ex
    assert "correct_answer" not in ex  # Answer must not leak!

    # Check answer
    with Session(engine) as session:
        db_ex = session.get(Exercise, ex["id"])
        correct = db_ex.correct_answer

    check_res = client.post("/api/practice/check", json={
        "exercise_id": ex["id"],
        "user_answer": correct,
        "student_name": "TestStudent",
        "student_device_id": "test_device_123"
    })
    assert check_res.status_code == 200
    check_data = check_res.json()
    assert check_data["score"] == 2
    assert check_data["is_exact"] is True

def test_exam_flow():
    # Start exam
    start_res = client.post("/api/exam/start", json={
        "book": "all",
        "student_name": "Lucas",
        "student_device_id": "lucas_phone_123"
    })
    assert start_res.status_code == 200
    exam_data = start_res.json()
    assert len(exam_data["exercises"]) == 6
    exam_id = exam_data["exam_id"]

    # Submit exam
    answers = []
    for ex in exam_data["exercises"]:
        with Session(engine) as session:
            db_ex = session.get(Exercise, ex["id"])
            answers.append({
                "exercise_id": ex["id"],
                "user_answer": db_ex.correct_answer
            })

    sub_res = client.post("/api/exam/submit", json={
        "exam_id": exam_id,
        "student_name": "Lucas",
        "student_device_id": "lucas_phone_123",
        "time_taken_seconds": 180,
        "answers": answers
    })
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    assert sub_data["total_score"] == 12
    assert sub_data["passed"] is True
    assert len(sub_data["results"]) == 6

def test_admin_flow():
    # Login check
    login_res = client.post("/api/admin/login", json={"password": "admin123"})
    assert login_res.status_code == 200

    # Analytics check
    analytics_res = client.get("/api/admin/analytics", headers={"X-Admin-Password": "admin123"})
    assert analytics_res.status_code == 200
    an_data = analytics_res.json()
    assert an_data["total_attempts"] >= 1

if __name__ == "__main__":
    print("Running tests directly...")
    test_engine_grading()
    print("[PASS] test_engine_grading passed")
    test_api_books()
    print("[PASS] test_api_books passed")
    test_api_random_and_check()
    print("[PASS] test_api_random_and_check passed")
    test_exam_flow()
    print("[PASS] test_exam_flow passed")
    test_admin_flow()
    print("[PASS] test_admin_flow passed")
    print("ALL TESTS PASSED SUCCESSFULLY!")
