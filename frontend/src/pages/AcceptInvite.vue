<template>
  <div class="auth-shell">
    <div class="auth-card">
      <h1 class="auth-title">
        Set up your account
      </h1>
      <p class="auth-subtitle">
        You've been invited to DutySlip
      </p>

      <div
        v-if="tokenError"
        class="auth-error-block"
      >
        {{ tokenError }}
      </div>

      <form
        v-else
        class="auth-form"
        @submit.prevent="submit"
      >
        <div class="field">
          <label class="label">Your Name</label>
          <input
            v-model="form.name"
            type="text"
            class="input"
            placeholder="Full name"
            required
          >
        </div>

        <div class="field">
          <label class="label">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="input"
            placeholder="Choose a password"
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
          {{ submitting ? 'Creating account…' : 'Create account' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'

const router = useRouter()
const route  = useRoute()

const form       = ref({ name: '', password: '', confirm: '' })
const error      = ref('')
const tokenError = ref('')
const submitting = ref(false)
const token      = route.query.token || ''

onMounted(() => {
  if (!token) tokenError.value = 'Invalid or missing invite link.'
})

async function submit() {
  if (form.value.password !== form.value.confirm) {
    error.value = 'Passwords do not match.'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    await api.post('/auth/accept-invite/', {
      token,
      name: form.value.name,
      password: form.value.password,
    })
    router.push('/login')
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to create account.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.auth-shell {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface, #1a1a2e);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 40px 32px;
}
.auth-title { font-size: 24px; font-weight: 700; text-align: center; margin: 0 0 6px; }
.auth-subtitle { font-size: 14px; color: rgba(255,255,255,0.5); text-align: center; margin: 0 0 28px; }
.auth-form { display: flex; flex-direction: column; gap: 16px; }
.auth-error { color: #f87171; font-size: 13px; margin: 0; }
.auth-error-block { color: #f87171; text-align: center; padding: 16px 0; }
.w-full { width: 100%; }
</style>
