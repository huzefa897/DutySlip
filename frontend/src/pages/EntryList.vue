<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-mono font-bold text-white">Entries</h1>
      <router-link
        to="/entries/create"
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
      >
        + New Entry
      </router-link>
    </div>

    <!-- Filters -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      <input
        v-model="filters.party_name"
        type="text"
        placeholder="Search party name..."
        class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 font-mono placeholder-gray-600"
      />
      <select
        v-model="filters.company"
        class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
      >
        <option value="">All Companies</option>
        <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select
        v-model="filters.car"
        class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
      >
        <option value="">All Cars</option>
        <option v-for="c in cars" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <div class="flex gap-2">
        <input
          v-model="filters.date_from"
          type="date"
          class="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
        />
        <input
          v-model="filters.date_to"
          type="date"
          class="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
        />
      </div>
    </div>

    <!-- Filter summary -->
    <div class="flex items-center justify-between mb-4">
      <p class="text-xs font-mono text-gray-500">
        Showing {{ filteredEntries.length }} of {{ entries.length }} entries
      </p>
      <button
        v-if="isFiltered"
        @click="clearFilters"
        class="text-xs font-mono text-amber-400 hover:text-amber-300 transition-colors"
      >
        Clear filters ×
      </button>
    </div>

    <p v-if="loading" class="text-gray-500 text-sm">Loading...</p>

    <p v-else-if="filteredEntries.length === 0" class="text-gray-500 text-sm">
      No entries match your filters.
    </p>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-gray-800 text-gray-400 text-left">
            <th class="py-3 pr-4 font-mono font-normal">Date</th>
            <th class="py-3 pr-4 font-mono font-normal">Party</th>
            <th class="py-3 pr-4 font-mono font-normal">Company</th>
            <th class="py-3 pr-4 font-mono font-normal">Car</th>
            <th class="py-3 pr-4 font-mono font-normal">KMs</th>
            <th class="py-3 pr-4 font-mono font-normal">Extra Hrs</th>
            <th class="py-3 pr-4 font-mono font-normal">Row Total</th>
            <th class="py-3 pr-4 font-mono font-normal">Duty Slip</th>
            <th class="py-3 font-mono font-normal"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in filteredEntries"
            :key="entry.id"
            class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
          >
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.date }}</td>
            <td class="py-3 pr-4 text-white">{{ entry.party_name }}</td>
            <td class="py-3 pr-4 text-gray-300">{{ entry.company_name }}</td>
            <td class="py-3 pr-4 text-gray-300">{{ entry.car_name }}</td>
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.total_kms }}</td>
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.extra_hrs }}h extra</td>
            <td class="py-3 pr-4 font-mono text-amber-400">{{ currencySymbol }}{{ entry.row_total }}</td>
            <td class="py-3 pr-4">
              <span v-if="entry.duty_slip"
                class="text-xs bg-green-900 text-green-400 px-2 py-1 rounded font-mono">
                {{ formatSlipId(entry.duty_slip) }}
              </span>
              <span v-else class="text-xs text-gray-600 font-mono">unassigned</span>
            </td>
            <td class="py-3 flex items-center gap-3">
              <button
                @click="editingEntry = entry; showModal = true"
                class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Edit
              </button>
              <button
                @click="deleteEntry(entry.id)"
                class="text-xs text-red-500 hover:text-red-400 transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <EntryFormModal
      v-if="showModal"
      :entry="editingEntry"
      @close="showModal = false; editingEntry = null"
      @saved="onEntrySaved"
    />
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
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import { notify } from '../store/notification'
import EntryFormModal from '../components/EntryFormModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const entries = ref([])
const cars = ref([])
const companies = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingEntry = ref(null)

const filters = ref({
  party_name: '',
  company: '',
  car: '',
  date_from: '',
  date_to: '',
})

const isFiltered = computed(() =>
  Object.values(filters.value).some(v => v !== '')
)

const filteredEntries = computed(() => {
  return entries.value.filter(e => {
    if (filters.value.party_name &&
      !e.party_name.toLowerCase().includes(filters.value.party_name.toLowerCase()))
      return false
    if (filters.value.company && e.company !== filters.value.company)
      return false
    if (filters.value.car && e.car !== filters.value.car)
      return false
    if (filters.value.date_from && e.date < filters.value.date_from)
      return false
    if (filters.value.date_to && e.date > filters.value.date_to)
      return false
    return true
  })
})

function clearFilters() {
  filters.value = { party_name: '', company: '', car: '', date_from: '', date_to: '' }
}

async function fetchEntries() {
  try {
    const [entriesRes, carsRes, companiesRes] = await Promise.all([
      api.get('/entries/'),
      api.get('/cars/'),
      api.get('/companies/'),
    ])
    entries.value = entriesRes.data
    cars.value = carsRes.data
    companies.value = companiesRes.data
  } finally {
    loading.value = false
  }
}
async function deleteEntry(id) {
  const ok = await ask({
    title: 'Delete Entry',
    message: 'Are you sure you want to delete this entry? This cannot be undone.',
    confirmLabel: 'Delete',
  })
  if (!ok) return
  await api.delete(`/entries/${id}/`)
  entries.value = entries.value.filter(e => e.id !== id)
  notify('Entry deleted.')
}

async function onEntrySaved() {
  await fetchEntries()
  notify('Entry updated successfully.')
}

onMounted(fetchEntries)
</script>