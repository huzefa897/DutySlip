<template>
  <Teleport to="body">
    <div
      class="modal-overlay"
      @click.self="$emit('close')"
    >
      <div class="modal-card modal-card--wide w-full">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">
              {{ props.entry ? 'Edit Entry' : 'New Entry' }}
            </h2>
            <p class="page-header__subtitle mt-1">
              Step {{ currentStep }} of 2 · {{ currentStep === 1 ? 'Basics' : 'Charges & Notes' }}
            </p>
          </div>

          <button
            class="btn-cancel text-xl leading-none"
            @click="$emit('close')"
          >
            ×
          </button>
        </div>

        <form
          class="modal-body modal-body--compact form"
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
                  :readonly="!!partyName"
                  placeholder="Enter or select party name"
                  required
                />
              </div>

              <div class="field">
                <label class="label">Company</label>
                <select
                  v-model="form.company"
                  required
                  :disabled="!!companyId"
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
                  v-if="rateOverride"
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
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
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
              class="grid grid-cols-2 gap-3"
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

            <div
              v-if="form.entry_type === 'outstation' && rateOverride?.outstation_rate"
              class="summary-card mt-2"
            >
              <div class="text-sm text-blue-200">
                <p class="font-semibold text-blue-300">
                  Custom outstation rate applied
                </p>
                <p>{{ currencySymbol }}{{ rateOverride.outstation_rate }}/km</p>
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

          <p
            v-if="error"
            class="error"
          >
            {{ error }}
          </p>

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
              @click="goToStepTwo"
            >
              Next
            </button>
            <button
              v-else
              type="submit"
              :disabled="submitting"
              class="btn-primary"
            >
              {{ submitting ? 'Saving...' : props.entry ? 'Save Changes' : 'Save Entry' }}
            </button>
            <button
              type="button"
              class="btn-cancel px-2 py-2"
              @click="$emit('close')"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import AutocompleteInput from './AutoCompleteInput.vue'
// ── 1. Props first ────────────────────────────────────────────
const props = defineProps({
    partyName: String,
    companyId: Number,
    dutySlipId: Number,
    entry: Object,
})

const emit = defineEmits(['close', 'saved'])

// ── 2. Refs ───────────────────────────────────────────────────
const cars = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')
const rateOverride = ref(null)
const currentStep = ref(1)

// ── 3. Form (needs props, so must come after defineProps) ─────
const form = ref({
    party_name: props.entry?.party_name || props.partyName || '',
    company: props.entry?.company || props.companyId || '',
    date: props.entry?.date || '',
    car: props.entry?.car || '',
    start_kms: props.entry?.start_kms || '',
    end_kms: props.entry?.end_kms || '',
    start_time: props.entry?.start_time || '',
    end_time: props.entry?.end_time || '',
    driver_bhatta: props.entry?.driver_bhatta || '0',
    parking: props.entry?.parking || '0',
    entry_type: props.entry?.entry_type || 'regular',
    notes: props.entry?.notes || '',
})

// ── 4. Watch (needs form, so must come after form ref) ────────
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
const partyNames = ref([])

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
    },
    { immediate: true } // ← run on mount too if company is pre-filled
)
// ── 5. Functions ──────────────────────────────────────────────
function goToStepTwo() {
    error.value = ''
    if (!canGoNext.value) return
    currentStep.value = 2
}

async function submit() {
    submitting.value = true
    error.value = ''
    try {
        let res
        if (props.entry) {
            res = await api.put(`/entries/${props.entry.id}/`, form.value)
        } else {
            const payload = { ...form.value }
            if (props.dutySlipId) payload.duty_slip = props.dutySlipId
            res = await api.post('/entries/', payload)
        }
        emit('saved', res.data)
        emit('close')
    } catch (e) {
        error.value = e.response?.data
            ? Object.values(e.response.data).flat().join(' ')
            : 'Something went wrong'
    } finally {
        submitting.value = false
    }
}

// ── 6. Lifecycle ──────────────────────────────────────────────
onMounted(async () => {
    const [carsRes, companiesRes] = await Promise.all([
        api.get('/cars/'),
        api.get('/companies/'),
    ])
    cars.value = carsRes.data
    companies.value = companiesRes.data

    // check override on load if editing an existing entry
    if (props.entry?.company && props.entry?.car) {
        try {
            const res = await api.get(`/companies/${props.entry.company}/rates/`)
            const match = res.data.find(r => r.car === props.entry.car)
            rateOverride.value = match || null
        } catch {
            rateOverride.value = null
        }
    }
})
</script>
