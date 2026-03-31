<template>
  <div class="max-w-2xl">
    <h1 class="text-xl font-mono font-bold text-white mb-6">New Entry</h1>

    <form @submit.prevent="submit" class="space-y-5">

      <!-- Party Name -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Party Name</label>
        <input v-model="form.party_name" type="text" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Company -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Company</label>
        <select v-model="form.company" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
          <option value="" disabled>Select company</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <!-- Date -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Date</label>
        <input v-model="form.date" type="date" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Car -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Car</label>
        <select v-model="form.car" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
          <option value="" disabled>Select car</option>
          <option v-for="c in cars" :key="c.id" :value="c.id">
            {{ c.name }} — ${{ c.base_rate }} base
          </option>
        </select>
      </div>

      <!-- KMs -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Start KMs</label>
          <input v-model="form.start_kms" type="number" step="0.01" required
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">End KMs</label>
          <input v-model="form.end_kms" type="number" step="0.01" required
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
      </div>

      <!-- Times -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Start Time</label>
          <input v-model="form.start_time" type="time" required
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">End Time</label>
          <input v-model="form.end_time" type="time" required
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
      </div>

      <!-- Charges -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Driver Bhatta ($)</label>
          <input v-model="form.driver_bhatta" type="number" step="0.01"
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Parking ($)</label>
          <input v-model="form.parking" type="number" step="0.01"
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
      </div>
      <!-- Optional Duty Slip assignment -->

<div>
  <label class="block text-xs text-gray-400 font-mono mb-1">
    Assign to Duty Slip <span class="text-gray-600">(optional)</span>
  </label>
  <select
    v-model="form.duty_slip"
    class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
  >
    <option value="">None — save as standalone</option>
    <option v-for="s in dutySlips" :key="s.id" :value="s.id">
      {{ s.party_name }} · {{ s.company_name }}
    </option>
  </select>
</div>
      <!-- Notes -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Notes (optional)</label>
        <textarea v-model="form.notes" rows="2"
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Error -->
      <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

      <!-- Submit -->
      <div class="flex gap-3">
        <button type="submit" :disabled="submitting"
          class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50">
          {{ submitting ? 'Saving...' : 'Save Entry' }}
        </button>
        <router-link to="/"
          class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
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
const cars = ref([])
const dutySlips = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')

const form = ref({
  party_name: '',
  company: '',
  date: '',
  car: '',
  start_kms: '',
  end_kms: '',
  start_time: '',
  end_time: '',
  driver_bhatta: '0',
  parking: '0',
  duty_slip: '',
  notes: '',
})

async function fetchOptions() {
  const [carsRes, companiesRes, slipsRes] = await Promise.all([
    api.get('/cars/'),
    api.get('/companies/'),
     api.get('/dutyslips/'),
  ])
  cars.value = carsRes.data
  companies.value = companiesRes.data   
  dutySlips.value = slipsRes.data
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    await api.post('/entries/', form.value)
    router.push('/')
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Something went wrong')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchOptions)
</script>