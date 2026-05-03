<template>
  <div>
    <div class="no-print">
      <div class="flex items-center justify-between mb-6">
        <h1 class="text-xl font-mono font-bold text-white">
          Entries
        </h1>
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono disabled:opacity-40"
            :disabled="entriesToPrint.length === 0"
            @click="printEntries"
          >
            🖨 Print {{ selectedEntryIds.length ? `Selected (${selectedEntryIds.length})` : 'Entries' }}
          </button>
          <router-link
            to="/entries/create"
            class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
          >
            + New Entry
          </router-link>
        </div>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <input
          v-model="filters.party_name"
          type="text"
          placeholder="Search party name..."
          class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 font-mono placeholder-gray-600"
        >
        <select
          v-model="filters.company"
          class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
        >
          <option value="">
            All Companies
          </option>
          <option
            v-for="c in companies"
            :key="c.id"
            :value="c.id"
          >
            {{ c.name }}
          </option>
        </select>
        <select
          v-model="filters.car"
          class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
        >
          <option value="">
            All Cars
          </option>
          <option
            v-for="c in cars"
            :key="c.id"
            :value="c.id"
          >
            {{ c.name }}
          </option>
        </select>
        <div class="flex gap-2">
          <input
            v-model="filters.date_from"
            type="date"
            class="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
          >
          <input
            v-model="filters.date_to"
            type="date"
            class="w-full bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
          >
        </div>
      </div>

      <!-- Filter summary -->
      <div class="flex items-center justify-between mb-4">
        <p class="text-xs font-mono text-gray-500">
          Showing {{ filteredEntries.length }} of {{ entries.length }} entries
          <span v-if="selectedEntryIds.length">
            · {{ selectedEntryIds.length }} selected
          </span>
        </p>
        <div class="flex items-center gap-4">
          <button
            v-if="selectedEntryIds.length"
            class="text-xs font-mono text-gray-400 hover:text-white transition-colors"
            @click="clearSelection"
          >
            Clear selection ×
          </button>
          <button
            v-if="isFiltered"
            class="text-xs font-mono text-amber-400 hover:text-amber-300 transition-colors"
            @click="clearFilters"
          >
            Clear filters ×
          </button>
        </div>
      </div>

      <p
        v-if="loading"
        class="text-gray-500 text-sm"
      >
        Loading...
      </p>

      <p
        v-else-if="filteredEntries.length === 0"
        class="text-gray-500 text-sm"
      >
        No entries match your filters.
      </p>

      <div
        v-else
        class="overflow-x-auto"
      >
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="border-b border-gray-800 text-gray-400 text-left">
              <th class="py-3 pr-4 font-mono font-normal">
                <input
                  type="checkbox"
                  class="accent-amber-400"
                  :checked="allVisibleSelected"
                  :disabled="paginatedEntries.length === 0"
                  @change="toggleVisibleEntries($event.target.checked)"
                >
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Date
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Party
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Company
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Car
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                KMs
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Extra Hrs
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Row Total
              </th>
              <th class="py-3 pr-4 font-mono font-normal">
                Duty Slip
              </th>
              <th class="py-3 font-mono font-normal" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="entry in paginatedEntries"
              :key="entry.id"
              class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
            >
              <td class="py-3 pr-4">
                <input
                  v-model="selectedEntryIds"
                  type="checkbox"
                  class="accent-amber-400"
                  :value="entry.id"
                >
              </td>
              <td class="py-3 pr-4 font-mono text-gray-300">
                {{ entry.date }}
              </td>
              <td class="py-3 pr-4 text-white">
                {{ entry.party_name }}
              </td>
              <td class="py-3 pr-4 text-gray-300">
                {{ entry.company_name }}
              </td>
              <td class="py-3 pr-4 text-gray-300">
                {{ entry.car_name }}
              </td>
              <td class="py-3 pr-4 font-mono text-gray-300">
                {{ entry.total_kms }}
              </td>
              <td class="py-3 pr-4 font-mono text-gray-300">
                {{ entry.extra_hrs }}h extra
              </td>
              <td class="py-3 pr-4 font-mono text-amber-400">
                {{ currencySymbol }}{{ entry.row_total }}
              </td>
              <td class="py-3 pr-4">
                <span
                  v-if="entry.duty_slip"
                  class="text-xs bg-green-900 text-green-400 px-2 py-1 rounded font-mono"
                >
                  {{ formatSlipId(entry.duty_slip) }}
                </span>
                <span
                  v-else
                  class="text-xs text-gray-600 font-mono"
                >unassigned</span>
              </td>
              <td class="py-3 flex items-center gap-3">
                <button
                  class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                  @click="editingEntry = entry; showModal = true"
                >
                  Edit
                </button>
                <button
                  class="text-xs text-red-500 hover:text-red-400 transition-colors"
                  @click="deleteEntry(entry.id)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <!-- Pagination -->
        <div
          v-if="filteredEntries.length > 0"
          class="flex items-center justify-center gap-3 flex-wrap mt-6"
        >
          <p class="text-xs font-mono text-gray-500 mr-2">
            Showing {{ pageStart }}-{{ pageEnd }} of {{ filteredEntries.length }}
          </p>
          <button
            class="bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-600 text-xs font-mono px-3 py-2 rounded transition-colors disabled:opacity-35 disabled:cursor-not-allowed"
            :disabled="!hasPrev"
            @click="prevPage"
          >
            Previous
          </button>
          <div class="flex gap-1.5">
            <button
              v-for="page in totalPages"
              :key="page"
              class="border text-xs font-mono px-3 py-2 rounded transition-colors"
              :class="page === currentPage
                ? 'bg-amber-400 border-amber-400 text-gray-950'
                : 'bg-gray-900 border-gray-800 text-gray-400 hover:text-white hover:border-gray-600'"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button
            class="bg-gray-900 border border-gray-800 text-gray-400 hover:text-white hover:border-gray-600 text-xs font-mono px-3 py-2 rounded transition-colors disabled:opacity-35 disabled:cursor-not-allowed"
            :disabled="!hasNext"
            @click="nextPage"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <div class="print-only entries-print">
      <div class="print-header">
        <div>
          <h1>{{ selectedEntryIds.length ? 'Selected Entries Report' : 'Entries Report' }}</h1>
          <p>{{ printDate }}</p>
        </div>
        <div class="print-summary">
          <p>{{ entriesToPrint.length }} entries</p>
          <p>Total: {{ currencySymbol }}{{ entriesToPrintTotal }}</p>
        </div>
      </div>

      <div
        v-if="printFilterSummary"
        class="print-filters"
      >
        {{ printFilterSummary }}
      </div>

      <table class="print-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Party</th>
            <th>Company</th>
            <th>Car</th>
            <th>Total KMs</th>
            <th>Extra Hrs</th>
            <th>Bhatta</th>
            <th>Parking</th>
            <th>Duty Slip</th>
            <th>Row Total</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entriesToPrint"
            :key="entry.id"
          >
            <td>{{ entry.date }}</td>
            <td>{{ formatEntryType(entry.entry_type) }}</td>
            <td>{{ entry.party_name }}</td>
            <td>{{ entry.company_name }}</td>
            <td>{{ entry.car_name }}</td>
            <td>{{ entry.total_kms }}</td>
            <td>{{ entry.extra_hrs }}</td>
            <td>{{ currencySymbol }}{{ entry.driver_bhatta }}</td>
            <td>{{ currencySymbol }}{{ entry.parking }}</td>
            <td>{{ entry.duty_slip ? formatSlipId(entry.duty_slip) : 'Unassigned' }}</td>
            <td>{{ currencySymbol }}{{ entry.row_total }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td
              colspan="10"
              class="print-total-label"
            >
              GRAND TOTAL
            </td>
            <td class="print-total-value">
              {{ currencySymbol }}{{ entriesToPrintTotal }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="no-print">
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
import { usePagination } from '../composables/usePagination'


const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const entries = ref([])
const cars = ref([])
const companies = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingEntry = ref(null)
const selectedEntryIds = ref([])

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
    if (filters.value.company && String(e.company) !== String(filters.value.company))
      return false
    if (filters.value.car && String(e.car) !== String(filters.value.car))
      return false
    if (filters.value.date_from && e.date < filters.value.date_from)
      return false
    if (filters.value.date_to && e.date > filters.value.date_to)
      return false
    return true
  })
})

