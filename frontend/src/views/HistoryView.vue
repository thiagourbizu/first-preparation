<script setup>
import { ref, onMounted } from 'vue'
import { History } from 'lucide-vue-next'

const props = defineProps({
  studentDeviceId: { type: String, required: true },
  studentName: { type: String, default: 'Anonymous' }
})

const emit = defineEmits(['start-exam'])

const history = ref([])
const isLoading = ref(true)

async function fetchHistory() {
  isLoading.value = true
  try {
    const res = await fetch(`/api/exam/history?student_device_id=${encodeURIComponent(props.studentDeviceId)}`)
    if (res.ok) {
      history.value = await res.json()
    }
  } catch (e) {
    console.error('Error fetching history', e)
  } finally {
    isLoading.value = false
  }
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8 sm:py-12 space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h2 class="font-heading font-bold text-xl text-nordic-900">
          Exam History
        </h2>
        <p class="text-xs text-nordic-500 mt-0.5">
          Past Cambridge B2 mock tests for <span class="font-medium text-nordic-800">{{ studentName || 'you' }}</span> on this device.
        </p>
      </div>

      <button
        @click="emit('start-exam')"
        class="px-4 py-2 rounded-xl bg-nordic-900 hover:bg-cobalt text-white font-semibold text-xs transition"
      >
        Take New Exam
      </button>
    </div>

    <div v-if="isLoading" class="text-center py-12 text-xs text-nordic-400">
      Loading past tests...
    </div>

    <div
      v-else-if="history.length === 0"
      class="bg-white rounded-2xl border border-nordic-200 p-10 text-center space-y-4"
    >
      <div class="w-10 h-10 rounded-full bg-nordic-100 flex items-center justify-center mx-auto text-nordic-400">
        <History class="w-5 h-5" />
      </div>
      <div>
        <h3 class="font-heading font-bold text-base text-nordic-800">
          No Completed Exams Yet
        </h3>
        <p class="text-xs text-nordic-500 mt-1 max-w-sm mx-auto">
          Take a 6-task timed mock exam to test your skills and view your progress here.
        </p>
      </div>
      <button
        @click="emit('start-exam')"
        class="px-5 py-2.5 rounded-xl bg-nordic-900 hover:bg-cobalt text-white text-xs font-semibold shadow-xs"
      >
        Start Mock Exam
      </button>
    </div>

    <div v-else class="space-y-2.5">
      <div
        v-for="att in history"
        :key="att.id"
        class="bg-white rounded-xl border border-nordic-200 p-4 sm:p-5 flex items-center justify-between gap-4"
      >
        <div class="flex items-center gap-4">
          <div
            :class="[
              'w-11 h-11 rounded-lg flex items-center justify-center font-mono font-bold text-sm',
              att.total_score >= 8
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                : 'bg-rose-50 text-rose-700 border border-rose-200'
            ]"
          >
            {{ att.total_score }}/12
          </div>

          <div>
            <div class="flex items-center gap-2">
              <span class="font-heading font-bold text-sm text-nordic-900">
                {{ att.total_score >= 8 ? 'Passed' : 'Needs Review' }}
              </span>
              <span class="text-xs font-mono text-nordic-400">({{ att.percentage }}%)</span>
            </div>

            <div class="flex items-center gap-2.5 text-xs text-nordic-400 font-mono mt-1">
              <span>{{ formatDate(att.submitted_at) }}</span>
              <span>·</span>
              <span>{{ Math.floor(att.time_taken_seconds / 60) }}m {{ att.time_taken_seconds % 60 }}s</span>
            </div>
          </div>
        </div>

        <span
          :class="[
            'px-2.5 py-0.5 rounded text-[11px] font-mono font-bold tracking-wider uppercase',
            att.total_score >= 8
              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
              : 'bg-rose-50 text-rose-700 border border-rose-200'
          ]"
        >
          {{ att.total_score >= 8 ? 'PASS' : 'FAIL' }}
        </span>
      </div>
    </div>
  </div>
</template>
