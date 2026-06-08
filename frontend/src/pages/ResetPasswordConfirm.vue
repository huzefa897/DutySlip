<template>
  <div class="auth-shell">
    <div class="auth-card">
      <h1 class="auth-title">
        Choose a new password
      </h1>

      <div
        v-if="tokenError"
        class="auth-error-block"
      >
        {{ tokenError }}
      </div>

      <div
        v-else-if="done"
        class="auth-success"
      >
        <p>Password updated! You can now sign in.</p>
        <router-link
          to="/login"
          class="auth-link"
        >
          Go to sign in
        </router-link>
      </div>

      <form
        v-else
        class="auth-form"
        @submit.prevent="submit"
      >
        <div class="field">
          <label class="label">New Password</label>
          <input
            v-model="form.password"
            type="password"
            class="input"
            placeholder="At least 8 characters"
            autocomplete="new-password"
            required
          >
        </div>

        <div class="field">
          <label class="label">Confirm Password</label>
          <input
            v-model="form.confirm"
            type="password"
            class="input"
            placeholder="Repeat password"
            autocomplete="new-password"
            required
          >
        </div>

        <p
          v-if="error"
          class="auth-error"
        >
          {{ error }}
        </p>

        <button
          type="submit"
          class="btn-primary w-full"
          :disabled="submitting"
        >
          {{ submitting ? 'Saving…' : 'Set new password' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'

const route = useRoute()
const token = route.query.token || ''

const form       = ref({ password: '', confirm: '' })
const error      = ref('')
const tokenError = ref('')
const submitting = ref(false)
const done       = ref(false)

onMounted(() => {
  if (!token) tokenError.value = 'Invalid or missing reset link.'
})

async function submit() {
  if (form.value.password !== form.value.confirm) {
    error.value = 'Passwords do not match.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await api.post('/auth/password-reset/confirm/', {
      token,
      password: form.value.password,
    })
    done.value = true
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to reset password.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-shell { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-card { width: 100%; max-width: 400px; background: var(--surface, #1a1a2e); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 40px 32px; }
.auth-title { font-size: 24px; font-weight: 700; text-align: center; margin: 0 0 28px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-error { color: #f87171; font-size: 13px; margin: 0; }
.auth-error-block { color: #f87171; text-align: center; padding: 16px 0; }
.auth-success { text-align: center; display: flex; flex-direction: column; gap: 20px; color: rgba(255,255,255,0.8); }
.auth-link { font-size: 13px; color: rgba(255,255,255,0.5); text-align: center; text-decoration: none; }
.auth-link:hover { color: rgba(255,255,255,0.8); }
.w-full { width: 100%; }
</style>
