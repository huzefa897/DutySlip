<template>
  <div
    class="page"
    :class="{ 'page--selection-active': selectedTripIds.length > 0 }"
  >
    <div class="no-print">
      <div class="page-header">
        <div class="page-header__content">
          <span class="page-header__eyebrow">Duty Slips</span>
          <h1 class="page-title">
            Duty Slip records
          </h1>
          <p class="page-header__subtitle">
            Manage all duty slip entries before assigning them to invoices.
          </p>
        </div>
        <div class="quick-actions-row">
          <button
            type="button"
            class="btn-secondary"
            :disabled="tripsToPrint.length === 0"
            @click="printTrips"
          >
            Print {{ selectedTripIds.length ? `Selected (${selectedTripIds.length})` : 'Duty Slips' }}
          </button>
          <button
            type="button"
            class="btn-secondary"
            :disabled="downloadingExcel"
            @click="downloadTripsExcel"
          >
            {{ downloadingExcel ? 'Preparing Excel...' : 'Export Excel' }}
          </button>
          <router-link
            v-if="isAdmin"
            to="/duty-slips/create"
            class="btn-primary"
          >
            + New Duty Slip
          </router-link>
        </div>
      </div>

      <div
        v-if="isClient && !activeCompany"
        class="empty-state-container py-20"
      >
        <div class="empty-state text-center max-w-sm mx-auto">
          <div class="empty-state__icon w-16 h-16 mx-auto mb-6 opacity-20">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path d="M4 21V7l8-4 8 4v14M9 21V11h6v10" />
            </svg>
          </div>
          <h2 class="text-xl font-semibold mb-3">
            Select a Company
          </h2>
          <p class="text-sm opacity-50 leading-relaxed">
            Please select a company from the header to view its duty slips.
          </p>
        </div>
      </div>

      <section
        v-else
        class="section-card"
      >
        <div class="filters-grid">
          <input
            v-model="filters.party_name"
            type="text"
            placeholder="Search party name..."
            class="input"
          >
          <select
            v-if="isAdmin"
            v-model="filters.company"
            class="input"
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
            class="input"
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
          <div class="quick-actions-row">
            <input
              v-model="filters.date_from"
              type="date"
              class="input"
            >
            <input
              v-model="filters.date_to"
              type="date"
              class="input"
            >
          </div>
        </div>

        <div class="filter-summary">
          <p class="filter-count">
            Showing {{ filteredTrips.length }} of {{ trips.length }} duty slips
            <span v-if="selectedTripIds.length">
              · {{ selectedTripIds.length }} selected
            </span>
          </p>
          <div class="quick-actions-row">
            <button
              v-if="selectedTripIds.length"
              class="clear-filters"
              @click="clearSelection"
            >
              Clear selection
            </button>
            <button
              v-if="isFiltered"
              class="clear-filters"
              @click="clearFilters"
            >
              Clear filters
            </button>
          </div>
        </div>
      </section>

      <p
        v-if="loading"
        class="empty-text"
      >
        Loading...
      </p>

      <p
        v-else-if="filteredTrips.length === 0"
        class="empty-text"
      >
        No duty slips match your filters.
      </p>

      <section
        v-else
        class="table-card"
      >
        <div class="table-shell">
          <table class="data-table">
            <thead>
              <tr>
                <th>
                  <input
                    type="checkbox"
                    class="sr-only"
                    :checked="allVisibleSelected"
                    :disabled="paginatedTrips.length === 0"
                    @change="toggleVisibleTrips($event.target.checked)"
                  >
                  <span
                    class="slip-checkbox"
                    :class="{ 'slip-checkbox--checked': allVisibleSelected }"
                  />
                </th>
                <th>Date</th>
                <th>Party</th>
                <th>Company</th>
                <th>Car</th>
                <th>KMs</th>
                <th>Extra Hrs</th>
                <th>Row Total</th>
                <th>Invoice</th>
                <th
                  v-if="isAdmin"
                  class="data-table__actions"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="trip in paginatedTrips"
                :key="trip.id"
                class="entry-row"
                :class="{ 'entry-row--selected': selectedTripIds.includes(trip.id) }"
              >
                <td>
                  <label class="entry-select">
                    <input
                      v-model="selectedTripIds"
                      type="checkbox"
                      class="sr-only"
                      :value="trip.id"
                    >
                    <span
                      class="slip-checkbox"
                      :class="{ 'slip-checkbox--checked': selectedTripIds.includes(trip.id) }"
                    />
                  </label>
                </td>
                <td class="data-table__numeric data-table__muted">
                  {{ trip.date }}
                </td>
                <td>
                  {{ trip.party_name }}
                </td>
                <td class="data-table__muted">
                  {{ trip.company_name }}
                </td>
                <td class="data-table__muted">
                  {{ trip.car_name }}
                </td>
                <td class="data-table__numeric data-table__muted">
                  {{ trip.total_kms }}
                </td>
                <td class="data-table__numeric data-table__muted">
                  {{ trip.extra_hrs }}h extra
                </td>
                <td class="data-table__numeric data-table__accent">
                  {{ currencySymbol }}{{ trip.row_total }}
                </td>
                <td>
                  <span
                    v-if="trip.invoice"
                    class="status-badge status-badge--paid"
                  >
                    INV-{{ formatSlipId(trip.invoice) }}
                  </span>
                  <span
                    v-else
                    class="status-badge status-badge--draft"
                  >unassigned</span>
                </td>
                <td
                  v-if="isAdmin"
                  class="data-table__actions"
                >
                  <div class="data-table__actions-group data-table__actions-group--compact">
                    <RowActionMenu
                      @edit="editingTrip = trip; showModal = true"
                      @delete="deleteTrip(trip.id)"
                    />
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-if="filteredTrips.length > 0"
          class="pagination-row p-4"
        >
          <p class="pagination-info">
            Showing {{ pageStart }}-{{ pageEnd }} of {{ filteredTrips.length }}
          </p>
          <button
            class="btn-page"
            :disabled="!hasPrev"
            @click="prevPage"
          >
            Previous
          </button>
          <div class="page-numbers">
            <button
              v-for="page in totalPages"
              :key="page"
              class="btn-page-number"
              :class="{ 'btn-page-number--active': page === currentPage }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button
            class="btn-page"
            :disabled="!hasNext"
            @click="nextPage"
          >
            Next
          </button>
        </div>
      </section>
    </div>

    <div
      v-if="selectedTripIds.length > 0"
      class="selection-bar"
    >
      <span class="selection-bar__count">
        {{ selectedTripIds.length }} selected
      </span>
      <div class="selection-bar__actions">
        <button
          class="btn-secondary"
          @click="clearSelection"
        >
          Clear selection
        </button>
        <button
          class="btn-secondary"
          :disabled="downloadingExcel"
          @click="downloadTripsExcel"
        >
          {{ downloadingExcel ? 'Preparing Excel...' : 'Export Excel' }}
        </button>
        <button
          class="btn-secondary"
          :disabled="tripsToPrint.length === 0"
          @click="printTrips"
        >
          Print Selected
        </button>
      </div>
    </div>

    <div class="print-only trips-print">
      <div class="print-header">
        <div>
          <h1>{{ selectedTripIds.length ? 'Selected Duty Slips Report' : 'Duty Slips Report' }}</h1>
          <p>{{ printDate }}</p>
        </div>
        <div class="print-summary">
          <p>{{ tripsToPrint.length }} duty slips</p>
          <p>Total: {{ currencySymbol }}{{ tripsToPrintTotal }}</p>
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
            <th>Invoice</th>
            <th>Row Total</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="trip in tripsToPrint"
            :key="trip.id"
          >
            <td>{{ trip.date }}</td>
            <td>{{ formatTripType(trip.trip_type) }}</td>
            <td>{{ trip.party_name }}</td>
            <td>{{ trip.company_name }}</td>
            <td>{{ trip.car_name }}</td>
            <td>{{ trip.total_kms }}</td>
            <td>{{ trip.extra_hrs }}</td>
            <td>{{ currencySymbol }}{{ trip.driver_bhatta }}</td>
            <td>{{ currencySymbol }}{{ trip.parking }}</td>
            <td>{{ trip.invoice ? formatSlipId(trip.invoice) : 'Unassigned' }}</td>
            <td>{{ currencySymbol }}{{ trip.row_total }}</td>
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
              {{ currencySymbol }}{{ tripsToPrintTotal }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>

    <div class="no-print">
      <TripFormModal
        v-if="showModal"
        :trip="editingTrip"
        @close="showModal = false; editingTrip = null"
        @saved="onTripSaved"
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
import TripFormModal from '../components/TripFormModal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'
import { usePagination } from '../composables/usePagination'
import RowActionMenu from '../components/RowActionMenu.vue'
import { isAdmin, isClient, activeCompany } from '../store/auth'


const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const trips = ref([])
const cars = ref([])
const companies = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingTrip = ref(null)
const selectedTripIds = ref([])
const downloadingExcel = ref(false)

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

const filteredTrips = computed(() => {
  return trips.value.filter(t => {
    if (filters.value.party_name &&
      !t.party_name.toLowerCase().includes(filters.value.party_name.toLowerCase()))
      return false
    if (filters.value.company && String(t.company) !== String(filters.value.company))
      return false
    if (filters.value.car && String(t.car) !== String(filters.value.car))
      return false
    if (filters.value.date_from && t.date < filters.value.date_from)
      return false
    if (filters.value.date_to && t.date > filters.value.date_to)
      return false
    return true
  })
})

const selectedTrips = computed(() => {
  const selected = new Set(selectedTripIds.value.map(id => String(id)))
  return trips.value.filter(t => selected.has(String(t.id)))
})

const tripsToPrint = computed(() =>
  selectedTrips.value.length ? selectedTrips.value : filteredTrips.value
)

const tripsToPrintTotal = computed(() =>
  tripsToPrint.value
    .reduce((sum, t) => sum + parseFloat(t.row_total || 0), 0)
    .toFixed(2)
)

const allVisibleSelected = computed(() =>
  paginatedTrips.value.length > 0 &&
  paginatedTrips.value.every(t => selectedTripIds.value.includes(t.id))
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

function formatTripType(type) {
  return type === 'outstation' ? 'Outstation' : 'Regular'
}

function escapeHtml(value) {
  return String(value ?? '—')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function buildPrintHtml() {
  const rows = tripsToPrint.value.map((trip) => `
    <tr>
      <td>${escapeHtml(trip.date)}</td>
      <td>${escapeHtml(formatTripType(trip.trip_type))}</td>
      <td>${escapeHtml(trip.party_name)}</td>
      <td>${escapeHtml(trip.company_name)}</td>
      <td>${escapeHtml(trip.car_name)}</td>
      <td>${escapeHtml(trip.total_kms)}</td>
      <td>${escapeHtml(trip.extra_hrs)}</td>
      <td>${escapeHtml(`${currencySymbol.value}${trip.driver_bhatta}`)}</td>
      <td>${escapeHtml(`${currencySymbol.value}${trip.parking}`)}</td>
      <td>${escapeHtml(trip.invoice ? `INV-${formatSlipId(trip.invoice)}` : 'Unassigned')}</td>
      <td>${escapeHtml(`${currencySymbol.value}${trip.row_total}`)}</td>
    </tr>
  `).join('')

  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>${selectedTripIds.value.length ? 'Selected Duty Slips Report' : 'Duty Slips Report'}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          color: #111;
          margin: 0;
          padding: 32px;
          background: #fff;
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
        .print-summary { text-align: right; }
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
        @page {
          size: A4 landscape;
          margin: 14mm;
        }
      </style>
    </head>
    <body>
      <div class="print-header">
        <div>
          <h1>${escapeHtml(selectedTripIds.value.length ? 'Selected Duty Slips Report' : 'Duty Slips Report')}</h1>
          <p>${escapeHtml(printDate.value)}</p>
        </div>
        <div class="print-summary">
          <p>${escapeHtml(`${tripsToPrint.value.length} duty slips`)}</p>
          <p>Total: ${escapeHtml(`${currencySymbol.value}${tripsToPrintTotal.value}`)}</p>
        </div>
      </div>
      ${printFilterSummary.value ? `<div class="print-filters">${escapeHtml(printFilterSummary.value)}</div>` : ''}
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
            <th>Invoice</th>
            <th>Row Total</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
        <tfoot>
          <tr>
            <td colspan="10" class="print-total-label">GRAND TOTAL</td>
            <td class="print-total-value">${escapeHtml(`${currencySymbol.value}${tripsToPrintTotal.value}`)}</td>
          </tr>
        </tfoot>
      </table>
    </body>
  </html>`
}

function printTrips() {
  const printWindow = window.open('', '_blank', 'width=1200,height=900')
  if (!printWindow) {
    notify('Popup blocked. Allow popups to print the duty slips report.', 'error')
    return
  }

  printWindow.document.open()
  printWindow.document.write(buildPrintHtml())
  printWindow.document.close()
  printWindow.focus()
  printWindow.onload = () => {
    printWindow.print()
  }
}

async function downloadTripsExcel() {
  downloadingExcel.value = true
  try {
    const params = {}
    if (selectedTripIds.value.length > 0) {
      params.ids = selectedTripIds.value.join(',')
    } else {
      if (filters.value.party_name) params.party_name = filters.value.party_name
      if (filters.value.company) params.company = filters.value.company
      if (filters.value.car) params.car = filters.value.car
      if (filters.value.date_from) params.date_from = filters.value.date_from
      if (filters.value.date_to) params.date_to = filters.value.date_to
      if (isClient.value && activeCompany.value) params.company = activeCompany.value.id
    }

    const response = await api.get('/trips/excel/', {
      responseType: 'blob',
      params,
    })
    const blobUrl = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    const suffix = selectedTripIds.value.length > 0 ? 'selected' : 'filtered'
    link.download = `trips-export-${suffix}-${new Date().toISOString().slice(0, 10).replaceAll('-', '')}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(blobUrl)
    notify('Duty Slips Excel exported.')
  } catch {
    notify('Failed to export Duty Slips Excel.', 'error')
  } finally {
    downloadingExcel.value = false
  }
}

function clearSelection() {
  selectedTripIds.value = []
}

function toggleVisibleTrips(checked) {
  const visibleIds = paginatedTrips.value.map(t => t.id)
  if (checked) {
    selectedTripIds.value = Array.from(new Set([...selectedTripIds.value, ...visibleIds]))
  } else {
    selectedTripIds.value = selectedTripIds.value.filter(id => !visibleIds.includes(id))
  }
}

function clearFilters() {
  filters.value = { party_name: '', company: '', car: '', date_from: '', date_to: '' }
}
const {
  paginated: paginatedTrips,
  currentPage,
  totalPages,
  pageStart,
  pageEnd,
  hasPrev,
  hasNext,
  goToPage,
  prevPage,
  nextPage,
} = usePagination(filteredTrips)

async function fetchTrips() {
  if (isClient.value && !activeCompany.value) {
    loading.value = false
    return
  }

  const params = isClient.value && activeCompany.value
    ? { company: activeCompany.value.id }
    : {}

  try {
    const [tripsRes, carsRes, companiesRes] = await Promise.all([
      api.get('/trips/', { params }),
      api.get('/cars/'),
      isAdmin.value ? api.get('/companies/') : Promise.resolve({ data: [] }),
    ])
    trips.value = tripsRes.data
    selectedTripIds.value = selectedTripIds.value.filter(id =>
      trips.value.some(t => t.id === id)
    )
    cars.value = carsRes.data
    companies.value = companiesRes.data
  } finally {
    loading.value = false
  }
}
async function deleteTrip(id) {
  const ok = await ask({
    title: 'Delete Duty Slip',
    message: 'Are you sure you want to delete this duty slip? This cannot be undone.',
    confirmLabel: 'Delete',
  })
  if (!ok) return
  await api.delete(`/trips/${id}/`)
  trips.value = trips.value.filter(t => t.id !== id)
  selectedTripIds.value = selectedTripIds.value.filter(tripId => tripId !== id)
  notify('Duty Slip deleted.')
}

async function onTripSaved() {
  await fetchTrips()
  notify('Duty Slip updated successfully.')
}

onMounted(fetchTrips)
</script>

<style scoped>
.print-only {
  display: none;
}

.trips-print {
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
