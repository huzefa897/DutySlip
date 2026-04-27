<template>
  <div class="container">
    <button @click="$router.back()" class="back-btn">← Back</button>
    <h1 class="title">New Duty Slip</h1>

    <form @submit.prevent="submit" class="form">

      <div class="field">
        <label class="label">Party Name</label>
        <input v-model="form.party_name" type="text" required class="input" />
      </div>

      <div class="field">
        <label class="label">Company</label>
        <select v-model="form.company" required class="input">
          <option value="" disabled>Select company</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <div class="field">
        <label class="label">Slip Type</label>
        <div class="toggle-group">
          <button
            type="button"
            @click="form.slip_type = 'regular'"
            class="toggle-btn"
            :class="{ 'toggle-btn--regular': form.slip_type === 'regular' }"
          >
            Regular
          </button>
          <button
            type="button"
            @click="form.slip_type = 'outstation'"
            class="toggle-btn"
            :class="{ 'toggle-btn--outstation': form.slip_type === 'outstation' }"
          >
            Outstation
          </button>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="actions">
        <button type="submit" :disabled="submitting" class="btn-primary">
          {{ submitting ? 'Creating...' : 'Create Duty Slip' }}
        </button>
        <router-link to="/dutyslips" class="btn-cancel">Cancel</router-link>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const companies = ref([])
const submitting = ref(false)
const error = ref('')

const form = ref({
  party_name: '',
  company: '',
  slip_type: 'regular',
})

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const res = await api.post('/dutyslips/', form.value)
    router.push(`/dutyslips/${res.data.id}`)
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Something went wrong')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const res = await api.get('/companies/')
  companies.value = res.data
})
</script>

<style scoped>
.container {
  max-width: 42rem;
}

.back-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-family: monospace;
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 1rem;
  padding: 0;
  transition: color 0.2s;
}

.back-btn:hover {
  color: #ffffff;
}

.title {
  font-family: monospace;
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 1.5rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
}

.label {
  font-family: monospace;
  font-size: 0.75rem;
  color: #9ca3af;
  margin-bottom: 0.25rem;
}

.input {
  width: 100%;
  background-color: #111827;
  border: 1px solid #374151;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
  color: #ffffff;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.input:focus {
  border-color: #fbbf24;
}

.toggle-group {
  display: flex;
  gap: 0.5rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.5rem;
  font-family: monospace;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  border: 1px solid #374151;
  background-color: #111827;
  color: #9ca3af;
  cursor: pointer;
  transition: border-color 0.2s, color 0.2s, background-color 0.2s;
}

.toggle-btn:hover {
  border-color: #6b7280;
}

.toggle-btn--regular {
  background-color: #fbbf24;
  border-color: #fbbf24;
  color: #030712;
  font-weight: 700;
}

.toggle-btn--outstation {
  background-color: #3b82f6;
  border-color: #3b82f6;
  color: #ffffff;
  font-weight: 700;
}

.error {
  color: #f87171;
  font-size: 0.875rem;
  margin: 0;
}

.actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-primary {
  background-color: #fbbf24;
  color: #030712;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.5rem 1.5rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #fcd34d;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-cancel {
  font-size: 0.875rem;
  color: #9ca3af;
  padding: 0.5rem 1rem;
  text-decoration: none;
  transition: color 0.2s;
}

.btn-cancel:hover {
  color: #ffffff;
}
</style>