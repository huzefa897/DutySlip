<template>
  <div
    ref="triggerRef"
    class="row-menu-trigger"
  >
    <button
      type="button"
      class="icon-btn"
      :aria-expanded="open"
      aria-label="Open row actions"
      @click.stop="toggleMenu"
    >
      ⋮
    </button>

    <Teleport to="body">
      <div
        v-if="open"
        class="row-menu__layer"
      >
        <div
          class="row-menu__backdrop"
          @click="closeMenu"
        />
        <div
          class="row-menu__dropdown"
          :style="menuStyle"
        >
          <button
            type="button"
            class="row-menu__item"
            @click="emitAction('edit')"
          >
            Edit
          </button>
          <button
            type="button"
            class="row-menu__item row-menu__item--danger"
            @click="emitAction('delete')"
          >
            Delete
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const emit = defineEmits(['edit', 'delete'])

const open = ref(false)
const triggerRef = ref(null)
const position = ref({ top: 0, left: 0 })

const menuStyle = computed(() => ({
  position: 'fixed',
  top: `${position.value.top}px`,
  left: `${position.value.left}px`,
}))

function updatePosition() {
  if (!triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()
  position.value = {
    top: rect.bottom + 8,
    left: rect.right - 144,
  }
}

function closeMenu() {
  open.value = false
}

function toggleMenu() {
  if (!open.value) updatePosition()
  open.value = !open.value
}

function emitAction(action) {
  closeMenu()
  emit(action)
}

function handleViewportChange() {
  if (!open.value) return
  updatePosition()
}

onMounted(() => {
  window.addEventListener('resize', handleViewportChange)
  window.addEventListener('scroll', handleViewportChange, true)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleViewportChange)
  window.removeEventListener('scroll', handleViewportChange, true)
})
</script>
