<template>
  <div class="auth-shell">
    <div class="auth-card">
      <h1 class="auth-title">
        Reset password
      </h1>
      <p class="auth-subtitle">
        Enter your email and we'll send you a reset link
      </p>

      <form
        v-if="!sent"
        class="auth-form"
        @submit.prevent="submit"
      >
        <div class="field">
          <label class="label">Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
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
          {{ submitting ? 'Sending…' : 'Send reset link' }}
        </button>

        <router-link
          to="/login"
          class="auth-link"
        >
          Back to sign in
        </router-link>
      </form>

      <div
        v-else
        class="auth-success"
      >
        <p>Check your inbox — if that email is registered, a reset link has been sent.</p>
        <router-link
          to="/login"
          class="auth-link"
        >
          Back to sign in
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'

const email      = ref('')
const error      = ref('')
const submitting = ref(false)
const sent       = ref(false)

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    await api.post('/auth/password-reset/', { email: email.value })
    sent.value = true
  } catch {
    error.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-shell { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.auth-card { width: 100%; max-width: 400px; background: var(--surface, #1a1a2e); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 40px 32px; }
.auth-title { font-size: 24px; font-weight: 700; text-align: center; margin: 0 0 6px; }
.auth-subtitle { font-size: 14px; color: rgba(255,255,255,0.5); text-align: center; margin: 0 0 28px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-error { color: #f87171; font-size: 13px; margin: 0; }
.auth-success { text-align: center; display: flex; flex-direction: column; gap: 20px; color: rgba(255,255,255,0.8); }
.auth-link { font-size: 13px; color: rgba(255,255,255,0.5); text-align: center; text-decoration: none; }
.auth-link:hover { color: rgba(255,255,255,0.8); }
.w-full { width: 100%; }
</style>