const selectedEntries = computed(() => {
  const selected = new Set(selectedEntryIds.value.map(id => String(id)))
  return entries.value.filter(e => selected.has(String(e.id)))
})

const entriesToPrint = computed(() =>
  selectedEntries.value.length ? selectedEntries.value : filteredEntries.value
)

const entriesToPrintTotal = computed(() =>
  entriesToPrint.value
    .reduce((sum, e) => sum + parseFloat(e.row_total || 0), 0)
    .toFixed(2)
)

const allVisibleSelected = computed(() =>
  paginatedEntries.value.length > 0 &&
  paginatedEntries.value.every(e => selectedEntryIds.value.includes(e.id))
)

const printDate = computed(() =>
  new Date().toLocaleDateString('en-AU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
)

const printFilterSummary = computed(() => {
  const parts = []
  if (filters.value.party_name) parts.push(`Party: ${filters.value.party_name}`)
  if (filters.value.company) {
    const company = companies.value.find(c => String(c.id) === String(filters.value.company))
    parts.push(`Company: ${company?.name || filters.value.company}`)
  }
  if (filters.value.car) {
    const car = cars.value.find(c => String(c.id) === String(filters.value.car))
    parts.push(`Car: ${car?.name || filters.value.car}`)
  }
  if (filters.value.date_from) parts.push(`From: ${filters.value.date_from}`)
  if (filters.value.date_to) parts.push(`To: ${filters.value.date_to}`)
  return parts.join(' | ')
})

function formatEntryType(type) {
  return type === 'outstation' ? 'Outstation' : 'Regular'
}

function printEntries() {
  window.print()
}

function clearSelection() {
  selectedEntryIds.value = []
}

function toggleVisibleEntries(checked) {
  const visibleIds = paginatedEntries.value.map(e => e.id)
  if (checked) {
    selectedEntryIds.value = Array.from(new Set([...selectedEntryIds.value, ...visibleIds]))
  } else {
    selectedEntryIds.value = selectedEntryIds.value.filter(id => !visibleIds.includes(id))
  }
}

function clearFilters() {
  filters.value = { party_name: '', company: '', car: '', date_from: '', date_to: '' }
}
const {
  paginated: paginatedEntries,
  currentPage,
  totalPages,
  pageStart,
  pageEnd,
  hasPrev,
  hasNext,
  goToPage,
  prevPage,
  nextPage,
} = usePagination(filteredEntries)
async function fetchEntries() {
  try {
    const [entriesRes, carsRes, companiesRes] = await Promise.all([
      api.get('/entries/'),
      api.get('/cars/'),
      api.get('/companies/'),
    ])
    entries.value = entriesRes.data
    selectedEntryIds.value = selectedEntryIds.value.filter(id =>
      entries.value.some(e => e.id === id)
    )
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
  selectedEntryIds.value = selectedEntryIds.value.filter(entryId => entryId !== id)
  notify('Entry deleted.')
}

async function onEntrySaved() {
  await fetchEntries()
  notify('Entry updated successfully.')
}

onMounted(fetchEntries)
</script>

<style scoped>
.print-only {
  display: none;
}

.entries-print {
  color: #111;
  font-family: Arial, sans-serif;
}

.print-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  border-bottom: 2px solid #111;
  padding-bottom: 14px;
  margin-bottom: 14px;
}

.print-header h1 {
  font-size: 24px;
  letter-spacing: 1px;
  margin: 0 0 4px;
  text-transform: uppercase;
}

.print-header p,
.print-summary p,
.print-filters {
  color: #555;
  font-size: 11px;
  margin: 0;
}

.print-summary {
  text-align: right;
}

.print-filters {
  border-bottom: 1px solid #ddd;
  margin-bottom: 14px;
  padding-bottom: 10px;
}

.print-table {
  border-collapse: collapse;
  font-size: 9px;
  width: 100%;
}

.print-table th {
  background: #111;
  color: #fff;
  font-weight: 600;
  padding: 7px 5px;
  text-align: left;
  white-space: nowrap;
}

.print-table td {
  border-bottom: 1px solid #ddd;
  padding: 6px 5px;
  white-space: nowrap;
}

.print-table tbody tr:nth-child(even) td {
  background: #f7f7f7;
}

.print-total-label,
.print-total-value {
  border-top: 2px solid #111;
  font-weight: 700;
  padding-top: 9px;
}

.print-total-label {
  text-align: right;
}

@media print {
  @page {
    size: A4 landscape;
    margin: 14mm;
  }
}
</style>
