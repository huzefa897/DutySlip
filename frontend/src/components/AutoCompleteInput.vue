<template>
  <div class="autocomplete-field">
    <input
      v-model="inputValue"
      type="text"
      :required="required"
      :readonly="readonly"
      :placeholder="placeholder"
      class="autocomplete-input"
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
      class="autocomplete-menu"
    >
      <li
        v-for="(suggestion, index) in filtered"
        :key="suggestion"
        class="autocomplete-menu__item"
        :class="index === highlighted ? 'bg-white/8 text-white' : 'hover:bg-white/5'"
        @mousedown.prevent="select(suggestion)"
      >
        {{ suggestion }}
      </li>
    </ul>

    <!-- No suggestions / add option -->
    <ul
      v-else-if="showSuggestions && inputValue && filtered.length === 0"
      class="autocomplete-menu"
    >
      <li
        v-if="allowAdd && inputValue.trim()"
        class="autocomplete-menu__item autocomplete-add"
        @mousedown.prevent="emit('add', inputValue.trim()); close()"
      >
        + Add "{{ inputValue }}"
      </li>
      <li
        v-else
        class="autocomplete-menu__item autocomplete-empty"
      >
        No matches
      </li>
    </ul>
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
  allowAdd: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'add'])

const inputValue = ref(props.modelValue || '')
const isFocused = ref(false)
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

watch(
  () => props.suggestions,
  (suggestions) => {
    if (!isFocused.value || props.readonly) return
    showSuggestions.value = suggestions.length > 0
    highlighted.value = -1
  }
)

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
  isFocused.value = true
  if (props.suggestions.length > 0) showSuggestions.value = true
}

function onBlur() {
  isFocused.value = false
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
