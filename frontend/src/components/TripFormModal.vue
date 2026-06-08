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
              {{ props.trip ? 'Edit Duty Slip' : 'New Duty Slip' }}
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
                <label class="label">Duty Slip Type</label>
                <p
                  v-if="lockedTripType"
                  class="upload-hint mb-2"
                >
                  This invoice only accepts {{ lockedTripType === 'outstation' ? 'outstation' : 'regular' }} duty slip types.
                </p>
                <div class="toggle-group">
                  <button
                    type="button"
                    class="toggle-btn"
                    :class="{ 'toggle-btn--regular': form.trip_type === 'regular' }"
                    :disabled="!!lockedTripType"
                    @click="form.trip_type = 'regular'"
                  >
                    Regular
                  </button>
                  <button
                    type="button"
                    class="toggle-btn"
                    :class="{ 'toggle-btn--outstation': form.trip_type === 'outstation' }"
                    :disabled="!!lockedTripType"
                    @click="form.trip_type = 'outstation'"
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
              v-if="form.trip_type === 'regular'"
              class="grid grid-cols-2 gap-3"
            >
              <div class="field">
                <label class="label">Start Time</label>
                <input
                  v-model="form.start_time"
                  type="time"
                  :required="form.trip_type === 'regular'"
                  class="field-control"
                >
              </div>
              <div class="field">
                <label class="label">End Time</label>
                <input
                  v-model="form.end_time"
                  type="time"
                  :required="form.trip_type === 'regular'"
                  class="field-control"
                >
              </div>
            </div>

            <div
              v-if="form.trip_type === 'outstation' && rateOverride?.outstation_rate"
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
                  Duty Slip Type
                </p>
                <p class="summary-card__value">
                  {{ form.trip_type === 'outstation' ? 'Outstation' : 'Regular' }}
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
              {{ submitting ? 'Saving...' : props.trip ? 'Save Changes' : 'Save Duty Slip' }}
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

const props = defineProps({
    partyName: String,
    companyId: Number,
    invoiceId: Number,
    lockedTripType: String,
    trip: Object,
})

const emit = defineEmits(['close', 'saved'])

const cars = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')
const rateOverride = ref(null)
const currentStep = ref(1)

const form = ref({
    party_name: props.trip?.party_name || props.partyName || '',
    company: props.trip?.company || props.companyId || '',
    date: props.trip?.date || '',
    car: props.trip?.car || '',
    start_kms: props.trip?.start_kms || '',
    end_kms: props.trip?.end_kms || '',
    start_time: props.trip?.start_time || '',
    end_time: props.trip?.end_time || '',
    driver_bhatta: props.trip?.driver_bhatta || '0',
    parking: props.trip?.parking || '0',
    trip_type: props.lockedTripType || props.trip?.trip_type || 'regular',
    notes: props.trip?.notes || '',
})

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
    () => props.lockedTripType,
    (lockedType) => {
        if (lockedType) {
            form.value.trip_type = lockedType
        }
    },
    { immediate: true }
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
    (form.value.trip_type === 'outstation' || (form.value.start_time && form.value.end_time))
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
    { immediate: true }
)

function goToStepTwo() {
    error.value = ''
    if (!canGoNext.value) return
    currentStep.value = 2
}

async function submit() {
    submitting.value = true
    error.value = ''
    try {
        if (props.lockedTripType) {
            form.value.trip_type = props.lockedTripType
        }
        let res
        if (props.trip) {
            res = await api.put(`/trips/${props.trip.id}/`, form.value)
        } else {
            const payload = { ...form.value }
            if (props.invoiceId) payload.invoice = props.invoiceId
            res = await api.post('/trips/', payload)
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

onMounted(async () => {
    const [carsRes, companiesRes] = await Promise.all([
        api.get('/cars/'),
        api.get('/companies/'),
    ])
    cars.value = carsRes.data
    companies.value = companiesRes.data

    if (props.trip?.company && props.trip?.car) {
        try {
            const res = await api.get(`/companies/${props.trip.company}/rates/`)
            const match = res.data.find(r => r.car === props.trip.car)
            rateOverride.value = match || null
        } catch {
            rateOverride.value = null
        }
    }
})
</script>
