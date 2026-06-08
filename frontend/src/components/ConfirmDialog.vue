<template>
  <Teleport to="body">
    <div
      v-if="visible"
      class="modal-overlay"
      @click.self="cancel"
    >
      <div class="modal-card modal-card--sm">
        <div class="modal-header">
          <h3 class="modal-title">
            {{ title }}
          </h3>
        </div>

        <div class="modal-body">
          <p class="page-header__subtitle">
            {{ message }}
          </p>
        </div>

        <div class="modal-footer">
          <button
            class="btn-cancel px-2 py-2"
            @click="cancel"
          >
            Cancel
          </button>
          <button
            class="px-5 py-2.5"
            :class="destructive
              ? 'btn-danger'
              : 'btn-primary'"
            @click="confirm"
          >
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
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
