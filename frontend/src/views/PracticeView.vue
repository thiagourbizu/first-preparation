<script setup>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { ArrowRight, RefreshCw, Check, X, MessageSquarePlus, CornerDownLeft } from 'lucide-vue-next'

const props = defineProps({
  studentName: { type: String, default: 'Anonymous' },
  studentDeviceId: { type: String, required: true }
})

const books = ref([])
const totalExercises = ref(0)
const selectedBook = ref('all')

const currentExercise = ref(null)
const userAnswer = ref('')
const isEvaluating = ref(false)
const result = ref(null)
const seenIds = ref([])

// Suggestion state
const isSuggestOpen = ref(false)
const suggestText = ref('')
const isSubmittingSuggest = ref(false)
const suggestFeedback = ref('')

const inputRef = ref(null)

// Split incomplete phrase around "..."
const sentenceParts = computed(() => {
  if (!currentExercise.value) return { before: '', after: '' }
  const phrase = currentExercise.value.incomplete_phrase || ''
  const splitIndex = phrase.indexOf('...')
  if (splitIndex !== -1) {
    return {
      before: phrase.substring(0, splitIndex).trim(),
      after: phrase.substring(splitIndex + 3).trim()
    }
  }
  return { before: phrase, after: '' }
})

const wordCount = computed(() => {
  const text = userAnswer.value.trim()
  if (!text) return 0
  return text.split(/\s+/).filter(w => w.length > 0).length
})

const isWordCountValid = computed(() => {
  return wordCount.value >= 2 && wordCount.value <= 5
})

async function fetchBooks() {
  try {
    const res = await fetch('/api/practice/books')
    const data = await res.json()
    books.value = data.books || []
    totalExercises.value = data.total_exercises || 0
  } catch (e) {
    console.error('Error fetching books', e)
  }
}

async function loadNextExercise() {
  isEvaluating.value = false
  result.value = null
  userAnswer.value = ''
  suggestFeedback.value = ''

  try {
    const exclude = seenIds.value.slice(-30).join(',')
    const res = await fetch(`/api/practice/random?book=${selectedBook.value}&exclude_ids=${exclude}`)
    if (!res.ok) throw new Error('Failed to load')
    const ex = await res.json()
    currentExercise.value = ex
    seenIds.value.push(ex.id)

    await nextTick()
    if (inputRef.value) {
      inputRef.value.focus()
    }
  } catch (e) {
    console.error('Error loading exercise', e)
  }
}

async function handleCheck() {
  if (!userAnswer.value.trim() || isEvaluating.value || result.value) return
  isEvaluating.value = true

  try {
    const res = await fetch('/api/practice/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exercise_id: currentExercise.value.id,
        user_answer: userAnswer.value.trim(),
        student_name: props.studentName || 'Anonymous',
        student_device_id: props.studentDeviceId
      })
    })

    const data = await res.json()
    result.value = data
  } catch (e) {
    console.error('Check failed', e)
  } finally {
    isEvaluating.value = false
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault()
    if (result.value) {
      loadNextExercise()
    } else {
      handleCheck()
    }
  } else if (e.key === 'Escape' && !result.value) {
    userAnswer.value = ''
  }
}

async function submitSuggestion() {
  if (!suggestText.value.trim() || isSubmittingSuggest.value) return
  isSubmittingSuggest.value = true
  suggestFeedback.value = ''

  try {
    const res = await fetch('/api/suggestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        exercise_id: currentExercise.value.id,
        student_name: props.studentName || 'Anonymous',
        suggested_answer: suggestText.value.trim()
      })
    })
    const data = await res.json()
    suggestFeedback.value = data.message || 'Suggestion sent to teacher!'
    setTimeout(() => {
      isSuggestOpen.value = false
      suggestText.value = ''
    }, 1200)
  } catch (e) {
    suggestFeedback.value = 'Failed to submit suggestion.'
  } finally {
    isSubmittingSuggest.value = false
  }
}

function openSuggestModal() {
  suggestText.value = userAnswer.value
  suggestFeedback.value = ''
  isSuggestOpen.value = true
}

watch(selectedBook, () => {
  seenIds.value = []
  loadNextExercise()
})

