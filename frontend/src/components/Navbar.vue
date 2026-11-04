<script setup>
import { Shield, User } from 'lucide-vue-next'

const props = defineProps({
  currentMode: { type: String, required: true },
  studentName: { type: String, default: '' }
})

const emit = defineEmits(['set-mode', 'edit-name', 'open-admin'])
</script>

<template>
  <header class="w-full bg-white/95 border-b border-nordic-200 sticky top-0 z-40 backdrop-blur-sm">
    <div class="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
      
      <!-- Brand & Tag -->
      <div class="flex items-center gap-3 cursor-pointer" @click="emit('set-mode', 'practice')">
        <span class="font-heading font-bold text-base sm:text-lg tracking-tight text-nordic-900">
          B2 First Rewrite
        </span>
        <span class="hidden sm:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider uppercase bg-nordic-100 text-nordic-600 border border-nordic-200">
          Part 4 · Use of English
        </span>
      </div>

      <!-- Segmented Control Tray (Center) -->
      <nav class="flex items-center p-1 rounded-xl bg-nordic-100 border border-nordic-200 text-xs font-semibold">
        <button
          @click="emit('set-mode', 'practice')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition-all',
            currentMode === 'practice'
              ? 'bg-white text-nordic-900 shadow-xs font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          Practice
        </button>
        <button
          @click="emit('set-mode', 'exam')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition-all',
            currentMode === 'exam'
              ? 'bg-white text-nordic-900 shadow-xs font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          Timed Exam
        </button>
        <button
          @click="emit('set-mode', 'history')"
          :class="[
            'px-3.5 py-1.5 rounded-lg transition-all',
            currentMode === 'history'
              ? 'bg-white text-nordic-900 shadow-xs font-bold'
              : 'text-nordic-500 hover:text-nordic-900'
          ]"
        >
          History
        </button>
      </nav>

      <!-- Right Trailing Actions -->
      <div class="flex items-center gap-2">
        <!-- Student Name Pill -->
        <button
          @click="emit('edit-name')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-nordic-200 bg-white text-nordic-700 text-xs font-medium hover:border-nordic-300 transition"
          title="Click to edit your name"
        >
          <User class="w-3.5 h-3.5 text-cobalt" />
          <span class="max-w-[100px] truncate">{{ studentName || 'Name' }}</span>
        </button>

        <!-- Admin Access Button -->
        <button
          @click="emit('open-admin')"
          class="p-2 rounded-lg border border-nordic-200 bg-white text-nordic-400 hover:text-nordic-700 transition"
          title="Teacher / Admin Portal"
        >
          <Shield class="w-4 h-4" />
        </button>
      </div>

    </div>
  </header>
</template>

