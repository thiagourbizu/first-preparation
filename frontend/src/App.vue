<script setup>
import { ref, onMounted } from 'vue'
import Navbar from './components/Navbar.vue'
import PracticeView from './views/PracticeView.vue'
import ExamView from './views/ExamView.vue'
import HistoryView from './views/HistoryView.vue'
import AdminView from './views/AdminView.vue'
import StudentNameModal from './components/StudentNameModal.vue'

import {
  getDeviceId,
  getStudentName,
  setStudentName
} from './services/storage'

const currentMode = ref('practice') // 'practice' | 'exam' | 'history' | 'admin'
const studentName = ref('')
const studentDeviceId = ref('')

const isNameModalOpen = ref(false)

function handleSaveName(newName) {
  setStudentName(newName)
  studentName.value = newName
  isNameModalOpen.value = false
}

onMounted(() => {
  studentDeviceId.value = getDeviceId()
  const savedName = getStudentName()
  studentName.value = savedName

  if (!savedName) {
    isNameModalOpen.value = true
  }
})
</script>

<template>
  <div class="min-h-screen flex flex-col bg-nordic-50 text-nordic-900">
    <!-- Clean Minimalist Header -->
    <Navbar
      :current-mode="currentMode"
      :student-name="studentName"
      @set-mode="currentMode = $event"
      @edit-name="isNameModalOpen = true"
      @open-admin="currentMode = 'admin'"
    />

    <!-- Main Workspace -->
    <main class="flex-1 pb-16">
      <Transition name="fade" mode="out-in">
        <PracticeView
          v-if="currentMode === 'practice'"
          :key="'practice'"
          :student-name="studentName"
          :student-device-id="studentDeviceId"
        />

        <ExamView
          v-else-if="currentMode === 'exam'"
          :key="'exam'"
          :student-name="studentName"
          :student-device-id="studentDeviceId"
          @view-history="currentMode = 'history'"
        />

        <HistoryView
          v-else-if="currentMode === 'history'"
          :key="'history'"
          :student-name="studentName"
          :student-device-id="studentDeviceId"
          @start-exam="currentMode = 'exam'"
        />

        <AdminView
          v-else-if="currentMode === 'admin'"
          :key="'admin'"
        />
      </Transition>
    </main>

    <!-- Student Name Modal -->
    <StudentNameModal
      :is-open="isNameModalOpen"
      :initial-name="studentName"
      @save="handleSaveName"
      @close="isNameModalOpen = false"
    />
  </div>
</template>
