import re
from typing import List, Optional, Dict, Any

CONTRACTIONS = {
    "didn't": "did not",
    "don't": "do not",
    "doesn't": "does not",
    "haven't": "have not",
    "hasn't": "has not",
    "hadn't": "had not",
    "won't": "will not",
    "wouldn't": "would not",
    "can't": "cannot",
    "couldn't": "could not",
    "shouldn't": "should not",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "it's": "it is",
    "there's": "there is",
    "that's": "that is",
    "i'm": "i am",
    "you're": "you are",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "i'd": "i would",
    "you'd": "you would",
    "he'd": "he would",
    "she'd": "she would",
    "we'd": "we would",
    "they'd": "they would",
}

def clean_words(text: str) -> str:
    """Normalize apostrophes, lowercase, and collapse multiple spaces."""
    if not text:
        return ""
    text = re.sub(r"[\'’`]", "'", text.strip().lower())
    words = re.findall(r"[\w']+", text)
    return " ".join(words)

def normalize_contractions(text: str) -> str:
    """Expand known contractions for equivalence checks."""
    if not text:
        return ""
    cleaned = clean_words(text)
    for c, full in CONTRACTIONS.items():
        cleaned = re.sub(r"\b" + re.escape(c) + r"\b", full, cleaned)
    return " ".join(re.findall(r"[\w']+", cleaned))

def count_words(text: str) -> int:
    """Returns number of words in string."""
    cleaned = clean_words(text)
    if not cleaned:
        return 0
    return len(cleaned.split())

def grade_answer(
    user_ans: str,
    correct_ans: str,
    keyword: str,
    acceptable_answers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Grades user answer requiring 100% exact match against:
    1. The primary correct answer, OR
    2. Any entry in acceptable_answers, OR
    3. Contraction-normalized equivalence (e.g. wouldn't == would not).
    """
    user_raw = (user_ans or "").strip()
    kw = (keyword or "").strip().upper()
    
    if not user_raw:
        return {
            "score": 0,
            "max": 2,
            "is_exact": False,
            "matched_variant": None,
            "feedback": "Empty answer. (0/2 marks)"
        }

    # Keyword check: keyword must be included without changing form
    if kw.lower() not in user_raw.lower():
        return {
            "score": 0,
            "max": 2,
            "is_exact": False,
            "matched_variant": None,
            "feedback": f"Missing or modified keyword '{kw}'. You must use the given word unchanged."
        }

    u_clean = clean_words(user_raw)
    u_norm = normalize_contractions(user_raw)

    candidates = [correct_ans]
    if acceptable_answers:
        for acc in acceptable_answers:
            if acc and acc.strip() and acc.strip() not in candidates:
                candidates.append(acc.strip())

    for cand in candidates:
        if not cand:
            continue
        c_clean = clean_words(cand)
        # 1. Direct word-for-word exact match
        if u_clean == c_clean:
            return {
                "score": 2,
                "max": 2,
                "is_exact": True,
                "matched_variant": cand,
                "feedback": "100% Exact Match! Correct (2/2 marks)"
            }

        # 2. Contraction-normalized exact match
        c_norm = normalize_contractions(cand)
        if u_norm == c_norm:
            return {
                "score": 2,
                "max": 2,
                "is_exact": True,
                "matched_variant": cand,
                "feedback": "100% Exact Match (Contraction equivalent)! Correct (2/2 marks)"
            }

    # Word count advisory if incorrect
    w_count = count_words(user_raw)
    extra_hint = ""
    if w_count < 2 or w_count > 5:
        extra_hint = f" (Note: Cambridge B2 Part 4 requires between 2 and 5 words; your answer has {w_count} words)."

    return {
        "score": 0,
        "max": 2,
        "is_exact": False,
        "matched_variant": None,
        "feedback": f"Incorrect. Your answer does not match the official key.{extra_hint}"
    }
