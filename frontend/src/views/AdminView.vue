<script setup>
import { ref } from 'vue'
import { Shield, Check, X, Search, Plus } from 'lucide-vue-next'

const password = ref('')
const isAuthenticated = ref(false)
const loginError = ref('')
const activeTab = ref('suggestions') // 'suggestions' | 'analytics' | 'exercises'

const suggestions = ref([])
const isSuggestionsLoading = ref(false)

const analytics = ref(null)

const exercises = ref([])
const exercisesTotal = ref(0)
const searchQuery = ref('')
const isSearching = ref(false)

// Edit Exercise Modal
const isEditModalOpen = ref(false)
const editingEx = ref(null)
const editForm = ref({
  sentence_given: '',
  keyword: '',
  incomplete_phrase: '',
  correct_answer: '',
  acceptable_answers_str: '',
  explanation: '',
  is_locked: false,
  verified: false
})

// Create Exercise Modal
const isCreateModalOpen = ref(false)
const createForm = ref({
  book: 'libro_clase',
  page_identifier: 'Class Session',
  exercise_number: 1,
  sentence_given: '',
  keyword: '',
  incomplete_phrase: '',
  correct_answer: '',
  acceptable_answers_str: '',
  explanation: ''
})

async function handleLogin() {
  loginError.value = ''
  try {
    const res = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ password: password.value })
    })

    if (!res.ok) throw new Error('Incorrect password')
    isAuthenticated.value = true
    loadActiveTabData()
  } catch (e) {
    loginError.value = 'Incorrect password. Check ADMIN_PASSWORD in .env.'
  }
}

function getAuthHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-Admin-Password': password.value
  }
}

