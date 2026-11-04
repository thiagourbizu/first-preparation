<script setup>
import { ref } from 'vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  initialName: { type: String, default: '' }
})

const emit = defineEmits(['save', 'close'])

const inputName = ref(props.initialName)

function handleSave() {
  const clean = inputName.value.trim()
  if (clean) {
    emit('save', clean)
  }
}
</script>

<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-nordic-900/30 backdrop-blur-xs animate-fade-in">
    <div class="bg-white rounded-2xl border border-nordic-200 w-full max-w-sm p-6 shadow-xl space-y-4">
      
      <div class="space-y-1">
        <h3 class="font-heading font-bold text-base text-nordic-900">
          Student Profile
        </h3>
        <p class="text-xs text-nordic-500 leading-relaxed">
          Enter your first name to track your mock exam results on this device.
        </p>
      </div>

      <form @submit.prevent="handleSave" class="space-y-4">
        <div>
          <label class="text-[11px] font-semibold text-nordic-400 uppercase tracking-wider block mb-1">
            Your Name
          </label>
          <input
            v-model="inputName"
            type="text"
            required
            placeholder="e.g. Lucas, Valen..."
            class="w-full px-3 py-2 text-xs rounded-lg border border-nordic-300 bg-white text-nordic-900 focus:outline-none focus:border-cobalt"
            autofocus
          />
        </div>

        <div class="flex justify-end gap-2 pt-1">
          <button
            type="button"
            @click="emit('close')"
            class="px-4 py-2 text-xs font-semibold text-nordic-500 hover:text-nordic-900"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!inputName.trim()"
            class="px-5 py-2 rounded-lg bg-nordic-900 text-white text-xs font-semibold hover:bg-cobalt transition disabled:opacity-40"
          >
            Save Name
          </button>
        </div>
      </form>

    </div>
  </div>
</template>
