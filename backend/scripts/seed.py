import sys
import json
from pathlib import Path

# Add backend directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from sqlmodel import Session, select
from app.database import engine, init_db
from app.models import Exercise

SEEDS_DIR = BASE_DIR / "data" / "seeds"

SEED_FILES = [
    ("libro_clase", "libro_que_usamos_en_clase.json"),
    ("book2", "book2.json"),
    ("book3", "flojoe.json"),
    ("book4", "esl_lounge.json"),
    ("handbook", "engxam_handbook.json"),
]

def seed_database():
    print("Initializing database tables...")
    init_db()

    total_inserted = 0
    total_updated = 0

    with Session(engine) as session:
        for book_code, filename in SEED_FILES:
            filepath = SEEDS_DIR / filename
            if not filepath.exists():
                print(f"Warning: {filename} not found at {filepath}, skipping.")
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    pages = json.load(f)
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue

            for page in pages:
                p_ident = page.get("page_identifier") or f"Page {page.get('page', 1)}"
                p_num = page.get("page", 1)

                for ex_data in page.get("exercises", []):
                    ex_id = ex_data.get("id")
                    if not ex_id:
                        continue

                    # Check if already exists
                    existing = session.exec(select(Exercise).where(Exercise.id == ex_id)).first()
                    
                    variants = ex_data.get("acceptable_answers") or []
                    correct_ans = ex_data.get("correct_answer", "").strip()
                    if correct_ans and correct_ans not in variants:
                        variants.append(correct_ans)

                    # Determine book key
                    b_key = ex_data.get("book") or book_code

                    if existing:
                        existing.book = b_key
                        existing.page_identifier = p_ident
                        existing.sentence_given = ex_data.get("sentence_given", "").strip()
                        existing.keyword = ex_data.get("keyword", "").strip()
                        existing.incomplete_phrase = ex_data.get("incomplete_phrase", "").strip()
                        existing.correct_answer = correct_ans
                        existing.set_acceptable_answers(variants)
                        existing.explanation = ex_data.get("explanation")
                        existing.is_locked = bool(ex_data.get("is_locked", False))
                        existing.verified = bool(ex_data.get("verified", False))
                        session.add(existing)
                        total_updated += 1
                    else:
                        new_ex = Exercise(
                            id=ex_id,
                            book=b_key,
                            page_identifier=p_ident,
                            page=p_num,
                            exercise_number=ex_data.get("exercise_number", 1),
                            sentence_given=ex_data.get("sentence_given", "").strip(),
                            keyword=ex_data.get("keyword", "").strip(),
                            incomplete_phrase=ex_data.get("incomplete_phrase", "").strip(),
                            correct_answer=correct_ans,
                            explanation=ex_data.get("explanation"),
                            is_locked=bool(ex_data.get("is_locked", False)),
                            verified=bool(ex_data.get("verified", False))
                        )
                        new_ex.set_acceptable_answers(variants)
                        session.add(new_ex)
                        total_inserted += 1

        session.commit()

    print(f"Seeding completed successfully! Inserted: {total_inserted}, Updated: {total_updated}")

if __name__ == "__main__":
    seed_database()
