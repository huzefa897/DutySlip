<template>
  <div
    v-if="visible"
    class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
    @click.self="cancel"
  >
    <div class="bg-gray-900 border border-gray-800 rounded-lg w-full max-w-sm">

      <!-- Header -->
      <div class="px-6 py-4 border-b border-gray-800">
        <h3 class="text-sm font-mono font-bold text-white">{{ title }}</h3>
      </div>

      <!-- Body -->
      <div class="px-6 py-4">
        <p class="text-sm text-gray-400">{{ message }}</p>
      </div>

      <!-- Actions -->
      <div class="px-6 py-4 border-t border-gray-800 flex justify-end gap-3">
        <button
          @click="cancel"
          class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors"
        >
          Cancel
        </button>
        <button
          @click="confirm"
          class="text-sm font-bold px-5 py-2 rounded transition-colors"
          :class="destructive
            ? 'bg-red-600 hover:bg-red-500 text-white'
            : 'bg-amber-400 hover:bg-amber-300 text-gray-950'"
        >
          {{ confirmLabel }}
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  visible:      { type: Boolean, default: false },
  title:        { type: String,  default: 'Are you sure?' },
  message:      { type: String,  default: 'This action cannot be undone.' },
  confirmLabel: { type: String,  default: 'Confirm' },
  destructive:  { type: Boolean, default: true },
})

const emit = defineEmits(['confirm', 'cancel'])

function confirm() { emit('confirm') }
function cancel()  { emit('cancel') }
</script>