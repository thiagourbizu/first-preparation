<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Clock, Check, X, Award, AlertCircle, ChevronDown, BookOpen } from 'lucide-vue-next'

const props = defineProps({
  studentName: { type: String, default: 'Anonymous' },
  studentDeviceId: { type: String, required: true }
})

const emit = defineEmits(['view-history'])

// Books / dataset sources
const books = ref([])
const totalExercises = ref(0)
const selectedBook = ref('all')

// States: 'idle' | 'active' | 'submitting' | 'finished'
const examState = ref('idle')
const examId = ref('')
const exercises = ref([])
const answers = ref({}) // { [exId]: string }
const timeRemaining = ref(600) // 10 minutes in seconds
let timerInterval = null

const examResult = ref(null)
const submitWarning = ref('')

const selectedBookLabel = computed(() => {
  if (selectedBook.value === 'all') return 'All sources'
  const found = books.value.find(b => b.key === selectedBook.value)
  return found ? found.title : 'Libro que usamos en clase'
})

const formattedTime = computed(() => {
  const m = Math.floor(timeRemaining.value / 60)
  const s = timeRemaining.value % 60
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
})

const answeredCount = computed(() => {
  return exercises.value.filter(ex => (answers.value[ex.id] || '').trim().length > 0).length
})

function getSentenceParts(incompletePhrase) {
  const phrase = incompletePhrase || ''
  const splitIndex = phrase.indexOf('...')
  if (splitIndex !== -1) {
    return {
      before: phrase.substring(0, splitIndex).trim(),
      after: phrase.substring(splitIndex + 3).trim()
    }
  }
  return { before: phrase, after: '' }
}

function getWordCount(exId) {
  const text = (answers.value[exId] || '').trim()
  if (!text) return 0
  return text.split(/\s+/).filter(w => w.length > 0).length
}

async function fetchBooks() {
  try {
    const res = await fetch('/api/practice/books')
    if (res.ok) {
      const data = await res.json()
      books.value = data.books || []
      totalExercises.value = data.total_exercises || 0
    }
  } catch (e) {
    console.error('Error fetching books for exam', e)
  }
}

onMounted(() => {
  fetchBooks()
})

function resetToIdle() {
  if (timerInterval) clearInterval(timerInterval)
  examState.value = 'idle'
  examResult.value = null
  answers.value = {}
  timeRemaining.value = 600
  submitWarning.value = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function startNewExam() {
  examState.value = 'idle'
  answers.value = {}
  examResult.value = null
  timeRemaining.value = 600
  submitWarning.value = ''

  try {
    const res = await fetch('/api/exam/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        book: selectedBook.value,
        student_name: props.studentName || 'Anonymous',
        student_device_id: props.studentDeviceId
      })
    })

    if (!res.ok) throw new Error('Failed to start exam')
    const data = await res.json()
    examId.value = data.exam_id
    exercises.value = data.exercises || []
    
    // Initialize answers map
    exercises.value.forEach(ex => {
      answers.value[ex.id] = ''
    })

    examState.value = 'active'

    if (timerInterval) clearInterval(timerInterval)
    timerInterval = setInterval(() => {
      if (timeRemaining.value > 0) {
        timeRemaining.value -= 1
      } else {
        clearInterval(timerInterval)
        submitExam(true)
      }
    }, 1000)
  } catch (e) {
    console.error('Error starting exam', e)
  }
}

