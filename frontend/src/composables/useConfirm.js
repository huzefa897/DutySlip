import { ref } from 'vue'

export function useConfirm() {
  const visible = ref(false)
  const title = ref('')
  const message = ref('')
  const confirmLabel = ref('Delete')
  const destructive = ref(true)
  let resolveFn = null

  function ask(options = {}) {
    title.value        = options.title        || 'Are you sure?'
    message.value      = options.message      || 'This action cannot be undone.'
    confirmLabel.value = options.confirmLabel || 'Delete'
    destructive.value  = options.destructive  !== false
    visible.value      = true

    return new Promise(resolve => {
      resolveFn = resolve
    })
  }

  function onConfirm() {
    visible.value = false
    resolveFn?.(true)
  }

  function onCancel() {
    visible.value = false
    resolveFn?.(false)
  }

  return { visible, title, message, confirmLabel, destructive, ask, onConfirm, onCancel }
}