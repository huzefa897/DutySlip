<template>
  <div class="page items-center">
    <button
      class="back-btn self-start"
      @click="$router.back()"
    >
      ← Back
    </button>
    <div class="w-full max-w-4xl">
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
        class="section-card form w-full"
        @submit.prevent="submit"
      >
        <div class="summary-card">
          <div class="flex items-center gap-3">
            <div
              class="status-badge"
              :class="currentStep === 1 ? 'status-badge--finalised' : 'status-badge--draft'"
            >
              1
            </div>
            <div class="flex-1 h-px bg-white/10" />
            <div
              class="status-badge"
              :class="currentStep === 2 ? 'status-badge--finalised' : 'status-badge--draft'"
            >
              2
            </div>
          </div>
        </div>

        <template v-if="currentStep === 1">
          <div class="modal-form-grid">
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

            <div class="field">
              <label class="label">Date</label>
              <input
                v-model="form.date"
                type="date"
                required
                class="field-control"
              >
            </div>

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

            <div class="field modal-form-grid__full">
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
          </div>

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
        </template>

        <template v-else>
          <div class="modal-form-grid">
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
            <div class="field modal-form-grid__full">
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
                  v-for="s in matchingDutySlips"
                  :key="s.id"
                  :value="s.id"
                >
                  {{ s.party_name }} · {{ s.company_name }}
                </option>
              </select>
              <p class="upload-hint">
                Showing {{ matchingDutySlips.length }} {{ form.entry_type }} invoice(s) for assignment.
              </p>
            </div>
          </div>

          <div class="summary-grid !grid-cols-2">
            <div class="summary-card">
              <p class="summary-card__label">
                Entry Type
              </p>
              <p class="summary-card__value">
                {{ form.entry_type === 'outstation' ? 'Outstation' : 'Regular' }}
              </p>
            </div>
            <div class="summary-card">
              <p class="summary-card__label">
                KMs
              </p>
              <p class="summary-card__value">
                {{ form.start_kms || '—' }} → {{ form.end_kms || '—' }}
              </p>
            </div>
          </div>

          <div class="field">
            <label class="label">Notes (optional)</label>
            <textarea
              v-model="form.notes"
              rows="4"
              class="field-control textarea"
            />
          </div>
        </template>

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
            v-if="currentStep === 2"
            type="button"
            class="btn-secondary"
            @click="currentStep = 1"
          >
            Back
          </button>
          <button
            v-if="currentStep === 1"
            type="button"
            class="btn-primary"
            :disabled="!canGoNext"
            @click="currentStep = 2"
          >
            Next
          </button>
          <button
            v-else
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
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
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
const currentStep = ref(1)

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

const canGoNext = computed(() =>
  Boolean(
    form.value.party_name &&
    form.value.company &&
    form.value.date &&
    form.value.car &&
    form.value.start_kms !== '' &&
    form.value.end_kms !== '' &&
    (form.value.entry_type === 'outstation' || (form.value.start_time && form.value.end_time))
  )
)

const matchingDutySlips = computed(() =>
  dutySlips.value.filter((slip) => slip.slip_type === form.value.entry_type)
)

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

watch(
  () => form.value.entry_type,
  () => {
    if (
      form.value.duty_slip &&
      !matchingDutySlips.value.some((slip) => String(slip.id) === String(form.value.duty_slip))
    ) {
      form.value.duty_slip = ''
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
