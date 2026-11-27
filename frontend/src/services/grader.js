export const CONTRACTIONS = {
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
};

export function cleanWords(text) {
  if (!text) return "";
  const normalized = text.trim().toLowerCase().replace(/['’`]/g, "'");
  const words = normalized.match(/[\w']+/g) || [];
  return words.join(" ");
}

export function normalizeContractions(text) {
  if (!text) return "";
  let cleaned = cleanWords(text);
  for (const [c, full] of Object.entries(CONTRACTIONS)) {
    const escaped = c.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'g');
    cleaned = cleaned.replace(regex, full);
  }
  const words = cleaned.match(/[\w']+/g) || [];
  return words.join(" ");
}

export function countWords(text) {
  const cleaned = cleanWords(text);
  if (!cleaned) return 0;
  return cleaned.split(/\s+/).length;
}

export function gradeAnswer(userAns, correctAns, keyword, acceptableAnswers = []) {
  const userRaw = (userAns || "").trim();
  const kw = (keyword || "").trim().toUpperCase();

  if (!userRaw) {
    return {
      score: 0,
      max: 2,
      is_exact: false,
      matched_variant: null,
      feedback: "Empty answer. (0/2 marks)"
    };
  }

  // Keyword check: keyword must be included without changing form
  if (!userRaw.toLowerCase().includes(kw.toLowerCase())) {
    return {
      score: 0,
      max: 2,
      is_exact: false,
      matched_variant: null,
      feedback: `Missing or modified keyword '${kw}'. You must use the given word unchanged.`
    };
  }

  const uClean = cleanWords(userRaw);
  const uNorm = normalizeContractions(userRaw);

  const candidates = [correctAns];
  if (Array.isArray(acceptableAnswers)) {
    for (const acc of acceptableAnswers) {
      if (acc && acc.trim() && !candidates.includes(acc.trim())) {
        candidates.push(acc.trim());
      }
    }
  }

  for (const cand of candidates) {
    if (!cand) continue;
    const cClean = cleanWords(cand);
    // 1. Direct word-for-word exact match
    if (uClean === cClean) {
      return {
        score: 2,
        max: 2,
        is_exact: true,
        matched_variant: cand,
        feedback: "100% Exact Match! Correct (2/2 marks)"
      };
    }

    // 2. Contraction-normalized exact match
    const cNorm = normalizeContractions(cand);
    if (uNorm === cNorm) {
      return {
        score: 2,
        max: 2,
        is_exact: true,
        matched_variant: cand,
        feedback: "100% Exact Match (Contraction equivalent)! Correct (2/2 marks)"
      };
    }
  }

  // Word count advisory if incorrect
  const wCount = countWords(userRaw);
  let extraHint = "";
  if (wCount < 2 || wCount > 5) {
    extraHint = ` (Note: Cambridge B2 Part 4 requires between 2 and 5 words; your answer has ${wCount} words).`;
  }

  return {
    score: 0,
    max: 2,
    is_exact: false,
    matched_variant: null,
    feedback: `Incorrect. Your answer does not match the official key.${extraHint}`
  };
}
