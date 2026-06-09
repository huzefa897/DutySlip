<template>
  <div class="auth-shell">
    <div class="auth-card">
      <h1 class="auth-title">
        DutySlip
      </h1>
      <p class="auth-subtitle">
        Sign in to your account
      </p>

      <form
        class="auth-form"
        @submit.prevent="submit"
      >
        <div class="field">
          <label class="label">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            placeholder="you@example.com"
            autocomplete="email"
            required
          >
        </div>

        <div class="field">
          <label class="label">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="input"
            placeholder="••••••••"
            autocomplete="current-password"
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
          {{ submitting ? 'Signing in…' : 'Sign in' }}
        </button>

        <router-link
          to="/auth/reset-password"
          class="auth-link"
        >
          Forgot password?
        </router-link>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '../api'
import { setTokens } from '../store/auth'

const router   = useRouter()
const route    = useRoute()
const form     = ref({ email: '', password: '' })
const error    = ref('')
const submitting = ref(false)

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const res = await api.post('/auth/login/', {
      username: form.value.email,
      password: form.value.password,
    })
    setTokens(res.data.access, res.data.refresh)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (e) {
    const detail = e.response?.data?.detail
    error.value = detail || 'Invalid email or password.'
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
  max-width: 400px;
  background: var(--surface, #1a1a2e);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 40px 32px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 6px;
}

.auth-subtitle {
  font-size: 14px;
  color: rgba(255,255,255,0.5);
  text-align: center;
  margin: 0 0 32px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-error {
  color: #f87171;
  font-size: 13px;
  margin: 0;
}

.auth-link {
  font-size: 13px;
  color: rgba(255,255,255,0.5);
  text-align: center;
  text-decoration: none;
}

.auth-link:hover {
  color: rgba(255,255,255,0.8);
}

.w-full { width: 100%; }
</style>
