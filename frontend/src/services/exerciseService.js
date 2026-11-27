import exercisesData from '../data/exercises.json';
import { gradeAnswer } from './grader.js';

export const BOOK_LABELS = {
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
};

const EXAM_HISTORY_KEY = 'b2_exam_history';
const SUGGESTIONS_KEY = 'b2_user_suggestions';

export function getBooks() {
  const counts = {};
  for (const ex of exercisesData) {
    counts[ex.book] = (counts[ex.book] || 0) + 1;
  }

  const booksData = Object.entries(counts).map(([key, count]) => ({
    key,
    title: BOOK_LABELS[key] || (key.charAt(0).toUpperCase() + key.slice(1)),
    count
  }));

  const sortKey = (b) => {
    const k = b.key;
    if (k === 'libro_clase' || k === 'book0') return '0';
    if (k === 'book1') return '1';
    if (k === 'book2') return '2';
    if (k === 'book3') return '3';
    if (k === 'book4') return '4';
    if (k === 'handbook') return '5';
    return '9';
  };

  booksData.sort((a, b) => sortKey(a).localeCompare(sortKey(b)));

  return {
    total_exercises: exercisesData.length,
    books: booksData
  };
}

export function getRandomExercise(bookFilter = 'all', excludeIds = []) {
  let filtered = exercisesData;
  if (bookFilter && bookFilter !== 'all') {
    filtered = filtered.filter(ex => ex.book === bookFilter);
  }

  if (excludeIds && excludeIds.length > 0) {
    const excludeSet = new Set(excludeIds.map(Number));
    const nonExcluded = filtered.filter(ex => !excludeSet.has(ex.id));
    if (nonExcluded.length > 0) {
      filtered = nonExcluded;
    }
  }

  if (!filtered.length) {
    filtered = exercisesData;
  }

  const ex = filtered[Math.floor(Math.random() * filtered.length)];
  return {
    id: ex.id,
    book: ex.book,
    book_label: BOOK_LABELS[ex.book] || ex.book,
    page_identifier: ex.page_identifier,
    page: ex.page,
    exercise_number: ex.exercise_number,
    sentence_given: ex.sentence_given,
    keyword: ex.keyword,
    incomplete_phrase: ex.incomplete_phrase,
    verified: ex.verified,
    is_locked: ex.is_locked
  };
}

export function checkPracticeAnswer(exerciseId, userAnswer) {
  const ex = exercisesData.find(e => e.id === Number(exerciseId));
  if (!ex) {
    throw new Error(`Exercise ${exerciseId} not found`);
  }

  const res = gradeAnswer(
    userAnswer,
    ex.correct_answer,
    ex.keyword,
    ex.acceptable_answers
  );

  return {
    score: res.score,
    max: res.max,
    is_exact: res.is_exact,
    matched_variant: res.matched_variant,
    feedback: res.feedback,
    correct_answer: ex.correct_answer,
    acceptable_answers: ex.acceptable_answers,
    explanation: ex.explanation
  };
}

export function startExam(bookFilter = 'all') {
  let pool = exercisesData;
  if (bookFilter && bookFilter !== 'all') {
    const bookPool = pool.filter(ex => ex.book === bookFilter);
    if (bookPool.length >= 6) {
      pool = bookPool;
    }
  }

  // Pick 6 unique random exercises
  const shuffled = [...pool].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 6);
  const examId = 'exam_' + Math.random().toString(36).substring(2, 9) + '_' + Date.now();

  return {
    exam_id: examId,
    total_questions: 6,
    max_score: 12,
    time_limit_seconds: 600, // 10 minutes
    book_filter: bookFilter || 'all',
    book_label: (bookFilter && bookFilter !== 'all') ? (BOOK_LABELS[bookFilter] || bookFilter) : 'All sources',
    exercises: selected.map(ex => ({
      id: ex.id,
      book: ex.book,
      book_label: BOOK_LABELS[ex.book] || ex.book,
      page_identifier: ex.page_identifier,
      sentence_given: ex.sentence_given,
      keyword: ex.keyword,
      incomplete_phrase: ex.incomplete_phrase,
    }))
  };
}

export function submitExam({ exam_id, student_name, student_device_id, book_filter, time_taken_seconds, answers }) {
  let totalScore = 0;
  const resultsDetail = [];

  for (const ans of (answers || [])) {
    const ex = exercisesData.find(e => e.id === Number(ans.exercise_id));
    if (!ex) continue;

    const evalRes = gradeAnswer(
      ans.user_answer,
      ex.correct_answer,
      ex.keyword,
      ex.acceptable_answers
    );

    totalScore += evalRes.score;

    resultsDetail.push({
      exercise_id: ex.id,
      sentence_given: ex.sentence_given,
      keyword: ex.keyword,
      incomplete_phrase: ex.incomplete_phrase,
      user_answer: ans.user_answer,
      correct_answer: ex.correct_answer,
      acceptable_answers: ex.acceptable_answers,
      explanation: ex.explanation,
      score_awarded: evalRes.score,
      max_score: 2,
      is_exact: evalRes.is_exact,
      feedback: evalRes.feedback
    });
  }

  const percentage = Math.round((totalScore / 12) * 1000) / 10;
  const passed = totalScore >= 8; // Cambridge 60%+ pass threshold

  const record = {
    id: exam_id,
    student_name: student_name || 'Anonymous',
    student_device_id: student_device_id || 'local',
    mode: 'exam',
    book_filter: book_filter || 'all',
    book_label: (book_filter && book_filter !== 'all') ? (BOOK_LABELS[book_filter] || book_filter) : 'All sources',
    total_score: totalScore,
    max_score: 12,
    percentage,
    passed,
    time_taken_seconds: time_taken_seconds || 0,
    submitted_at: new Date().toISOString(),
    results: resultsDetail
  };

  saveExamToHistory(record);

  return {
    exam_id,
    book_filter: book_filter || 'all',
    book_label: record.book_label,
    total_score: totalScore,
    max_score: 12,
    percentage,
    passed,
    time_taken_seconds: time_taken_seconds || 0,
    results: resultsDetail
  };
}

export function saveExamToHistory(record) {
  try {
    const history = getExamHistory();
    history.unshift(record);
    const trimmed = history.slice(0, 50); // Keep last 50 attempts
    localStorage.setItem(EXAM_HISTORY_KEY, JSON.stringify(trimmed));
  } catch (err) {
    console.error('Failed to save exam history', err);
  }
}

export function getExamHistory(studentDeviceId) {
  try {
    const raw = localStorage.getItem(EXAM_HISTORY_KEY);
    if (!raw) return [];
    const list = JSON.parse(raw);
    if (!Array.isArray(list)) return [];
    if (studentDeviceId) {
      return list.filter(item => !item.student_device_id || item.student_device_id === studentDeviceId);
    }
    return list;
  } catch (err) {
    console.error('Failed to load exam history', err);
    return [];
  }
}

export function submitSuggestion(exerciseId, studentName, suggestedAnswer) {
  try {
    const raw = localStorage.getItem(SUGGESTIONS_KEY) || '[]';
    const suggestions = JSON.parse(raw);
    suggestions.push({
      id: Date.now(),
      exercise_id: exerciseId,
      student_name: studentName || 'Anonymous',
      suggested_answer: suggestedAnswer,
      created_at: new Date().toISOString()
    });
    localStorage.setItem(SUGGESTIONS_KEY, JSON.stringify(suggestions));
    return { ok: true };
  } catch (err) {
    console.error('Failed to store suggestion', err);
    return { ok: false };
  }
}
