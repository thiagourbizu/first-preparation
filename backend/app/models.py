import json
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field

class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book: str = Field(index=True)
    page_identifier: str = Field(default="Page 1")
    page: int = Field(default=1)
    exercise_number: int = Field(default=1)
    sentence_given: str
    keyword: str
    incomplete_phrase: str
    correct_answer: str
    acceptable_answers_json: str = Field(default="[]")
    explanation: Optional[str] = None
    is_locked: bool = Field(default=False)
    verified: bool = Field(default=False)

    @property
    def acceptable_answers(self) -> List[str]:
        try:
            return json.loads(self.acceptable_answers_json)
        except Exception:
            return []

    def set_acceptable_answers(self, variants: List[str]):
        clean = list({v.strip() for v in variants if v and v.strip()})
        self.acceptable_answers_json = json.dumps(clean, ensure_ascii=False)

class VariantSuggestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    exercise_id: int = Field(index=True)
    student_name: str = Field(default="Anonymous")
    suggested_answer: str
    status: str = Field(default="pending", index=True)  # pending | approved | rejected
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Attempt(SQLModel, table=True):
    id: str = Field(primary_key=True)  # UUID
    student_name: str = Field(index=True)
    student_device_id: str = Field(index=True)
    mode: str = Field(default="exam")  # exam | practice
    book_filter: str = Field(default="all")
    total_score: int = Field(default=0)
    max_score: int = Field(default=12)
    time_taken_seconds: int = Field(default=0)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class AttemptAnswer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: str = Field(index=True)
    exercise_id: int = Field(index=True)
    sentence_given: str
    keyword: str
    incomplete_phrase: str
    correct_answer: str
    user_submitted: str
    score_awarded: int
    is_exact: bool
    matched_variant: Optional[str] = None
