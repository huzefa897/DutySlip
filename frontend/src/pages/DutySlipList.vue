<template>
  <div
    class="page"
    :class="{ 'page--selection-active': selectionMode }"
  >
    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Invoices</span>
        <h1 class="page-title">
          Duty Slip invoices
        </h1>
        <p class="page-header__subtitle">
          Search, filter, and manage invoice-ready duty slips.
        </p>
      </div>
      <div class="page-header__actions">
        <template v-if="!selectionMode">
          <button
            class="btn-secondary"
            @click="enterSelectionMode"
          >
            Bulk Print
          </button>
          <button
            class="btn-secondary"
            @click="enterSelectionMode"
          >
            Bulk Excel Export
          </button>
        </template>
        <router-link
          to="/dutyslips/create"
          class="btn-primary"
        >
          + Create Invoice
        </router-link>
      </div>
    </div>

    <section class="section-card">
      <div class="filters-grid">
        <input
          v-model="filters.party_name"
          type="text"
          placeholder="Search party name..."
          class="input"
        >
        <select
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
          v-model="filters.status"
          class="input"
        >
          <option value="">
            All Statuses
          </option>
          <option value="draft">
            Draft
          </option>
          <option value="finalised">
            Finalised
          </option>
        </select>
        <select
          v-model="filters.payment_status"
          class="input"
        >
          <option value="">
            All Payments
          </option>
          <option value="unpaid">
            Pending
          </option>
          <option value="paid">
            Paid
          </option>
        </select>
      </div>

      <div class="filter-summary">
        <p class="filter-count">
          Showing {{ filteredSlips.length }} of {{ slips.length }} invoices
        </p>
        <button
          v-if="isFiltered"
          class="clear-filters"
          @click="clearFilters"
        >
          Clear filters
        </button>
      </div>
    </section>

    <p
      v-if="loading"
      class="empty-text"
    >
      Loading invoices...
    </p>
    <p
      v-else-if="filteredSlips.length === 0"
      class="empty-text"
    >
      No invoices match your filters.
    </p>

    <section
      v-else
      class="card-list"
    >
      <div
        v-for="slip in paginatedSlips"
        :key="slip.id"
        class="slip-card"
        :class="{ 'slip-card--selected': isSelected(slip.id), 'slip-card--selectable': selectionMode }"
      >
        <!-- Clickable body: navigation or selection toggle -->
        <div
          class="slip-card__body"
          @click="selectionMode ? toggleSelect(slip.id) : router.push(`/dutyslips/${slip.id}`)"
        >
          <div class="slip-left">
            <div
              v-if="selectionMode"
              class="slip-checkbox"
              :class="{ 'slip-checkbox--checked': isSelected(slip.id) }"
            />
            <div class="slip-left__text">
              <p class="slip-id">
                INV-{{ formatSlipId(slip.id) }}
              </p>
              <p class="slip-party">
                {{ slip.party_name }}
              </p>
              <div class="slip-meta-row">
                <p class="slip-meta">
                  {{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}
                </p>
                <StatusBadge :status="slip.status" />
                <PaymentStatusBadge :status="slip.payment_status" />
                <span
                  v-if="slip.slip_type === 'outstation'"
                  class="outstation-badge"
                >Outstation</span>
              </div>
            </div>
          </div>
          <div class="slip-totals">
            <p class="slip-amount">
              {{ currencySymbol }}{{ slip.grand_total }}
            </p>
            <p class="slip-entries">
              {{ slip.entries?.length ?? 0 }} line items
            </p>
          </div>
        </div>
        <!-- Actions: outside the clickable body entirely -->
        <RowActionMenu
          v-if="!selectionMode"
          :show-print="true"
          @edit="router.push(`/dutyslips/${slip.id}`)"
          @delete="deleteSlip(slip)"
          @print="downloadSlipPdf(slip)"
        />
      </div>
    </section>

    <div
      v-if="selectionMode"
      class="selection-bar"
    >
      <span class="selection-bar__count">{{ selectedIds.length }} selected</span>
      <div class="selection-bar__actions">
        <button
          class="btn-secondary"
          @click="selectAll"
        >
          Select All
        </button>
        <button
          class="btn-secondary"
          :disabled="selectedIds.length === 0 || printingBulk"
          @click="bulkPrint"
        >
          {{ printingBulk ? 'Printing…' : `Print (${selectedIds.length})` }}
        </button>
        <button
          class="btn-primary"
          :disabled="selectedIds.length === 0 || exportingBulk"
          @click="bulkExportExcel"
        >
          {{ exportingBulk ? 'Exporting…' : `Export Excel (${selectedIds.length})` }}
        </button>
        <button
          class="btn-secondary"
          @click="exitSelectionMode"
        >
          Cancel
        </button>
      </div>
    </div>

    <div
      v-if="filteredSlips.length > 0"
      class="pagination-row"
    >
      <p class="pagination-info">
        Showing {{ pageStart }}-{{ pageEnd }} of {{ filteredSlips.length }}
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
import { useRouter } from 'vue-router'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import StatusBadge from '../components/StatusBadge.vue'
import PaymentStatusBadge from '../components/PaymentStatusBadge.vue'
import { usePagination } from '../composables/usePagination'
import { useConfirm } from '../composables/useConfirm'
import { notify } from '../store/notification'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import RowActionMenu from '../components/RowActionMenu.vue'

const router = useRouter()

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

async function deleteSlip(slip) {
  const ok = await ask({
    title: `Delete "${slip.party_name}"`,
    message: `This will permanently delete duty slip ${formatSlipId(slip.id)} and unassign all its entries. This cannot be undone.`,
    confirmLabel: 'Delete',
  })
  if (!ok) return
  try {
    await api.delete(`/dutyslips/${slip.id}/`)
    slips.value = slips.value.filter(s => s.id !== slip.id)
    notify(`Duty slip ${formatSlipId(slip.id)} deleted.`)
  } catch {
    notify('Failed to delete duty slip.', 'error')
  }
}

async function downloadSlipPdf(slip) {
  try {
    const response = await api.get(`/dutyslips/${slip.id}/pdf/`, { responseType: 'blob' })
    const blobUrl = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `invoice-${formatSlipId(slip.id)}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(blobUrl)
  } catch {
    notify('Failed to download PDF.', 'error')
  }
}

const slips        = ref([])
const companies    = ref([])
const loading      = ref(true)
const selectionMode  = ref(false)
const selectedIds    = ref([])
const exportingBulk  = ref(false)
const printingBulk   = ref(false)

function isSelected(id) { return selectedIds.value.includes(id) }

function toggleSelect(id) {
  if (isSelected(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

function selectAll() {
  selectedIds.value = filteredSlips.value.map(s => s.id)
}

function enterSelectionMode() { selectionMode.value = true }

function exitSelectionMode() {
  selectionMode.value = false
  selectedIds.value = []
}

async function bulkPrint() {
  if (selectedIds.value.length === 0) return
  printingBulk.value = true
  try {
    const response = await api.post(
      '/dutyslips/bulk-pdf/',
      { ids: selectedIds.value },
      { responseType: 'blob' },
    )
    const blobUrl = window.URL.createObjectURL(response.data)
    const w = window.open(blobUrl, '_blank')
    if (!w) {
      notify('Allow pop-ups to open the combined PDF.', 'error')
      window.URL.revokeObjectURL(blobUrl)
      return
    }
    setTimeout(() => window.URL.revokeObjectURL(blobUrl), 60_000)
  } catch {
    notify('Failed to generate combined PDF.', 'error')
  } finally {
    printingBulk.value = false
  }
}

async function bulkExportExcel() {
  if (selectedIds.value.length === 0) return
  exportingBulk.value = true
  try {
    const response = await api.post(
      '/dutyslips/bulk-excel/',
      { ids: selectedIds.value },
      { responseType: 'blob' },
    )
    const blobUrl = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = blobUrl
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    link.download = `invoices-export-${today}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(blobUrl)
  } catch {
    notify('Failed to export Excel.', 'error')
  } finally {
    exportingBulk.value = false
  }
}

const filters = ref({ party_name: '', company: '', status: '', payment_status: '' })

const isFiltered = computed(() => Object.values(filters.value).some(v => v !== ''))

const filteredSlips = computed(() =>
  slips.value.filter(s => {
    if (filters.value.party_name &&
        !s.party_name.toLowerCase().includes(filters.value.party_name.toLowerCase())) return false
    if (filters.value.company && s.company !== filters.value.company) return false
    if (filters.value.status && s.status !== filters.value.status) return false
    if (filters.value.payment_status &&
        s.payment_status !== filters.value.payment_status) return false
    return true
  })
)

function clearFilters() {
  filters.value = { party_name: '', company: '', status: '', payment_status: '' }
}

const {
  paginated: paginatedSlips,
  currentPage,
  totalPages,
  pageStart,
  pageEnd,
  hasPrev,
  hasNext,
  goToPage,
  prevPage,
  nextPage,
} = usePagination(filteredSlips)

async function fetchData() {
  try {
    const [slipsRes, companiesRes] = await Promise.all([
      api.get('/dutyslips/'),
      api.get('/companies/'),
    ])
    slips.value     = slipsRes.data
    companies.value = companiesRes.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
