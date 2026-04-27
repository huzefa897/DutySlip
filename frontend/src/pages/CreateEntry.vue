<template>
  <div class="max-w-2xl">
    <button @click="$router.back()"
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1">
      ← Back
    </button>
    <h1 class="text-xl font-mono font-bold text-white mb-6">New Entry</h1>

    <form @submit.prevent="submit" class="space-y-5">

      <!-- Party Name -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Party Name</label>
        <AutocompleteInput v-model="form.party_name" :suggestions="partyNames" placeholder="Enter or select party name"
          required />
        <p v-if="partyNames.length > 0" class="text-xs text-gray-600 font-mono mt-1">
          {{ partyNames.length }} saved name(s) for this company
        </p>
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

      <!-- Entry Type -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Entry Type</label>
        <div class="flex gap-2">
          <button type="button" @click="form.entry_type = 'regular'"
            class="flex-1 py-2 text-xs font-mono rounded border transition-colors" :class="form.entry_type === 'regular'
              ? 'bg-amber-400 border-amber-400 text-gray-950 font-bold'
              : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'">
            Regular
          </button>
          <button type="button" @click="form.entry_type = 'outstation'"
            class="flex-1 py-2 text-xs font-mono rounded border transition-colors" :class="form.entry_type === 'outstation'
              ? 'bg-blue-500 border-blue-500 text-white font-bold'
              : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'">
            Outstation
          </button>
        </div>
      </div>

      <!-- Car -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Car</label>
        <select v-model="form.car" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
          <option value="" disabled>Select car</option>
          <option v-for="c in cars" :key="c.id" :value="c.id">
            {{ c.name }} — {{ currencySymbol }}{{ c.base_rate }} base
          </option>
        </select>

        <!-- Regular rate override indicator -->
        <div v-if="rateOverride && form.entry_type === 'regular'"
          class="mt-2 flex items-start gap-2 bg-amber-400/10 border border-amber-400/30 rounded px-3 py-2">
          <span class="text-amber-400 text-xs mt-0.5">⚡</span>
          <div class="text-xs font-mono text-amber-300 space-y-0.5">
            <p class="font-bold text-amber-400">Custom rates applied for this company</p>
            <p v-if="rateOverride.base_rate">Base: {{ currencySymbol }}{{ rateOverride.base_rate }}</p>
            <p v-if="rateOverride.extra_km_rate">Extra KM: {{ currencySymbol }}{{ rateOverride.extra_km_rate }}/km</p>
            <p v-if="rateOverride.extra_hr_rate">Extra HR: {{ currencySymbol }}{{ rateOverride.extra_hr_rate }}/hr</p>
          </div>
        </div>

        <!-- Outstation rate override indicator -->
        <div v-if="rateOverride?.outstation_rate && form.entry_type === 'outstation'"
          class="mt-2 flex items-start gap-2 bg-blue-400/10 border border-blue-400/30 rounded px-3 py-2">
          <span class="text-blue-400 text-xs mt-0.5">⚡</span>
          <div class="text-xs font-mono text-blue-300">
            <p class="font-bold text-blue-400">Custom outstation rate applied</p>
            <p>{{ currencySymbol }}{{ rateOverride.outstation_rate }}/km</p>
          </div>
        </div>
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

      <!-- Times — regular only -->
      <div v-if="form.entry_type === 'regular'" class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Start Time</label>
          <input v-model="form.start_time" type="time" :required="form.entry_type === 'regular'"
            class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
        </div>
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">End Time</label>
          <input v-model="form.end_time" type="time" :required="form.entry_type === 'regular'"
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
        <select v-model="form.duty_slip"
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
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
        <router-link to="/" class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
          Cancel
        </router-link>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { notify } from '../store/notification'
import { currencySymbol } from '../store/currency'
import AutocompleteInput from '../components/AutoCompleteInput.vue'

const router = useRouter()
const cars = ref([])
const dutySlips = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')
const rateOverride = ref(null)
const partyNames = ref([])

const form = ref({
  party_name: '',
  company: '',
  date: '',
  entry_type: 'regular',
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

// ── Watch company → load party name suggestions ───────────────
watch(
  () => form.value.company,
  async (companyId) => {
    partyNames.value = []
    if (!companyId) return
    try {
      const res = await api.get(`/companies/${companyId}/parties/`)
      partyNames.value = res.data
    } catch {
      partyNames.value = []
    }
  }
)

// ── Watch company + car → load rate overrides ─────────────────
watch(
  () => [form.value.company, form.value.car],
  async ([companyId, carId]) => {
    rateOverride.value = null
    if (!companyId || !carId) return
    try {
      const res = await api.get(`/companies/${companyId}/rates/`)
      const match = res.data.find(r => r.car === carId)
      rateOverride.value = match || null
    } catch {
      rateOverride.value = null
    }
  }
)

// ── Fetch dropdowns ───────────────────────────────────────────
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

// ── Submit ────────────────────────────────────────────────────
async function submit() {
  submitting.value = true
  error.value = ''
  try {
    await api.post('/entries/', form.value)
    router.push('/')
    notify('Entry created successfully.')
  } catch (e) {
    error.value = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : 'Something went wrong'
    notify('Failed to create entry.', 'error')
  } finally {
    submitting.value = false
  }
}

onMounted(fetchOptions)
</script>