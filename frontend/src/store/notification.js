import { ref } from 'vue'

const message = ref('')
const type = ref('') // 'success' | 'error'
let timer = null

export function notify(msg, notifType = 'success') {
  message.value = msg
  type.value = notifType
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    message.value = ''
    type.value = ''
  }, 4000)
}

export function clearNotification() {
  message.value = ''
  type.value = ''
}

export const notification = { message, type }