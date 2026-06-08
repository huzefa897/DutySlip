<template>
  <div
    v-if="slip"
    class="page"
  >
    <div class="no-print page">
      <button
        class="back-btn"
        @click="$router.back()"
      >
        ← Back
      </button>
      <div class="page-header">
        <div class="page-header__content">
          <span class="page-header__eyebrow">Invoice {{ formatSlipId(slip.id) }}</span>
          <h1 class="page-title">
            {{ slip.party_name }}
          </h1>
          <p class="page-header__subtitle">
            {{ slip.company_name }} · Created {{ slip.created_at?.slice(0, 10) }}
          </p>
          <div class="slip-meta-row">
            <StatusBadge :status="slip.status" />
            <select
              :value="slip.status"
              class="field-control px-3 py-2 text-xs"
              @change="updateStatus($event.target.value)"
            >
              <option value="draft">
                Draft
              </option>
              <option value="finalised">
                Finalised
              </option>
            </select>
            <PaymentStatusBadge :status="slip.payment_status" />
            <select
              :value="slip.payment_status"
              class="field-control px-3 py-2 text-xs"
              @change="updatePaymentStatus($event.target.value)"
            >
              <option value="unpaid">
                Unpaid
              </option>
              <option value="paid">
                Paid
              </option>
            </select>
          </div>
        </div>
        <div class="quick-actions-row">
          <button
            type="button"
            class="btn-secondary"
            :disabled="downloadingPdf"
            @click="downloadInvoicePdf"
          >
            {{ downloadingPdf ? 'Preparing PDF...' : 'Download PDF' }}
          </button>
          <button
            type="button"
            class="btn-secondary"
            :disabled="downloadingExcel"
            @click="downloadInvoiceExcel"
          >
            {{ downloadingExcel ? 'Preparing Excel...' : 'Export Excel' }}
          </button>
          <button
            class="btn-secondary"
            @click="printInvoice"
          >
            Print Invoice
          </button>
          <button
            v-if="slip.payment_status !== 'paid'"
            class="btn-primary"
            @click="updatePaymentStatus('paid')"
          >
            Mark Paid
          </button>
          <button
            class="btn-danger"
            @click="deleteSlip"
          >
            Delete
          </button>
        </div>
      </div>

      <div class="summary-grid">
        <div class="summary-card">
          <p class="summary-card__label">
            Total
          </p>
          <p class="summary-card__value summary-card__value--accent">
            {{ currencySymbol }}{{ slip.grand_total }}
          </p>
        </div>
        <div class="summary-card">
          <p class="summary-card__label">
            Status
          </p>
          <div class="mt-3">
            <StatusBadge :status="slip.status" />
          </div>
        </div>
        <div class="summary-card">
          <p class="summary-card__label">
            Created Date
          </p>
          <p class="summary-card__value">
            {{ slip.created_at?.slice(0, 10) }}
          </p>
        </div>
      </div>

      <section class="page">
        <div class="flex items-center justify-between mb-3">
          <h2 class="section-label">
            Invoice Items
          </h2>
          <button
            class="btn-primary"
            @click="showModal = true"
          >
            + Add Entry
          </button>
        </div>

        <p
          v-if="slip.entries?.length === 0"
          class="empty-text"
        >
          No entries yet — add one above.
        </p>

        <InvoiceItemsTable
          v-else
          :entries="slip.entries"
          :grand-total="slip.grand_total"
          :currency-symbol="currencySymbol"
          :get-base-rate="getBaseRate"
          :get-rate-label="getRateLabel"
          @edit="openEntryEditor"
          @delete="deleteEntry"
        />
      </section>

      <section
        v-if="unassigned.length > 0"
        class="section-card"
      >
        <div class="flex items-center justify-between mb-3">
          <h2 class="section-label">
            Unassigned Entries for {{ slip.party_name }}
          </h2>
          <button
            :disabled="selected.length === 0"
            class="btn-secondary"
            @click="bulkAssign"
          >
            Assign Selected ({{ selected.length }})
          </button>
        </div>
        <p class="upload-hint mb-3">
          Only {{ slip.slip_type }} entries are shown here so this invoice stays type-specific.
        </p>
        <div class="selection-list">
          <label
            v-for="entry in unassigned"
            :key="entry.id"
            class="selection-item"
          >
            <input
              v-model="selected"
              type="checkbox"
              :value="entry.id"
              class="accent-[var(--accent-blue)]"
            >
            <span class="data-table__muted">
              {{ entry.date }} · {{ entry.car_name }} · {{ currencySymbol }}{{ entry.row_total }}
            </span>
          </label>
        </div>
      </section>
    </div>


    <!-- ── PRINT / INVOICE VIEW ───────────────────────────────────── -->
    <div class="print-only invoice">
      <!-- Invoice Header -->
      <!-- Invoice Header -->
      <!-- Letterhead -->
      <div class="letterhead">
        <div class="letterhead-left">
          <div class="letterhead-brand">
            <img
              :src="bizSettings?.logo ? `${mediaUrl}${bizSettings.logo}` : defaultLogoPath"
              class="letterhead-logo"
              alt="Logo"
            >
            <h1 class="letterhead-name">
              {{ bizSettings?.name }}
            </h1>
          </div>
          <div class="letterhead-details">
            <p class="letterhead-detail">
              {{ bizSettings?.address }}
            </p>
            <p class="letterhead-detail">
              {{ bizSettings?.phone }} · {{ bizSettings?.email }}
            </p>
            <p class="letterhead-detail">
              ABN: {{ bizSettings?.abn }}
            </p>
          </div>
        </div>
        <div class="invoice-title-block">
          <h2 class="invoice-title">
            INVOICE
          </h2>
          <p class="invoice-meta">
            Date: {{ today }}
          </p>
          <p class="invoice-meta">
            Ref: #{{ formatSlipId(slip.id) }}
          </p>
          <p
            class="invoice-status"
            :class="statusPrintClass"
          >
            {{ slip.status?.toUpperCase() }}
          </p>
          <p
            class="invoice-status"
            :class="paymentStatusPrintClass"
          >
            PAYMENT: {{ slip.payment_status?.toUpperCase() }}
          </p>
        </div>
      </div>
      <!-- Party Info -->
      <div class="invoice-party">
        <p class="invoice-label">
          Billed To
        </p>
        <p class="invoice-party-name">
          {{ slip.party_name }}
        </p>
      </div>

      <!-- Entries Table -->
      <table class="invoice-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Trip Type</th>
            <th>Vehicle</th>
            <th>Total Hrs</th>
            <th>Extra Hrs</th>
            <th>Total KMs</th>
            <th>Extra KMs</th>
            <th>Bhatta</th>
            <th>Parking</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in slip.entries"
            :key="entry.id"
          >
            <td>{{ entry.date }}</td>
            <td>{{ formatTripType(entry) }}</td>
            <td>{{ entry.car_name }}</td>
            <td>{{ formatTotalHrs(entry) }}</td>
            <td>{{ entry.extra_hrs }}</td>
            <td>{{ entry.total_kms }}</td>
            <td>{{ entry.extra_kms }}</td>
            <td>{{ currencySymbol }}{{ entry.driver_bhatta }}</td>
            <td>{{ currencySymbol }}{{ entry.parking }}</td>
            <td>{{ currencySymbol }}{{ entry.row_total }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td
              colspan="9"
              class="grand-total-label"
            >
              GRAND TOTAL
            </td>
            <td class="grand-total-value">
              {{ currencySymbol }}{{ slip.grand_total }}
            </td>
          </tr>
        </tfoot>
      </table>

      <!-- Footer -->
      <div class="invoice-footer">
        <p>Thank you for your business.</p>
      </div>
    </div>
    <!-- ── END PRINT VIEW ─────────────────────────────────────────── -->
  </div>

  <p
    v-else
    class="text-gray-500 text-sm"
  >
    Loading...
  </p>

  <!-- Modal -->
  <EntryFormModal
    v-if="showModal"
    :party-name="slip?.party_name"
    :company-id="slip?.company"
    :duty-slip-id="slip?.id"
    :locked-entry-type="slip?.slip_type"
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
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import EntryFormModal from '../components/EntryFormModal.vue'
import InvoiceItemsTable from '../components/InvoiceItemsTable.vue'
import { notify } from '../store/notification'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import StatusBadge from '../components/StatusBadge.vue'
import PaymentStatusBadge from '../components/PaymentStatusBadge.vue'
import { useRouter } from 'vue-router'
import { useConfirm } from '../composables/useConfirm'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const router = useRouter()

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
  confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

async function deleteSlip() {
  const ok = await ask({
    title: `Delete "${slip.value.party_name}"`,
    message: `This will permanently delete duty slip ${formatSlipId(slip.value.id)} and unassign all its entries. This cannot be undone.`,
    confirmLabel: 'Delete',
  })
  if (!ok) return

  try {
    await api.delete(`/dutyslips/${route.params.id}/`)
    notify('Duty slip deleted.')
    router.push('/dutyslips')
  } catch {
    notify('Failed to delete duty slip.', 'error')
  }
}
const statusPrintClass = computed(() => {
  const map = {
    draft:      'color: #888',
    finalised:  'color: #3b82f6',
  }
  return map[slip.value?.status] || ''
})
const paymentStatusPrintClass = computed(() => {
  const map = {
    unpaid: 'color: #d97706',
    paid:   'color: #22c55e',
  }
  return map[slip.value?.payment_status] || ''
})
const mediaUrl = import.meta.env.VITE_MEDIA_URL || ''
const apiUrl = import.meta.env.VITE_API_URL || '/api'
const defaultLogoPath = '/invoicely-mark.svg'
const editingEntry = ref(null)
const route = useRoute()
const slip = ref(null)
const unassigned = ref([])
const selected = ref([])
const showModal = ref(false)
const cars = ref([])
const companyRates = ref([])
const bizSettings = ref(null)
const downloadingPdf = ref(false)
const downloadingExcel = ref(false)

const today = new Date().toLocaleDateString('en-AU', {
  day: '2-digit', month: 'long', year: 'numeric'
})
const resolvedCurrencySymbol = computed(() => currencySymbol.value)

function getBaseRate(carId) {
  const car = cars.value.find(c => c.id === carId)
  const override = companyRates.value.find(rate => String(rate.car) === String(carId))
  if (override?.base_rate != null && override.base_rate !== '') return override.base_rate
  return car ? car.base_rate : '—'
}

function getExtraKmRate(carId) {
  const car = cars.value.find(c => c.id === carId)
  const override = companyRates.value.find(rate => String(rate.car) === String(carId))
  if (override?.extra_km_rate != null && override.extra_km_rate !== '') return override.extra_km_rate
  return car ? car.extra_km_rate : '—'
}

function getOutstationRate(carId) {
  const car = cars.value.find(c => c.id === carId)
  const override = companyRates.value.find(rate => String(rate.car) === String(carId))
  if (override?.outstation_rate != null && override.outstation_rate !== '') return override.outstation_rate
  return car ? car.outstation_rate : '—'
}

function getRateLabel(entry) {
  if (entry.entry_type === 'outstation') {
    return `${resolvedCurrencySymbol.value}${getOutstationRate(entry.car)}/km`
  }
  return `${resolvedCurrencySymbol.value}${getExtraKmRate(entry.car)}/km`
}

function formatTotalHrs(entry) {
  if (!entry.start_time || !entry.end_time) return '—'

  const [startHours, startMinutes = '0', startSeconds = '0'] = String(entry.start_time).split(':')
  const [endHours, endMinutes = '0', endSeconds = '0'] = String(entry.end_time).split(':')
  const start = new Date(0, 0, 0, Number(startHours), Number(startMinutes), Number(startSeconds))
  const end = new Date(0, 0, 0, Number(endHours), Number(endMinutes), Number(endSeconds))
  if (end < start) end.setDate(end.getDate() + 1)
  const totalHours = (end - start) / 36e5
  return Number.isInteger(totalHours) ? String(totalHours) : totalHours.toFixed(2)
}

function formatTripType(entry) {
  return entry.entry_type === 'outstation' ? 'Outstation Trip' : 'Regular Trip'
}

function openEntryEditor(entry) {
  editingEntry.value = entry
  showModal.value = true
}

function escapeHtml(value) {
  return String(value ?? '—')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function buildInvoiceHtml() {
  const symbol = resolvedCurrencySymbol.value
  const logoUrl = bizSettings.value?.logo ? `${mediaUrl}${bizSettings.value.logo}` : defaultLogoPath
  const rows = (slip.value?.entries || []).map(entry => `
    <tr>
      <td>${escapeHtml(entry.date)}</td>
      <td>${escapeHtml(formatTripType(entry))}</td>
      <td>${escapeHtml(entry.car_name)}</td>
      <td>${escapeHtml(formatTotalHrs(entry))}</td>
      <td>${escapeHtml(entry.extra_hrs)}</td>
      <td>${escapeHtml(entry.total_kms)}</td>
      <td>${escapeHtml(entry.extra_kms)}</td>
      <td>${escapeHtml(`${symbol}${entry.driver_bhatta}`)}</td>
      <td>${escapeHtml(`${symbol}${entry.parking}`)}</td>
      <td>${escapeHtml(`${symbol}${entry.row_total}`)}</td>
    </tr>
  `).join('')

  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>Invoice ${escapeHtml(formatSlipId(slip.value.id))}</title>
      <style>
        body { font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #111; margin: 0; padding: 32px; background: #fff; }
        .letterhead { display: flex; justify-content: space-between; align-items: flex-start; gap: 24px; margin-bottom: 28px; padding-bottom: 18px; border-bottom: 2px solid #111; }
        .letterhead-brand { display: flex; align-items: center; gap: 12px; }
        .letterhead-logo { max-height: 52px; max-width: 52px; object-fit: contain; }
        .letterhead-name { margin: 0; font-size: 22px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; }
        .letterhead-detail, .invoice-meta { margin: 2px 0; font-size: 11px; color: #555; }
        .invoice-title-block { text-align: right; }
        .invoice-title { margin: 0; font-size: 28px; font-weight: 700; letter-spacing: 4px; }
        .invoice-status { margin-top: 6px; font-size: 11px; font-weight: 600; letter-spacing: 2px; text-transform: uppercase; }
        .invoice-party { margin-bottom: 24px; }
        .invoice-label { margin: 0 0 4px; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #888; }
        .invoice-party-name { margin: 0; font-size: 16px; font-weight: 700; }
        .invoice-table { width: 100%; border-collapse: collapse; font-size: 11px; }
        .invoice-table th { background: #111; color: #fff; padding: 8px 6px; text-align: left; font-weight: 500; white-space: nowrap; }
        .invoice-table td { padding: 7px 6px; border-bottom: 1px solid #ddd; white-space: nowrap; }
        .invoice-table tbody tr:nth-child(even) td { background: #f9f9f9; }
        .grand-total-label { text-align: right; font-weight: 700; font-size: 12px; letter-spacing: 1px; padding-right: 12px; border-top: 2px solid #111; padding-top: 10px; }
        .grand-total-value { font-weight: 700; font-size: 14px; border-top: 2px solid #111; padding-top: 10px; }
        .invoice-footer { text-align: center; font-size: 11px; color: #888; border-top: 1px solid #ddd; padding-top: 16px; margin-top: 16px; }
        .pdf-watermark {
          position: fixed;
          left: 0;
          right: 0;
          bottom: 8px;
          text-align: center;
          font-size: 8px;
          letter-spacing: 0.18em;
          text-transform: uppercase;
          color: rgba(17, 17, 17, 0.38);
          pointer-events: none;
        }
        @page { size: A4 landscape; margin: 14mm; }
      </style>
    </head>
    <body>
      <div class="letterhead">
        <div>
          <div class="letterhead-brand">
            ${logoUrl ? `<img src="${escapeHtml(logoUrl)}" class="letterhead-logo" alt="Logo">` : ''}
            <h1 class="letterhead-name">${escapeHtml(bizSettings.value?.name || '')}</h1>
          </div>
          <p class="letterhead-detail">${escapeHtml(bizSettings.value?.address || '')}</p>
          <p class="letterhead-detail">${escapeHtml(bizSettings.value?.phone || '')} ${bizSettings.value?.email ? `· ${escapeHtml(bizSettings.value.email)}` : ''}</p>
          <p class="letterhead-detail">ABN: ${escapeHtml(bizSettings.value?.abn || '')}</p>
        </div>
        <div class="invoice-title-block">
          <h2 class="invoice-title">INVOICE</h2>
          <p class="invoice-meta">Date: ${escapeHtml(today)}</p>
          <p class="invoice-meta">Ref: #${escapeHtml(formatSlipId(slip.value.id))}</p>
          <p class="invoice-status">${escapeHtml(slip.value.status?.toUpperCase())}</p>
          <p class="invoice-status">PAYMENT: ${escapeHtml(slip.value.payment_status?.toUpperCase())}</p>
        </div>
      </div>
      <div class="invoice-party">
        <p class="invoice-label">Billed To</p>
        <p class="invoice-party-name">${escapeHtml(slip.value.party_name)}</p>
      </div>
      <table class="invoice-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Trip Type</th>
            <th>Vehicle</th>
            <th>Total Hrs</th>
            <th>Extra Hrs</th>
            <th>Total KMs</th>
            <th>Extra KMs</th>
            <th>Bhatta</th>
            <th>Parking</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
        <tfoot>
          <tr>
            <td colspan="9" class="grand-total-label">GRAND TOTAL</td>
            <td class="grand-total-value">${escapeHtml(`${symbol}${slip.value.grand_total}`)}</td>
          </tr>
        </tfoot>
      </table>
      <div class="invoice-footer"><p>Thank you for your business.</p></div>
      <div class="pdf-watermark">Created with Invoicely</div>
    </body>
  </html>`
}

async function deleteEntry(id) {
  const ok = await ask({
    title: 'Delete Entry',
    message: 'Are you sure you want to delete this entry? This cannot be undone.',
    confirmLabel: 'Delete',
  })
  if (!ok) return

  try {
    await api.delete(`/entries/${id}/`)
    await fetchSlip()
    await fetchUnassigned()
    notify('Entry deleted.')
  } catch {
    notify('Failed to delete entry.', 'error')
  }
}

function printInvoice() {
  const printWindow = window.open('', '_blank', 'width=1200,height=900')
  if (!printWindow) {
    notify('Popup blocked. Allow popups to print the invoice.', 'error')
    return
  }

  printWindow.document.open()
  printWindow.document.write(buildInvoiceHtml())
  printWindow.document.close()
  printWindow.focus()
  printWindow.onload = () => {
    printWindow.print()
  }
}

async function downloadInvoicePdf() {
  downloadingPdf.value = true
  try {
    const response = await fetch(`${apiUrl}/dutyslips/${slip.value.id}/pdf/`)
    if (!response.ok) throw new Error('Failed to download PDF')
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `invoice-${formatSlipId(slip.value.id)}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(blobUrl)
  } catch {
    notify('Failed to download PDF.', 'error')
  } finally {
    downloadingPdf.value = false
  }
}
async function downloadInvoiceExcel() {
  downloadingExcel.value = true
  try {
    const response = await fetch(`${apiUrl}/dutyslips/${slip.value.id}/excel/`)
    if (!response.ok) throw new Error('Failed to export Excel')
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `invoice-${formatSlipId(slip.value.id)}.xlsx`
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(blobUrl)
  } catch {
    notify('Failed to export Excel.', 'error')
  } finally {
    downloadingExcel.value = false
  }
}
async function updateStatus(newStatus) {
  await api.patch(`/dutyslips/${route.params.id}/status/`, { status: newStatus })
  await fetchSlip()
  notify(`Status updated to ${newStatus}.`)
}
async function updatePaymentStatus(newStatus) {
  await api.patch(`/dutyslips/${route.params.id}/payment-status/`, {
    payment_status: newStatus,
  })
  await fetchSlip()
  notify(`Payment status updated to ${newStatus}.`)
}
async function fetchSlip() {
  const res = await api.get(`/dutyslips/${route.params.id}/`)
  slip.value = res.data
  if (slip.value?.company) {
    const ratesRes = await api.get(`/companies/${slip.value.company}/rates/`)
    companyRates.value = ratesRes.data
  } else {
    companyRates.value = []
  }
}

async function fetchUnassigned() {
  const res = await api.get('/entries/')
  unassigned.value = res.data.filter(
    e => !e.duty_slip && e.party_name === slip.value.party_name && e.entry_type === slip.value.slip_type
  )
}

async function bulkAssign() {
  if (selected.value.length === 0) return
  await api.post(`/dutyslips/${route.params.id}/assign/`, {
    entry_ids: selected.value
  })
  selected.value = []
  await fetchSlip()
  await fetchUnassigned()
  notify(`${selected.value.length + 1} entries assigned.`)
}

async function onEntrySaved() {
  await fetchSlip()
  await fetchUnassigned()
  notify('Entry saved.')
}

onMounted(async () => {
  const carsRes = await api.get('/cars/')
  cars.value = carsRes.data
  await fetchSlip()
  await fetchUnassigned()
  const bizRes = await api.get('/settings/')
  bizSettings.value = bizRes.data
})
</script>

<style scoped>
/* ── Hide print view on screen ── */
.print-only {
  display: none;
}

/* ── Hide screen view when printing ── */
@media print {
  .no-print {
    display: none !important;
  }

  .print-only {
    display: block !important;
  }
}

/* ── Invoice Styles ── */

.invoice {
  font-family: 'Montserrat', sans-serif;
  color: #111;
  padding: 40px;
  max-width: 100%;
}

.invoice-status {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 2px;
  margin-top: 6px;
  text-transform: uppercase;
}

.invoice-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid #111;
}

.invoice-company {
  font-size: 22px;
  font-weight: bold;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.invoice-from {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.invoice-logo {
  max-height: 70px;
  max-width: 200px;
  object-fit: contain;
  margin-bottom: 8px;
}

.invoice-detail {
  font-size: 11px;
  color: #444;
}

.invoice-party-sub {
  font-size: 13px;
  color: #444;
  margin-top: 2px;
}

.invoice-abn {
  font-size: 12px;
  color: #555;
  margin-top: 4px;
}

.invoice-title-block {
  text-align: right;
}

.invoice-title {
  font-size: 28px;
  font-weight: bold;
  letter-spacing: 4px;
  color: #111;
}

.invoice-meta {
  font-size: 12px;
  color: #555;
  margin-top: 4px;
}

.invoice-party {
  margin-bottom: 24px;
}

.invoice-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #888;
  margin-bottom: 4px;
}

.invoice-party-name {
  font-size: 16px;
  font-weight: bold;
}

.invoice-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  margin-bottom: 32px;
}

.invoice-table th {
  background: #111;
  color: #fff;
  padding: 8px 6px;
  text-align: left;
  font-weight: normal;
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.invoice-table td {
  padding: 7px 6px;
  border-bottom: 1px solid #ddd;
  white-space: nowrap;
}

.invoice-table tbody tr:nth-child(even) td {
  background: #f9f9f9;
}

.no-print .invoice-table td {
  background: #030712;
  border-bottom: 1px solid #1f2937;
  color: #d1d5db;
}

.no-print .invoice-table tbody tr:nth-child(even) td {
  background: #020617;
}

.no-print .invoice-table tbody tr:nth-child(odd) td {
  background: #030712;
}

.grand-total-label {
  text-align: right;
  font-weight: bold;
  font-size: 12px;
  letter-spacing: 1px;
  padding-right: 12px;
  border-top: 2px solid #111;
  padding-top: 10px;
}

.grand-total-value {
  font-weight: bold;
  font-size: 14px;
  border-top: 2px solid #111;
  padding-top: 10px;
}

.invoice-footer {
  text-align: center;
  font-size: 11px;
  color: #888;
  border-top: 1px solid #ddd;
  padding-top: 16px;
  margin-top: 16px;
}

.letterhead {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 2px solid #111;
}

.letterhead-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.letterhead-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.letterhead-logo {
  max-height: 52px;
  max-width: 52px;
  object-fit: contain;
}

.letterhead-name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #111;
  margin: 0;
}

.letterhead-details {
  padding-left: 4px;
}

.letterhead-detail {
  font-size: 11px;
  color: #555;
  margin: 2px 0;
}
</style>
