<template>
  <div class="page">
    <button
      class="back-btn"
      @click="$router.back()"
    >
      ← Back
    </button>

    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Companies</span>
        <h1 class="page-title">
          Client companies
        </h1>
      </div>
      <button
        class="btn-primary"
        @click="openCreate"
      >
        + New Company
      </button>
    </div>

    <p
      v-if="loading"
      class="empty-text"
    >
      Loading...
    </p>
    <p
      v-else-if="companies.length === 0"
      class="empty-text"
    >
      No companies yet.
    </p>

    <div
      v-else
      class="card-list"
    >
      <div
        v-for="company in companies"
        :key="company.id"
        class="table-card overflow-hidden"
      >
        <!-- Company Row -->
        <div class="flex items-center justify-between gap-3 px-4 py-4">
          <div>
            <p class="card-name mt-0">
              {{ company.name }}
            </p>
            <p class="card-meta">
              ABN: {{ company.abn }}
            </p>
          </div>
          <div class="flex items-center gap-3">
            <button
              class="clear-filters"
              @click="toggleRates(company)"
            >
              {{ expandedCompany === company.id ? 'Hide Rates ↑' : 'Car Rates ↓' }}
            </button>
            <button
              class="clear-filters"
              @click="openEdit(company)"
            >
              Edit
            </button>
            <button
              class="btn-delete"
              @click="deleteCompany(company)"
            >
              Delete
            </button>
          </div>
        </div>

        <!-- Car Rates Panel -->
        <div
          v-if="expandedCompany === company.id"
          class="border-t border-white/8 px-4 py-4"
        >
          <p class="section-label mb-3">
            Car Rate Overrides
            <span class="label-hint ml-1">(leave blank to use global rates)</span>
          </p>

          <!-- Existing Overrides -->
          <div
            v-if="companyRates.length > 0"
            class="card-list mb-4"
          >
            <div
              v-for="rate in companyRates"
              :key="rate.id"
              class="selection-item text-xs"
            >
              <span>{{ rate.car_name }}</span>
              <span class="data-table__muted">
                Base: {{ currencySymbol }}{{ rate.base_rate ?? '—' }} ·
                /km: {{ currencySymbol }}{{ rate.extra_km_rate ?? '—' }} ·
                /hr: {{ currencySymbol }}{{ rate.extra_hr_rate ?? '—' }}
              </span>
              <button
                class="btn-delete ml-4"
                @click="deleteRate(company.id, rate.car)"
              >
                Remove
              </button>
            </div>
          </div>

          <p
            v-else
            class="empty-text mb-4"
          >
            No overrides — using global car rates.
          </p>

          <div class="summary-card space-y-3">
            <p class="section-label">
              Add / Update Override
            </p>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div>
                <label class="label">Car</label>
                <select
                  v-model="rateForm.car"
                  class="field-control"
                >
                  <option
                    value=""
                    disabled
                  >
                    Select
                  </option>
                  <option
                    v-for="car in cars"
                    :key="car.id"
                    :value="car.id"
                  >
                    {{ car.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="label">Base Rate</label>
                <input
                  v-model="rateForm.base_rate"
                  type="number"
                  step="0.01"
                  placeholder="e.g. 120"
                  class="field-control"
                >
              </div>
              <div>
                <label class="label">Extra Kms Rate</label>
                <input
                  v-model="rateForm.extra_km_rate"
                  type="number"
                  step="0.01"
                  placeholder="e.g. 1.50"
                  class="field-control"
                >
              </div>
              <div>
                <label class="label">Extra Hr Rate</label>
                <input
                  v-model="rateForm.extra_hr_rate"
                  type="number"
                  step="0.01"
                  placeholder="e.g. 15"
                  class="field-control"
                >
              </div>
              <div>
                <label class="label">Outstation /km</label>
                <input
                  v-model="rateForm.outstation_rate"
                  type="number"
                  step="0.01"
                  placeholder="e.g. 2.00"
                  class="field-control"
                >
              </div>
            </div>          
            <button
              :disabled="!rateForm.car"
              class="btn-primary"
              @click="saveRate(company.id)"
            >
              Save Override
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Company Modal -->
    <div
      v-if="showModal"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ editingCompany ? 'Edit Company' : 'New Company' }}
          </h2>
          <button
            class="btn-cancel text-xl leading-none"
            @click="closeModal"
          >
            ×
          </button>
        </div>
        <form
          class="modal-body form"
          @submit.prevent="submit"
        >
          <div class="field">
            <label class="label">Company Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="field-control"
            >
          </div>
          <div class="field">
            <label class="label">ABN</label>
            <input
              v-model="form.abn"
              type="text"
              required
              class="field-control"
            >
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
              {{ submitting ? 'Saving...' : editingCompany ? 'Save Changes' : 'Create Company' }}
            </button>
            <button
              type="button"
              class="btn-cancel px-2 py-2"
              @click="closeModal"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
    <ConfirmDialog
      :visible="confirmVisible"
      :title="confirmTitle"
      :message="confirmMessage"
      :confirm-label="confirmLabel"
      :destructive="destructive"
      @confirm="onConfirm"
      @cancel="onCancel"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { notify } from '../store/notification'
