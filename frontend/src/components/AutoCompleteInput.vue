<template>
  <div class="relative">
    <input
      v-model="inputValue"
      type="text"
      :required="required"
      :readonly="readonly"
      :placeholder="placeholder"
      class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 read-only:opacity-60"
      :class="inputClass"
      autocomplete="off"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
      @keydown.down.prevent="moveDown"
      @keydown.up.prevent="moveUp"
      @keydown.enter.prevent="selectHighlighted"
      @keydown.escape="close"
    >

    <!-- Suggestions dropdown -->
    <ul
      v-if="showSuggestions && filtered.length > 0"
      class="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded shadow-lg max-h-48 overflow-y-auto"
    >
      <li
        v-for="(suggestion, index) in filtered"
        :key="suggestion"
        class="px-3 py-2 text-sm text-gray-300 cursor-pointer transition-colors"
        :class="index === highlighted ? 'bg-amber-400/20 text-white' : 'hover:bg-gray-700'"
        @mousedown.prevent="select(suggestion)"
      >
        {{ suggestion }}
      </li>
    </ul>

    <!-- No suggestions hint -->
    <p
      v-if="showSuggestions && inputValue && filtered.length === 0 && suggestions.length > 0"
      class="absolute z-50 w-full mt-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-xs text-gray-600 font-mono"
    >
      No matches — new party name will be created
    </p>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: String,
  suggestions: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' },
  required: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  inputClass: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const inputValue = ref(props.modelValue || '')
const showSuggestions = ref(false)
const highlighted = ref(-1)

// Keep in sync if parent changes modelValue
watch(() => props.modelValue, val => {
  inputValue.value = val || ''
})

// Emit changes up
watch(inputValue, val => {
  emit('update:modelValue', val)
})

const filtered = computed(() => {
  if (!inputValue.value) return props.suggestions
  return props.suggestions.filter(s =>
    s.toLowerCase().includes(inputValue.value.toLowerCase())
  )
})

function onInput() {
  showSuggestions.value = true
  highlighted.value = -1
}

function onFocus() {
  if (props.suggestions.length > 0) showSuggestions.value = true
}

function onBlur() {
  setTimeout(() => {
    showSuggestions.value = false
    highlighted.value = -1
  }, 150)
}

function select(value) {
  inputValue.value = value
  emit('update:modelValue', value)
  showSuggestions.value = false
  highlighted.value = -1
}

function selectHighlighted() {
  if (highlighted.value >= 0 && filtered.value[highlighted.value]) {
    select(filtered.value[highlighted.value])
  }
}

function moveDown() {
  if (highlighted.value < filtered.value.length - 1) highlighted.value++
}

function moveUp() {
  if (highlighted.value > 0) highlighted.value--
}

function close() {
  showSuggestions.value = false
  highlighted.value = -1
}
</script>