async function submitExam(isAuto = false) {
  if (examState.value === 'submitting' || examState.value === 'finished') return

  if (!isAuto && answeredCount.value < exercises.value.length) {
    if (!submitWarning.value) {
      submitWarning.value = `You have completed ${answeredCount.value} of 6 questions. Click again to confirm submission.`
      return
    }
  }

  if (timerInterval) clearInterval(timerInterval)
  examState.value = 'submitting'
  submitWarning.value = ''

  const formattedAnswers = exercises.value.map(ex => ({
    exercise_id: ex.id,
    user_answer: (answers.value[ex.id] || '').trim()
  }))

  const timeTaken = 600 - timeRemaining.value

  try {
    const res = await fetch('/api/exam/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exam_id: examId.value,
        student_name: props.studentName || 'Anonymous',
        student_device_id: props.studentDeviceId,
        book_filter: selectedBook.value,
        time_taken_seconds: timeTaken,
        answers: formattedAnswers
      })
    })

    if (!res.ok) throw new Error('Failed to submit exam')
    const data = await res.json()
    examResult.value = data
    examState.value = 'finished'
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    console.error('Submit failed', e)
    examState.value = 'active'
  }
}

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8 sm:py-12">
    
    <!-- 1. Idle State: Exam Start Screen -->
    <div v-if="examState === 'idle'" class="bg-white rounded-2xl border border-nordic-200 p-8 sm:p-12 text-center space-y-6">
      <div class="space-y-2">
        <span class="text-xs font-semibold tracking-wider uppercase text-nordic-400">
          Official Cambridge Simulation
        </span>
        <h2 class="font-heading font-bold text-2xl sm:text-3xl text-nordic-900">
          Cambridge B2 First Mock Exam
        </h2>
        <p class="text-sm text-nordic-500 max-w-md mx-auto leading-relaxed">
          Complete all 6 key word transformations on a single page under real 10-minute exam conditions.
        </p>
      </div>

      <!-- Specs Row -->
      <div class="grid grid-cols-3 gap-3 max-w-sm mx-auto text-center py-1">
        <div class="p-3 rounded-xl bg-nordic-50 border border-nordic-200">
          <span class="text-[10px] text-nordic-400 uppercase tracking-wider block">Format</span>
          <span class="font-mono text-base font-bold text-nordic-900">All 6 Tasks</span>
        </div>
        <div class="p-3 rounded-xl bg-nordic-50 border border-nordic-200">
          <span class="text-[10px] text-nordic-400 uppercase tracking-wider block">Marks</span>
          <span class="font-mono text-base font-bold text-nordic-900">12 Marks</span>
        </div>
        <div class="p-3 rounded-xl bg-nordic-50 border border-nordic-200">
          <span class="text-[10px] text-nordic-400 uppercase tracking-wider block">Duration</span>
          <span class="font-mono text-base font-bold text-nordic-900">10 Min</span>
        </div>
      </div>

      <!-- Source Dataset Selection -->
      <div class="space-y-2 max-w-sm mx-auto text-left py-1">
        <div class="flex items-center justify-between">
          <label for="exam-source-select" class="text-[11px] font-semibold tracking-wider uppercase text-nordic-500">
            Practice Source / Dataset
          </label>
          <span class="text-[11px] font-mono text-nordic-400">
            {{ totalExercises }} total
          </span>
        </div>
        <div class="relative">
          <select
            id="exam-source-select"
            v-model="selectedBook"
            class="w-full appearance-none rounded-xl bg-nordic-50 border border-nordic-200 px-3.5 py-2.5 text-xs font-semibold text-nordic-800 hover:border-nordic-400 focus:outline-none focus:ring-2 focus:ring-cobalt/20 focus:border-cobalt transition cursor-pointer pr-10 shadow-2xs"
          >
            <option value="all">All sources ({{ totalExercises }} exercises)</option>
            <option
              v-for="b in books"
              :key="b.key"
              :value="b.key"
            >
              {{ b.title }} ({{ b.count }} exercises)
            </option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-nordic-400">
            <ChevronDown class="w-4 h-4" />
          </div>
        </div>
        <p class="text-[11px] text-nordic-400 leading-normal">
          6 random questions will be drawn exclusively from the selected collection.
        </p>
      </div>

      <div>
        <button
          @click="startNewExam"
          class="px-8 py-3 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-sm shadow-xs transition"
        >
          Start Timed Exam
        </button>
      </div>
    </div>

    <!-- 2. Active Exam State: All 6 Tasks on Screen -->
    <div v-else-if="examState === 'active' || examState === 'submitting'" class="space-y-6">
      
      <!-- Sticky Exam Control Header -->
      <div class="sticky top-16 z-30 bg-white/95 backdrop-blur-sm border border-nordic-200 rounded-xl p-4 shadow-sm flex items-center justify-between gap-4">
        <div class="flex items-center gap-2.5">
          <span class="font-heading font-bold text-sm text-nordic-900">
            Mock Exam
          </span>
          <span class="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-md bg-nordic-100 text-nordic-700 border border-nordic-200">
            <BookOpen class="w-3 h-3 text-nordic-400" />
            <span>{{ selectedBookLabel }}</span>
          </span>
          <span class="text-xs font-mono text-nordic-500">
            ({{ answeredCount }} / 6 Answered)
          </span>
        </div>

        <div class="flex items-center gap-3">
          <!-- Zen Timer Pill -->
          <div
            :class="[
              'flex items-center gap-2 px-3 py-1 rounded-full font-mono text-xs font-bold border transition-colors',
              timeRemaining < 120
                ? 'bg-rose-50 text-rose-600 border-rose-200 animate-pulse'
                : 'bg-nordic-100 text-nordic-700 border-nordic-200'
            ]"
          >
            <Clock class="w-3.5 h-3.5" />
            <span>{{ formattedTime }}</span>
          </div>

          <!-- Quick Top Submit -->
          <button
            @click="submitExam(false)"
            :disabled="examState === 'submitting'"
            class="px-4 py-1.5 rounded-lg bg-nordic-900 hover:bg-cobalt text-white text-xs font-semibold transition"
          >
            Submit
          </button>
        </div>
      </div>

      <!-- Warning if submitting incomplete -->
      <div v-if="submitWarning" class="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs flex items-center gap-2 animate-fade-in">
        <AlertCircle class="w-4 h-4 shrink-0 text-amber-600" />
        <span class="flex-1 font-medium">{{ submitWarning }}</span>
        <button @click="submitWarning = ''" class="text-amber-600 hover:underline">Dismiss</button>
      </div>

      <!-- All 6 Questions Listed Vertically -->
      <div class="space-y-6">
        <div
          v-for="(ex, index) in exercises"
          :key="ex.id"
          class="bg-white rounded-2xl border border-nordic-200 p-6 sm:p-8 shadow-xs space-y-6"
        >
          <!-- Task Header -->
          <div class="flex items-center justify-between border-b border-nordic-100 pb-3">
            <span class="font-mono text-xs font-bold text-nordic-500 uppercase tracking-wider">
              Task {{ index + 1 }} of 6
            </span>
            <span class="text-[11px] font-semibold text-nordic-400">
              2 Marks
            </span>
          </div>

          <!-- Original Sentence -->
          <div class="space-y-1">
            <span class="text-[10px] font-semibold tracking-wider uppercase text-nordic-400 block">
              Original Sentence
            </span>
            <p class="font-heading font-medium text-base sm:text-lg text-nordic-900 leading-relaxed">
              "{{ ex.sentence_given }}"
            </p>
          </div>

          <!-- Keyword Chip -->
          <div class="flex items-center gap-3 p-3 rounded-xl bg-nordic-50 border border-nordic-200/80">
            <span class="text-xs font-semibold text-nordic-500">GIVEN WORD:</span>
            <span class="px-3 py-0.5 rounded-md bg-white border border-nordic-200 font-mono text-sm font-bold tracking-wider text-cobalt">
              {{ ex.keyword }}
            </span>
          </div>

          <!-- Second Sentence with Well-Fit Gap Input -->
          <div class="space-y-2">
            <label class="text-[10px] font-semibold tracking-wider uppercase text-nordic-400 block">
              Second Sentence Transformation
            </label>

            <div class="p-4 rounded-xl bg-nordic-50 border border-nordic-200 leading-relaxed text-base text-nordic-900 font-medium flex flex-wrap items-baseline gap-y-2">
              <span v-if="getSentenceParts(ex.incomplete_phrase).before" class="mr-2">
                {{ getSentenceParts(ex.incomplete_phrase).before }}
              </span>
              
              <input
                v-model="answers[ex.id]"
                type="text"
                placeholder="type 2 to 5 words..."
                class="px-3.5 py-1.5 my-1 mx-2 rounded-lg border border-nordic-300 bg-white text-nordic-900 font-mono text-sm sm:text-base focus:border-cobalt focus:ring-1 focus:ring-cobalt focus:outline-none transition min-w-[220px] sm:min-w-[280px]"
                autocapitalize="off"
                spellcheck="false"
              />

              <span v-if="getSentenceParts(ex.incomplete_phrase).after" class="ml-2">
                {{ getSentenceParts(ex.incomplete_phrase).after }}
              </span>
            </div>

            <!-- Word count indicator for this question -->
            <div class="flex items-center justify-between text-xs px-1 font-mono text-nordic-500 pt-0.5">
              <span
                :class="[
                  'px-1.5 py-0.5 rounded text-[11px] font-bold',
                  getWordCount(ex.id) === 0
                    ? 'text-nordic-400'
                    : getWordCount(ex.id) >= 2 && getWordCount(ex.id) <= 5
                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                    : 'bg-rose-50 text-rose-700 border border-rose-200'
                ]"
              >
                {{ getWordCount(ex.id) }} {{ getWordCount(ex.id) === 1 ? 'WORD' : 'WORDS' }}
              </span>
              <span class="text-nordic-400 text-[11px]">
                Must use {{ ex.keyword }} unchanged
              </span>
            </div>
          </div>

        </div>
      </div>

      <!-- Bottom Submission Action Bar -->
      <div class="bg-white rounded-2xl border border-nordic-200 p-6 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xs">
        <div>
          <p class="font-heading font-bold text-sm text-nordic-900">
            Ready to finish your test?
          </p>
          <p class="text-xs text-nordic-500 mt-0.5">
            {{ answeredCount }} of 6 questions answered · Timer stops on submission
          </p>
        </div>

        <button
          @click="submitExam(false)"
          :disabled="examState === 'submitting'"
          class="w-full sm:w-auto px-8 py-3 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-sm transition shadow-xs disabled:opacity-50"
        >
          {{ examState === 'submitting' ? 'Evaluating Exam...' : 'Finish & Submit Exam (6 Tasks)' }}
        </button>
      </div>

    </div>

    <!-- 3. Finished State: Comprehensive Exam Breakdown -->
    <div v-else-if="examState === 'finished' && examResult" class="space-y-8 animate-fade-in">
      
      <!-- Score Summary Card -->
      <div class="bg-white rounded-2xl border border-nordic-200 p-8 sm:p-10 text-center space-y-4">
        <span class="text-xs font-semibold tracking-wider uppercase text-nordic-400">
          Official Cambridge Simulation Result
        </span>

        <h2 class="font-heading font-extrabold text-3xl sm:text-4xl text-nordic-900">
          {{ examResult.total_score }} / 12 Marks
          <span class="text-lg font-normal text-nordic-400">({{ examResult.percentage }}%)</span>
        </h2>

        <p class="text-xs sm:text-sm font-semibold">
          <span v-if="examResult.passed" class="text-emerald-600">
            Passed · Meets Cambridge B2 First Level ($\ge 8/12$ Marks)
          </span>
          <span v-else class="text-rose-600">
            Below Cambridge Pass Threshold (Requires $\ge 8/12$ Marks)
          </span>
        </p>

        <div class="flex flex-wrap items-center justify-center gap-2.5 text-xs text-nordic-400 font-mono pt-2">
          <span>Source: <strong class="text-nordic-700 font-semibold">{{ examResult.book_label || selectedBookLabel }}</strong></span>
          <span>·</span>
          <span>Time: {{ Math.floor(examResult.time_taken_seconds / 60) }}m {{ examResult.time_taken_seconds % 60 }}s</span>
          <span>·</span>
          <span>Student: {{ props.studentName || 'Anonymous' }}</span>
        </div>

        <div class="flex flex-wrap justify-center gap-3 pt-4">
          <button
            @click="startNewExam"
            class="px-5 py-2.5 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-xs transition"
          >
            Take Another Exam
          </button>
          <button
            @click="resetToIdle"
            class="px-5 py-2.5 rounded-xl border border-nordic-200 text-nordic-700 font-semibold text-xs hover:border-nordic-400 hover:bg-nordic-50 transition"
          >
            Change Dataset / Source
          </button>
          <button
            @click="emit('view-history')"
            class="px-5 py-2.5 rounded-xl border border-nordic-200 text-nordic-700 font-semibold text-xs hover:border-nordic-400 hover:bg-nordic-50 transition"
          >
            View Score History
          </button>
        </div>
      </div>

      <!-- Question by Question Breakdown -->
      <div class="space-y-4">
        <h3 class="text-xs font-semibold tracking-wider uppercase text-nordic-400 px-1">
          Detailed Assessment (Tasks 1 to 6)
        </h3>

        <div
          v-for="(r, i) in examResult.results"
          :key="r.exercise_id"
          class="bg-white rounded-xl border border-nordic-200 p-5 sm:p-6 space-y-3"
        >
          <div class="flex items-center justify-between text-xs">
            <span class="font-mono font-bold text-nordic-500">Task {{ i + 1 }} of 6</span>
            <span
              :class="[
                'font-mono font-bold px-2 py-0.5 rounded',
                r.score_awarded === 2
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              ]"
            >
              {{ r.score_awarded }} / 2 Marks
            </span>
          </div>

          <p class="text-sm font-medium text-nordic-800 leading-relaxed">
            "{{ r.sentence_given }}"
          </p>

          <div class="flex items-center gap-2 text-xs">
            <span class="text-nordic-400 font-semibold">Keyword:</span>
            <span class="font-mono font-bold uppercase text-cobalt">{{ r.keyword }}</span>
          </div>

          <!-- User Answer vs Key -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono pt-1">
            <div class="p-3 rounded-lg bg-nordic-50 border border-nordic-200/80">
              <span class="text-nordic-400 block text-[10px] uppercase font-semibold">Your Answer:</span>
              <span class="font-bold text-nordic-900">
                {{ r.user_answer || '(Blank — no answer provided)' }}
              </span>
            </div>
            <div class="p-3 rounded-lg bg-nordic-50 border border-nordic-200/80">
              <span class="text-nordic-400 block text-[10px] uppercase font-semibold">Official Key:</span>
              <span class="font-bold text-emerald-600">
                {{ r.correct_answer }}
              </span>
            </div>
          </div>

          <!-- Explanation if present -->
          <div v-if="r.explanation" class="text-xs text-nordic-500 italic pt-1 border-t border-nordic-100">
            💡 {{ r.explanation }}
          </div>
        </div>

      </div>

    </div>

  </div>
</template>