async function loadSuggestions() {
  isSuggestionsLoading.value = true
  try {
    const res = await fetch('/api/admin/suggestions?status=all', {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      suggestions.value = await res.json()
    }
  } catch (e) {
    console.error('Error loading suggestions', e)
  } finally {
    isSuggestionsLoading.value = false
  }
}

async function approveSuggestion(id) {
  try {
    const res = await fetch(`/api/admin/suggestions/${id}/approve`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    if (res.ok) {
      loadSuggestions()
    }
  } catch (e) {
    console.error('Error approving', e)
  }
}

async function rejectSuggestion(id) {
  try {
    const res = await fetch(`/api/admin/suggestions/${id}/reject`, {
      method: 'POST',
      headers: getAuthHeaders()
    })
    if (res.ok) {
      loadSuggestions()
    }
  } catch (e) {
    console.error('Error rejecting', e)
  }
}

async function loadAnalytics() {
  try {
    const res = await fetch('/api/admin/analytics', {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      analytics.value = await res.json()
    }
  } catch (e) {
    console.error('Error loading analytics', e)
  }
}

async function searchExercises() {
  isSearching.value = true
  try {
    const q = encodeURIComponent(searchQuery.value.trim())
    const res = await fetch(`/api/admin/exercises?search=${q}&limit=50`, {
      headers: getAuthHeaders()
    })
    if (res.ok) {
      const data = await res.json()
      exercises.value = data.items || []
      exercisesTotal.value = data.total || 0
    }
  } catch (e) {
    console.error('Error searching exercises', e)
  } finally {
    isSearching.value = false
  }
}

function openEditModal(ex) {
  editingEx.value = ex
  editForm.value = {
    sentence_given: ex.sentence_given,
    keyword: ex.keyword,
    incomplete_phrase: ex.incomplete_phrase,
    correct_answer: ex.correct_answer,
    acceptable_answers_str: (ex.acceptable_answers || []).join('\n'),
    explanation: ex.explanation || '',
    is_locked: ex.is_locked,
    verified: ex.verified
  }
  isEditModalOpen.value = true
}

async function saveEditExercise() {
  if (!editingEx.value) return
  const variants = editForm.value.acceptable_answers_str
    .split('\n')
    .map(v => v.trim())
    .filter(v => v.length > 0)

  try {
    const res = await fetch(`/api/admin/exercises/${editingEx.value.id}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        sentence_given: editForm.value.sentence_given,
        keyword: editForm.value.keyword,
        incomplete_phrase: editForm.value.incomplete_phrase,
        correct_answer: editForm.value.correct_answer,
        acceptable_answers: variants,
        explanation: editForm.value.explanation || null,
        is_locked: editForm.value.is_locked,
        verified: editForm.value.verified
      })
    })

    if (res.ok) {
      isEditModalOpen.value = false
      searchExercises()
    }
  } catch (e) {
    console.error('Error saving exercise', e)
  }
}

async function handleCreateExercise() {
  const variants = createForm.value.acceptable_answers_str
    .split('\n')
    .map(v => v.trim())
    .filter(v => v.length > 0)

  try {
    const res = await fetch('/api/admin/exercises', {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        book: createForm.value.book,
        page_identifier: createForm.value.page_identifier,
        exercise_number: createForm.value.exercise_number,
        sentence_given: createForm.value.sentence_given,
        keyword: createForm.value.keyword,
        incomplete_phrase: createForm.value.incomplete_phrase,
        correct_answer: createForm.value.correct_answer,
        acceptable_answers: variants,
        explanation: createForm.value.explanation || null
      })
    })

    if (res.ok) {
      isCreateModalOpen.value = false
      createForm.value = {
        book: 'libro_clase',
        page_identifier: 'Class Session',
        exercise_number: 1,
        sentence_given: '',
        keyword: '',
        incomplete_phrase: '',
        correct_answer: '',
        acceptable_answers_str: '',
        explanation: ''
      }
      searchExercises()
    }
  } catch (e) {
    console.error('Error creating exercise', e)
  }
}

function loadActiveTabData() {
  if (!isAuthenticated.value) return
  if (activeTab.value === 'suggestions') loadSuggestions()
  else if (activeTab.value === 'analytics') loadAnalytics()
  else if (activeTab.value === 'exercises') searchExercises()
}

function setTab(tab) {
  activeTab.value = tab
  loadActiveTabData()
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-4 py-8 sm:py-12">
    
    <!-- Login view if not unlocked -->
    <div v-if="!isAuthenticated" class="max-w-sm mx-auto bg-white rounded-2xl border border-nordic-200 p-8 text-center space-y-4">
      <div class="w-10 h-10 rounded-full bg-nordic-100 flex items-center justify-center mx-auto text-nordic-600">
        <Shield class="w-5 h-5" />
      </div>
      <div>
        <h2 class="font-heading font-bold text-lg text-nordic-900">
          Teacher Portal
        </h2>
        <p class="text-xs text-nordic-500 mt-1">
          Enter master password to manage content and student suggestions.
        </p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-3 pt-2">
        <input
          v-model="password"
          type="password"
          required
          placeholder="Password..."
          class="w-full px-3 py-2 text-xs rounded-lg border border-nordic-300 bg-white text-nordic-900 focus:outline-none focus:border-cobalt"
          autofocus
        />
        <div v-if="loginError" class="text-xs text-rose-600 font-medium">
          {{ loginError }}
        </div>
        <button
          type="submit"
          class="w-full py-2 rounded-lg bg-nordic-900 text-white text-xs font-semibold hover:bg-cobalt transition"
        >
          Unlock
        </button>
      </form>
    </div>

    <!-- Authenticated Portal -->
    <div v-else class="space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-heading font-bold text-xl text-nordic-900">
            Teacher Administration
          </h2>
          <p class="text-xs text-nordic-500 mt-0.5">
            Curation, student-suggested variants, and class progress.
          </p>
        </div>

        <button
          @click="isAuthenticated = false"
          class="px-3 py-1.5 rounded-lg border border-nordic-200 text-xs font-semibold text-nordic-500 hover:text-nordic-900 transition"
        >
          Lock
        </button>
      </div>

      <!-- Segmented Tabs -->
      <div class="flex items-center gap-1 border-b border-nordic-200 pb-2 text-xs font-semibold">
        <button
          @click="setTab('suggestions')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition',
            activeTab === 'suggestions'
              ? 'bg-nordic-900 text-white font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          Suggestions
          <span v-if="suggestions.filter(s => s.status === 'pending').length" class="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-rose-500 text-white">
            {{ suggestions.filter(s => s.status === 'pending').length }}
          </span>
        </button>

        <button
          @click="setTab('analytics')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition',
            activeTab === 'analytics'
              ? 'bg-nordic-900 text-white font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          Class Progress
        </button>

        <button
          @click="setTab('exercises')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition',
            activeTab === 'exercises'
              ? 'bg-nordic-900 text-white font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          Exercise Database
        </button>
      </div>

      <!-- Tab: Suggestions -->
      <div v-if="activeTab === 'suggestions'" class="space-y-3">
        <div v-if="isSuggestionsLoading" class="text-xs text-nordic-400 py-6 text-center">
          Loading student suggestions...
        </div>
        <div v-else-if="suggestions.length === 0" class="text-xs text-nordic-400 py-10 text-center bg-white rounded-xl border border-nordic-200">
          No suggestions submitted yet.
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="s in suggestions"
            :key="s.id"
            class="bg-white rounded-xl border border-nordic-200 p-4 space-y-3"
          >
            <div class="flex items-center justify-between text-xs">
              <div>
                <span class="font-bold text-nordic-900">{{ s.student_name }}</span>
                <span class="text-nordic-400 ml-1.5">for Exercise #{{ s.exercise_id }}</span>
              </div>
              <span class="font-mono text-[10px] uppercase px-2 py-0.5 rounded border border-nordic-200 text-nordic-500">
                {{ s.status }}
              </span>
            </div>

            <div v-if="s.exercise" class="text-xs text-nordic-600 p-3 rounded-lg bg-nordic-50 border border-nordic-200/60 space-y-1">
              <p>Original: "{{ s.exercise.sentence_given }}"</p>
              <p>Key: <span class="font-mono font-bold text-emerald-600">{{ s.exercise.correct_answer }}</span></p>
            </div>

            <div class="flex items-center justify-between pt-1">
              <div>
                <span class="text-[10px] text-nordic-400 uppercase tracking-wider block">Suggested Variant</span>
                <span class="font-mono font-bold text-sm text-nordic-900">"{{ s.suggested_answer }}"</span>
              </div>

              <div v-if="s.status === 'pending'" class="flex gap-2">
                <button
                  @click="approveSuggestion(s.id)"
                  class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1"
                >
                  <Check class="w-3.5 h-3.5" />
                  Approve (Add Key)
                </button>
                <button
                  @click="rejectSuggestion(s.id)"
                  class="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold flex items-center gap-1"
                >
                  <X class="w-3.5 h-3.5" />
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab: Class Progress -->
      <div v-if="activeTab === 'analytics'" class="space-y-4">
        <div v-if="!analytics" class="text-xs text-nordic-400 py-6 text-center">
          Loading statistics...
        </div>
        <div v-else class="space-y-4">
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div class="p-4 rounded-xl bg-white border border-nordic-200">
              <span class="text-[10px] uppercase text-nordic-400 font-semibold block">Total Tests</span>
              <span class="font-mono font-bold text-2xl text-nordic-900 mt-1 block">
                {{ analytics.total_attempts }}
              </span>
            </div>
            <div class="p-4 rounded-xl bg-white border border-nordic-200">
              <span class="text-[10px] uppercase text-nordic-400 font-semibold block">Class Average</span>
              <span class="font-mono font-bold text-2xl text-cobalt mt-1 block">
                {{ analytics.avg_score_out_of_12 }} <span class="text-xs font-normal text-nordic-400">/ 12</span>
              </span>
            </div>
            <div class="p-4 rounded-xl bg-white border border-nordic-200">
              <span class="text-[10px] uppercase text-nordic-400 font-semibold block">Pending Variants</span>
              <span class="font-mono font-bold text-2xl text-amber-500 mt-1 block">
                {{ analytics.pending_suggestions_count }}
              </span>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-nordic-200 overflow-hidden">
            <div class="px-4 py-3 border-b border-nordic-200 font-heading font-semibold text-xs text-nordic-900">
              Students Roster
            </div>
            <div v-if="analytics.students.length === 0" class="p-6 text-center text-xs text-nordic-400">
              No students recorded yet.
            </div>
            <table v-else class="w-full text-left text-xs font-mono">
              <thead class="bg-nordic-50 text-nordic-400 uppercase text-[10px]">
                <tr>
                  <th class="p-3 pl-4">Name</th>
                  <th class="p-3">Tests</th>
                  <th class="p-3">Avg Mark</th>
                  <th class="p-3 pr-4">Last Active</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-nordic-100">
                <tr v-for="st in analytics.students" :key="st.name">
                  <td class="p-3 pl-4 font-bold text-nordic-900">{{ st.name }}</td>
                  <td class="p-3">{{ st.tests_taken }}</td>
                  <td class="p-3 font-bold text-cobalt">{{ st.avg_score }} / 12</td>
                  <td class="p-3 pr-4 text-nordic-400">{{ st.last_active ? new Date(st.last_active).toLocaleDateString() : '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Tab: Exercises Database -->
      <div v-if="activeTab === 'exercises'" class="space-y-4">
        <div class="flex items-center justify-between gap-3">
          <div class="relative flex-1">
            <Search class="w-3.5 h-3.5 absolute left-3 top-2.5 text-nordic-400" />
            <input
              v-model="searchQuery"
              @keydown.enter="searchExercises"
              type="text"
              placeholder="Search keyword or sentence..."
              class="w-full pl-9 pr-3 py-2 text-xs rounded-lg border border-nordic-300 bg-white focus:outline-none focus:border-cobalt"
            />
          </div>
          <button
            @click="searchExercises"
            class="px-3 py-2 rounded-lg bg-nordic-100 text-xs font-semibold text-nordic-700 hover:bg-nordic-200"
          >
            Search
          </button>
          <button
            @click="isCreateModalOpen = true"
            class="px-3 py-2 rounded-lg bg-nordic-900 text-white text-xs font-semibold hover:bg-cobalt transition"
          >
            + Add Exercise
          </button>
        </div>

        <div class="text-[11px] font-mono text-nordic-400 px-1">
          Showing {{ exercises.length }} of {{ exercisesTotal }} items
        </div>

        <div class="space-y-2">
          <div
            v-for="ex in exercises"
            :key="ex.id"
            class="bg-white rounded-xl border border-nordic-200 p-3.5 space-y-1.5 text-xs"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="font-mono text-nordic-400">#{{ ex.id }}</span>
                <span class="font-mono font-bold uppercase text-cobalt">{{ ex.keyword }}</span>
              </div>
              <button @click="openEditModal(ex)" class="text-xs font-semibold text-cobalt hover:underline">
                Edit
              </button>
            </div>
            <p class="text-nordic-800">"{{ ex.sentence_given }}"</p>
            <p class="font-mono font-semibold text-emerald-600">Key: {{ ex.correct_answer }}</p>
          </div>
        </div>
      </div>

    </div>

    <!-- Edit Modal -->
    <div v-if="isEditModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-nordic-900/30 backdrop-blur-xs animate-fade-in">
      <div class="bg-white rounded-2xl border border-nordic-200 w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto space-y-4 text-xs">
        <h3 class="font-heading font-bold text-base text-nordic-900">
          Edit Exercise #{{ editingEx?.id }}
        </h3>

        <form @submit.prevent="saveEditExercise" class="space-y-3">
          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Sentence Given</label>
            <input v-model="editForm.sentence_given" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white" />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="font-semibold text-nordic-500 block mb-1">Keyword</label>
              <input v-model="editForm.keyword" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono uppercase" />
            </div>
            <div>
              <label class="font-semibold text-nordic-500 block mb-1">Incomplete Phrase</label>
              <input v-model="editForm.incomplete_phrase" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white" />
            </div>
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Primary Correct Answer</label>
            <input v-model="editForm.correct_answer" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono" />
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Accepted Variants (one per line)</label>
            <textarea v-model="editForm.acceptable_answers_str" rows="3" class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono"></textarea>
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Explanation</label>
            <textarea v-model="editForm.explanation" rows="2" class="w-full p-2 rounded-lg border border-nordic-300 bg-white"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="isEditModalOpen = false" class="px-4 py-2 text-nordic-500 hover:text-nordic-900">
              Cancel
            </button>
            <button type="submit" class="px-4 py-2 rounded-lg bg-nordic-900 text-white font-semibold hover:bg-cobalt transition">
              Save
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="isCreateModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-nordic-900/30 backdrop-blur-xs animate-fade-in">
      <div class="bg-white rounded-2xl border border-nordic-200 w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto space-y-4 text-xs">
        <h3 class="font-heading font-bold text-base text-nordic-900">
          Add New Cambridge Exercise
        </h3>

        <form @submit.prevent="handleCreateExercise" class="space-y-3">
          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Sentence Given</label>
            <input v-model="createForm.sentence_given" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white" />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="font-semibold text-nordic-500 block mb-1">Keyword</label>
              <input v-model="createForm.keyword" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono uppercase" />
            </div>
            <div>
              <label class="font-semibold text-nordic-500 block mb-1">Incomplete Phrase (use '...')</label>
              <input v-model="createForm.incomplete_phrase" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white" />
            </div>
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Primary Correct Answer</label>
            <input v-model="createForm.correct_answer" required class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono" />
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Accepted Variants (one per line)</label>
            <textarea v-model="createForm.acceptable_answers_str" rows="3" class="w-full p-2 rounded-lg border border-nordic-300 bg-white font-mono"></textarea>
          </div>

          <div>
            <label class="font-semibold text-nordic-500 block mb-1">Explanation</label>
            <textarea v-model="createForm.explanation" rows="2" class="w-full p-2 rounded-lg border border-nordic-300 bg-white"></textarea>
          </div>

          <div class="flex justify-end gap-2 pt-2">
            <button type="button" @click="isCreateModalOpen = false" class="px-4 py-2 text-nordic-500 hover:text-nordic-900">
              Cancel
            </button>
            <button type="submit" class="px-4 py-2 rounded-lg bg-nordic-900 text-white font-semibold hover:bg-cobalt transition">
              Create Exercise
            </button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>
