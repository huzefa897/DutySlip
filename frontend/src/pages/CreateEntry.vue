<template>
  <div class="page container">
    <button
      class="back-btn"
      @click="$router.back()"
    >
      ← Back
    </button>
    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Entries</span>
        <h1 class="page-title">
          Create a new entry
        </h1>
        <p class="page-header__subtitle">
          Add a trip row without changing pricing, routing, or assignment logic.
        </p>
      </div>
    </div>

    <form
      class="section-card form"
      @submit.prevent="submit"
    >
      <!-- Party Name -->
      <div class="field">
        <label class="label">Party Name</label>
        <AutocompleteInput
          v-model="form.party_name"
          :suggestions="partyNames"
          placeholder="Enter or select party name"
          required
        />
        <p
          v-if="partyNames.length > 0"
          class="upload-hint"
        >
          {{ partyNames.length }} saved name(s) for this company
        </p>
      </div>
      <!-- Company -->
      <div class="field">
        <label class="label">Company</label>
        <select
          v-model="form.company"
          required
          class="field-control"
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

      <!-- Date -->
      <div class="field">
        <label class="label">Date</label>
        <input
          v-model="form.date"
          type="date"
          required
          class="field-control"
        >
      </div>

      <!-- Entry Type -->
      <div class="field">
        <label class="label">Entry Type</label>
        <div class="toggle-group">
          <button
            type="button"
            class="toggle-btn"
            :class="{ 'toggle-btn--regular': form.entry_type === 'regular' }"
            @click="form.entry_type = 'regular'"
          >
            Regular
          </button>
          <button
            type="button"
            class="toggle-btn"
            :class="{ 'toggle-btn--outstation': form.entry_type === 'outstation' }"
            @click="form.entry_type = 'outstation'"
          >
            Outstation
          </button>
        </div>
      </div>

      <!-- Car -->
      <div class="field">
        <label class="label">Car</label>
        <select
          v-model="form.car"
          required
          class="field-control"
        >
          <option
            value=""
            disabled
          >
            Select car
          </option>
          <option
            v-for="c in cars"
            :key="c.id"
            :value="c.id"
          >
            {{ c.name }} — {{ currencySymbol }}{{ c.base_rate }} base
          </option>
        </select>

        <!-- Regular rate override indicator -->
        <div
          v-if="rateOverride && form.entry_type === 'regular'"
          class="summary-card mt-2"
        >
          <div class="space-y-1 text-sm text-amber-200">
            <p class="font-semibold text-amber-300">
              Custom rates applied for this company
            </p>
            <p v-if="rateOverride.base_rate">
              Base: {{ currencySymbol }}{{ rateOverride.base_rate }}
            </p>
            <p v-if="rateOverride.extra_km_rate">
              Extra KM: {{ currencySymbol }}{{ rateOverride.extra_km_rate }}/km
            </p>
            <p v-if="rateOverride.extra_hr_rate">
              Extra HR: {{ currencySymbol }}{{ rateOverride.extra_hr_rate }}/hr
            </p>
          </div>
        </div>

        <!-- Outstation rate override indicator -->
        <div
          v-if="rateOverride?.outstation_rate && form.entry_type === 'outstation'"
          class="summary-card mt-2"
        >
          <div class="text-sm text-blue-200">
            <p class="font-semibold text-blue-300">
              Custom outstation rate applied
            </p>
            <p>{{ currencySymbol }}{{ rateOverride.outstation_rate }}/km</p>
          </div>
        </div>
      </div>

      <!-- KMs -->
      <div class="grid grid-cols-2 gap-4">
        <div class="field">
          <label class="label">Start KMs</label>
          <input
            v-model="form.start_kms"
            type="number"
            step="0.01"
            required
            class="field-control"
          >
        </div>
        <div class="field">
          <label class="label">End KMs</label>
          <input
            v-model="form.end_kms"
            type="number"
            step="0.01"
            required
            class="field-control"
          >
        </div>
      </div>

      <!-- Times — regular only -->
      <div
        v-if="form.entry_type === 'regular'"
        class="grid grid-cols-2 gap-4"
      >
        <div class="field">
          <label class="label">Start Time</label>
          <input
            v-model="form.start_time"
            type="time"
            :required="form.entry_type === 'regular'"
            class="field-control"
          >
        </div>
        <div class="field">
          <label class="label">End Time</label>
          <input
            v-model="form.end_time"
            type="time"
            :required="form.entry_type === 'regular'"
            class="field-control"
          >
        </div>
      </div>

      <!-- Charges -->
      <div class="grid grid-cols-2 gap-4">
        <div class="field">
          <label class="label">Driver Bhatta ({{ currencySymbol }})</label>
          <input
            v-model="form.driver_bhatta"
            type="number"
            step="0.01"
            class="field-control"
          >
        </div>
        <div class="field">
          <label class="label">Parking ({{ currencySymbol }})</label>
          <input
            v-model="form.parking"
            type="number"
            step="0.01"
            class="field-control"
          >
        </div>
      </div>

      <!-- Optional Duty Slip assignment -->
      <div class="field">
        <label class="label">
          Assign to Duty Slip <span class="label-hint">(optional)</span>
        </label>
        <select
          v-model="form.duty_slip"
          class="field-control"
        >
          <option value="">
            None — save as standalone
          </option>
          <option
            v-for="s in dutySlips"
            :key="s.id"
            :value="s.id"
          >
            {{ s.party_name }} · {{ s.company_name }}
          </option>
        </select>
      </div>

      <!-- Notes -->
      <div class="field">
        <label class="label">Notes (optional)</label>
        <textarea
          v-model="form.notes"
          rows="2"
          class="field-control textarea"
        />
      </div>

      <!-- Error -->
      <p
        v-if="error"
        class="error"
      >
        {{ error }}
      </p>

      <!-- Submit -->
      <div class="actions">
        <button
          type="submit"
          :disabled="submitting"
          class="btn-primary"
        >
          {{ submitting ? 'Saving...' : 'Save Entry' }}
        </button>
        <router-link
          to="/"
          class="btn-cancel px-2 py-2"
        >
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
