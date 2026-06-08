<template>
  <div class="container">
    <button
      class="back-btn"
      @click="$router.back()"
    >
      ← Back
    </button>
    <h1 class="title">
      New Invoice
    </h1>

    <form
      class="form"
      @submit.prevent="submit"
    >
      <div class="field">
        <label class="label">Party Name</label>
        <input
          v-model="form.party_name"
          type="text"
          required
          class="input"
        >
      </div>

      <div class="field">
        <label class="label">Company</label>
        <select
          v-model="form.company"
          required
          class="input"
        >
          <option
            value=""
            disabled
          >
            Select company
          </option>
          <option
            v-for="c in companies"
            :key="c.id"
            :value="c.id"
          >
            {{ c.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label class="label">Invoice Type</label>
        <div class="toggle-group">
          <button
            type="button"
            class="toggle-btn"
            :class="{ 'toggle-btn--regular': form.invoice_type === 'regular' }"
            @click="form.invoice_type = 'regular'"
          >
            Regular
          </button>
          <button
            type="button"
            class="toggle-btn"
            :class="{ 'toggle-btn--outstation': form.invoice_type === 'outstation' }"
            @click="form.invoice_type = 'outstation'"
          >
            Outstation
          </button>
        </div>
      </div>

      <p
        v-if="error"
        class="error"
      >
        {{ error }}
      </p>

      <div class="actions">
        <button
          type="submit"
          :disabled="submitting"
          class="btn-primary"
        >
          {{ submitting ? 'Creating...' : 'Create Invoice' }}
        </button>
        <router-link
          to="/invoices"
          class="btn-cancel"
        >
          Cancel
        </router-link>
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
  invoice_type: 'regular',
})

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const res = await api.post('/invoices/', form.value)
    router.push(`/invoices/${res.data.id}`)
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