onMounted(async () => {
  await fetchBooks()
  await loadNextExercise()
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8 sm:py-12">
    <!-- Subtle Subheader: Dataset selector & Exercise ID -->
    <div class="flex items-center justify-between text-xs text-nordic-500 mb-4 px-1">
      <div class="flex items-center gap-2">
        <span class="font-mono font-medium text-nordic-400">Exercise #{{ currentExercise?.id || '...' }}</span>
        <span>·</span>
        <select
          v-model="selectedBook"
          class="bg-transparent border-none text-xs font-semibold text-nordic-700 focus:outline-none cursor-pointer hover:text-nordic-900"
        >
          <option value="all">All Sources ({{ totalExercises }} items)</option>
          <option v-for="b in books" :key="b.key" :value="b.key">
            {{ b.title }} ({{ b.count }})
          </option>
        </select>
      </div>

      <button
        @click="loadNextExercise"
        class="flex items-center gap-1.5 text-nordic-500 hover:text-nordic-900 transition font-medium"
      >
        <RefreshCw class="w-3.5 h-3.5" />
        <span>Skip</span>
      </button>
    </div>

    <!-- Main Clean Focus Card -->
    <div v-if="currentExercise" class="bg-white rounded-2xl border border-nordic-200 p-6 sm:p-10 shadow-xs space-y-8">
      
      <!-- Academic Directive -->
      <div class="flex items-center justify-between border-b border-nordic-100 pb-4 text-[11px] font-semibold tracking-wider uppercase text-nordic-400">
        <span>Complete the second sentence so that it has a similar meaning</span>
        <span>2 Marks</span>
      </div>

      <!-- Original Sentence -->
      <div class="space-y-1.5">
        <span class="text-[11px] font-semibold tracking-wider uppercase text-nordic-400 block">
          Original Sentence
        </span>
        <p class="font-heading font-medium text-lg sm:text-xl text-nordic-900 leading-relaxed">
          "{{ currentExercise.sentence_given }}"
        </p>
      </div>

      <!-- Keyword Chip (Quiet, elegant framing) -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 rounded-xl bg-nordic-50 border border-nordic-200/80">
        <div class="flex items-center gap-3">
          <span class="text-xs font-semibold text-nordic-500">GIVEN WORD:</span>
          <span class="px-3 py-1 rounded-md bg-white border border-nordic-200 font-mono text-sm font-bold tracking-wider text-cobalt">
            {{ currentExercise.keyword }}
          </span>
        </div>
        <span class="text-[11px] text-nordic-400 tracking-wide">
          DO NOT CHANGE THE GIVEN WORD
        </span>
      </div>

      <!-- Second Sentence with Integrated Writing Affordance & Well-Fit Gap -->
      <div class="space-y-2">
        <label class="text-[11px] font-semibold tracking-wider uppercase text-nordic-400 block">
          Second Sentence Transformation
        </label>

        <div class="p-4 sm:p-5 rounded-xl bg-nordic-50 border border-nordic-200 leading-relaxed text-base sm:text-lg text-nordic-900 font-medium flex flex-wrap items-baseline gap-y-2">
          <span v-if="sentenceParts.before" class="mr-2">{{ sentenceParts.before }}</span>
          
          <input
            ref="inputRef"
            v-model="userAnswer"
            :disabled="result !== null"
            @keydown="handleKeydown"
            type="text"
            placeholder="type 2 to 5 words..."
            class="px-3.5 py-1.5 my-1 mx-2 rounded-lg border border-nordic-300 bg-white text-nordic-900 font-mono text-sm sm:text-base focus:border-cobalt focus:ring-1 focus:ring-cobalt focus:outline-none transition min-w-[220px] sm:min-w-[280px]"
            autocapitalize="off"
            spellcheck="false"
          />

          <span v-if="sentenceParts.after" class="ml-2">{{ sentenceParts.after }}</span>
        </div>

        <!-- Constraint Ledger & Clear action -->
        <div class="flex items-center justify-between text-xs px-1 pt-1 font-mono text-nordic-500">
          <div class="flex items-center gap-2">
            <span
              :class="[
                'px-1.5 py-0.5 rounded text-[11px] font-bold',
                wordCount === 0
                  ? 'bg-nordic-100 text-nordic-500'
                  : isWordCountValid
                  ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                  : 'bg-rose-50 text-rose-700 border border-rose-200'
              ]"
            >
              {{ wordCount }} {{ wordCount === 1 ? 'WORD' : 'WORDS' }}
            </span>
            <span class="text-nordic-400 hidden sm:inline">
              (Permitted: 2 to 5 words, including {{ currentExercise.keyword }})
            </span>
          </div>

          <button
            v-if="userAnswer && !result"
            @click="userAnswer = ''; inputRef?.focus()"
            class="text-nordic-400 hover:text-nordic-700 underline cursor-pointer"
          >
            Clear (Esc)
          </button>
        </div>
      </div>

      <!-- Action Row -->
      <div class="flex items-center justify-end gap-3 pt-2 border-t border-nordic-100">
        <button
          v-if="!result"
          @click="handleCheck"
          :disabled="!userAnswer.trim() || isEvaluating"
          class="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-xs sm:text-sm shadow-xs transition disabled:opacity-40"
        >
          <span>Check Answer</span>
          <CornerDownLeft class="w-3.5 h-3.5 opacity-60" />
        </button>

        <button
          v-else
          @click="loadNextExercise"
          class="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-xs sm:text-sm shadow-xs transition"
        >
          <span>Next Exercise</span>
          <ArrowRight class="w-4 h-4" />
        </button>
      </div>

      <!-- Feedback Section (Clean Swiss Architecture) -->
      <div v-if="result" class="space-y-4 pt-4 border-t border-nordic-100 animate-fade-in">
        
        <!-- Status Banner -->
        <div
          :class="[
            'p-4 rounded-xl border flex items-center justify-between',
            result.is_exact
              ? 'bg-emerald-50/70 border-emerald-200 text-emerald-900'
              : 'bg-rose-50/70 border-rose-200 text-rose-900'
          ]"
        >
          <div class="flex items-center gap-3">
            <span
              :class="[
                'w-7 h-7 rounded-full flex items-center justify-center text-white shrink-0',
                result.is_exact ? 'bg-emerald-600' : 'bg-rose-600'
              ]"
            >
              <Check v-if="result.is_exact" class="w-4 h-4" />
              <X v-else class="w-4 h-4" />
            </span>
            <div>
              <p class="font-heading font-bold text-sm sm:text-base">
                {{ result.is_exact ? 'Transformation Verified' : 'Incorrect Match' }}
              </p>
              <p class="text-xs opacity-80 mt-0.5">
                {{ result.feedback }}
              </p>
            </div>
          </div>

          <div class="text-right">
            <span class="font-mono text-base sm:text-lg font-bold">
              {{ result.score }} / 2
            </span>
            <span class="text-[10px] tracking-wider uppercase block opacity-70">
              Marks
            </span>
          </div>
        </div>

        <!-- Official Key Details -->
        <div class="p-4 rounded-xl bg-nordic-50 border border-nordic-200 space-y-2">
          <span class="text-[11px] font-semibold tracking-wider uppercase text-nordic-400 block">
            Official Cambridge Key:
          </span>
          <p class="font-mono font-bold text-base text-nordic-900">
            {{ result.correct_answer }}
          </p>

          <div v-if="result.acceptable_answers && result.acceptable_answers.length > 1" class="pt-1">
            <span class="text-[11px] text-nordic-500">Also accepted:</span>
            <div class="flex flex-wrap gap-1.5 mt-1">
              <span
                v-for="(acc, i) in result.acceptable_answers"
                :key="i"
                class="px-2 py-0.5 rounded font-mono text-xs bg-white border border-nordic-200 text-nordic-700"
              >
                {{ acc }}
              </span>
            </div>
          </div>
        </div>

        <!-- Grammatical Explanation -->
        <div v-if="result.explanation" class="p-4 rounded-xl bg-nordic-50/60 border border-nordic-200/60 text-xs sm:text-sm text-nordic-700 leading-relaxed">
          <strong class="font-semibold text-nordic-900 block mb-0.5">Grammar Note:</strong>
          {{ result.explanation }}
        </div>

        <!-- Suggest Variant Action -->
        <div v-if="!result.is_exact" class="pt-1">
          <button
            @click="openSuggestModal"
            class="text-xs text-nordic-500 hover:text-nordic-800 flex items-center gap-1.5 transition underline cursor-pointer"
          >
            <MessageSquarePlus class="w-3.5 h-3.5" />
            <span>Suggest your answer as an alternative valid variant</span>
          </button>
        </div>

      </div>

    </div>

    <!-- Suggestion Modal -->
    <div v-if="isSuggestOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-nordic-900/30 backdrop-blur-xs animate-fade-in">
      <div class="bg-white rounded-2xl border border-nordic-200 w-full max-w-md p-6 shadow-xl space-y-4">
        <h3 class="font-heading font-bold text-base text-nordic-900">
          Suggest Alternative Variant
        </h3>
        <p class="text-xs text-nordic-500 leading-relaxed">
          If your wording is grammatically correct and satisfies Cambridge rules, submit it for teacher review. Once approved, it will be added to the official answer key.
        </p>

        <form @submit.prevent="submitSuggestion" class="space-y-4">
          <div>
            <label class="text-[11px] font-semibold text-nordic-400 uppercase tracking-wider block mb-1">
              Your Suggested Answer
            </label>
            <input
              v-model="suggestText"
              type="text"
              required
              class="w-full px-3 py-2 rounded-lg border border-nordic-300 bg-white text-nordic-900 font-mono text-sm focus:outline-none focus:border-cobalt"
            />
          </div>

          <div v-if="suggestFeedback" class="text-xs font-semibold text-emerald-600">
            {{ suggestFeedback }}
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button
              type="button"
              @click="isSuggestOpen = false"
              class="px-4 py-2 rounded-lg text-xs font-semibold text-nordic-500 hover:text-nordic-900"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!suggestText.trim() || isSubmittingSuggest"
              class="px-4 py-2 rounded-lg bg-nordic-900 text-white text-xs font-semibold hover:bg-cobalt transition"
            >
              Submit to Teacher
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>