import { currencySymbol } from '../store/currency'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()
const companies = ref([])
const cars = ref([])
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)
const error = ref('')
const editingCompany = ref(null)
const expandedCompany = ref(null)
const companyRates = ref([])

const form = ref({ name: '', abn: '' })
const rateForm = ref({
  car: '',
  base_rate: '',
  extra_km_rate: '',
  extra_hr_rate: '',
  outstation_rate: '',
})
async function fetchCompanies() {
  try {
    const res = await api.get('/companies/')
    companies.value = res.data
  } finally {
    loading.value = false
  }
}



async function fetchRates(companyId) {
  const res = await api.get(`/companies/${companyId}/rates/`)
  companyRates.value = res.data
}
async function saveRate(companyId) {
  if (!rateForm.value.car) return
  await api.post(`/companies/${companyId}/rates/`, {
    car:             rateForm.value.car,
    company:         companyId,
    base_rate:       rateForm.value.base_rate       || null,
    extra_km_rate:   rateForm.value.extra_km_rate   || null,
    extra_hr_rate:   rateForm.value.extra_hr_rate   || null,
    outstation_rate: rateForm.value.outstation_rate || null,
  })
  rateForm.value = { car: '', base_rate: '', extra_km_rate: '', extra_hr_rate: '', outstation_rate: '' }
  await fetchRates(companyId)
  notify('Rate override saved.')
}
async function toggleRates(company) {
  if (expandedCompany.value === company.id) {
    expandedCompany.value = null
    companyRates.value = []
    return
  }
  expandedCompany.value = company.id
  rateForm.value = { car: '', base_rate: '', extra_km_rate: '', extra_hr_rate: '', outstation_rate: '' }
  await fetchRates(company.id)
}

async function deleteRate(companyId, carId) {
  await api.delete(`/companies/${companyId}/rates/${carId}/`)
  await fetchRates(companyId)
  notify('Rate override removed.')
}

function openCreate() {
  editingCompany.value = null
  form.value = { name: '', abn: '' }
  error.value = ''
  showModal.value = true
}

function openEdit(company) {
  editingCompany.value = company
  form.value = { name: company.name, abn: company.abn }
  error.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingCompany.value = null
  error.value = ''
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    if (editingCompany.value) {
      const res = await api.put(`/companies/${editingCompany.value.id}/`, form.value)
      const idx = companies.value.findIndex(c => c.id === editingCompany.value.id)
      companies.value[idx] = res.data
      notify('Company updated successfully.')
    } else {
      const res = await api.post('/companies/', form.value)
      companies.value.push(res.data)
      notify('Company created successfully.')
    }
    closeModal()
  } catch (e) {
    error.value = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : 'Something went wrong'
  } finally {
    submitting.value = false
  }
}

async function deleteCompany(company) {
  const ok = await ask({
    title: `Delete "${company.name}"`,
    message: `This will permanently delete ${company.name} and all associated data. This cannot be undone.`,
    confirmLabel: 'Delete',
  })
  if (!ok) return
  try {
    await api.delete(`/companies/${company.id}/`)
    companies.value = companies.value.filter(c => c.id !== company.id)
    notify(`"${company.name}" deleted.`)
  } catch (e) {
    notify(e.response?.data?.error || 'Cannot delete — company is used in existing records.', 'error')
  }
}

onMounted(async () => {
  await fetchCompanies()
  const carsRes = await api.get('/cars/')
  cars.value = carsRes.data
})
</script>
