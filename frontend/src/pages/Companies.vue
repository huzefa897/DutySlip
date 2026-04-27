<template>
  <div>
    <button
      @click="$router.back()"
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
    >
      ← Back
    </button>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-mono font-bold text-white">Companies</h1>
      <button
        @click="openCreate"
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
      >
        + New Company
      </button>
    </div>

    <p v-if="loading" class="text-gray-500 text-sm">Loading...</p>
    <p v-else-if="companies.length === 0" class="text-gray-500 text-sm">No companies yet.</p>

    <div v-else class="space-y-3">
      <div
        v-for="company in companies"
        :key="company.id"
        class="bg-gray-900 border border-gray-800 rounded-lg overflow-hidden"
      >
        <!-- Company Row -->
        <div class="flex items-center justify-between px-4 py-3">
          <div>
            <p class="text-white font-medium text-sm">{{ company.name }}</p>
            <p class="text-gray-500 text-xs font-mono mt-0.5">ABN: {{ company.abn }}</p>
          </div>
          <div class="flex items-center gap-3">
            <button
              @click="toggleRates(company)"
              class="text-xs text-amber-400 hover:text-amber-300 font-mono transition-colors"
            >
              {{ expandedCompany === company.id ? 'Hide Rates ↑' : 'Car Rates ↓' }}
            </button>
            <button
              @click="openEdit(company)"
              class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteCompany(company)"
              class="text-xs text-red-500 hover:text-red-400 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>

        <!-- Car Rates Panel -->
        <div
          v-if="expandedCompany === company.id"
          class="border-t border-gray-800 px-4 py-4"
        >
          <p class="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">
            Car Rate Overrides
            <span class="text-gray-600 normal-case ml-1">(leave blank to use global rates)</span>
          </p>

          <!-- Existing Overrides -->
          <div v-if="companyRates.length > 0" class="mb-4 space-y-2">
            <div
              v-for="rate in companyRates"
              :key="rate.id"
              class="flex items-center justify-between bg-gray-800 rounded px-3 py-2 text-xs font-mono"
            >
              <span class="text-white">{{ rate.car_name }}</span>
              <span class="text-gray-400">
                Base: {{ currencySymbol }}{{ rate.base_rate ?? '—' }} ·
                /km: {{ currencySymbol }}{{ rate.extra_km_rate ?? '—' }} ·
                /hr: {{ currencySymbol }}{{ rate.extra_hr_rate ?? '—' }}
              </span>
              <button
                @click="deleteRate(company.id, rate.car)"
                class="text-red-500 hover:text-red-400 transition-colors ml-4"
              >
                Remove
              </button>
            </div>
          </div>

          <p v-else class="text-gray-600 text-xs font-mono mb-4">
            No overrides — using global car rates.
          </p>

          <!-- Add Override Form -->
          <div class="bg-gray-800/50 rounded p-3 space-y-3">
            <p class="text-xs font-mono text-gray-400">Add / Update Override</p>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div>
                <label class="block text-xs text-gray-500 font-mono mb-1">Car</label>
                <select
                  v-model="rateForm.car"
                  class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-amber-400"
                >
                  <option value="" disabled>Select</option>
                  <option v-for="car in cars" :key="car.id" :value="car.id">
                    {{ car.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-xs text-gray-500 font-mono mb-1">Base Rate</label>
                <input
                  v-model="rateForm.base_rate"
                  type="number" step="0.01"
                  placeholder="e.g. 120"
                  class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-amber-400"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 font-mono mb-1">Extra Kms Rate</label>
                <input
                  v-model="rateForm.extra_km_rate"
                  type="number" step="0.01"
                  placeholder="e.g. 1.50"
                  class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-amber-400"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 font-mono mb-1">Extra Hr Rate</label>
                <input
                  v-model="rateForm.extra_hr_rate"
                  type="number" step="0.01"
                  placeholder="e.g. 15"
                  class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-amber-400"
                />
              </div>
              <div>
                <label class="block text-xs text-gray-500 font-mono mb-1">Outstation /km</label>
                <input
                  v-model="rateForm.outstation_rate"
                  type="number" step="0.01"
                  placeholder="e.g. 2.00"
                  class="w-full bg-gray-800 border border-gray-700 rounded px-2 py-1.5 text-white text-xs focus:outline-none focus:border-amber-400"
                />
              </div>
            </div>          
            <button
              @click="saveRate(company.id)"
              :disabled="!rateForm.car"
              class="bg-amber-400 text-gray-950 text-xs font-bold px-4 py-1.5 rounded hover:bg-amber-300 transition-colors disabled:opacity-40"
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
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-gray-900 border border-gray-800 rounded-lg w-full max-w-md">
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider">
            {{ editingCompany ? 'Edit Company' : 'New Company' }}
          </h2>
          <button @click="closeModal" class="text-gray-500 hover:text-white text-xl leading-none">×</button>
        </div>
        <form @submit.prevent="submit" class="px-6 py-5 space-y-4">
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Company Name</label>
            <input v-model="form.name" type="text" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
          </div>
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">ABN</label>
            <input v-model="form.abn" type="text" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
          </div>
          <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>
          <div class="flex gap-3 pt-2">
            <button type="submit" :disabled="submitting"
              class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50">
              {{ submitting ? 'Saving...' : editingCompany ? 'Save Changes' : 'Create Company' }}
            </button>
            <button type="button" @click="closeModal"
              class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
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