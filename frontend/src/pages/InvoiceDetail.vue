<template>
  <div
    v-if="invoice"
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
          <span class="page-header__eyebrow">Invoice {{ formatSlipId(invoice.id) }}</span>
          <h1 class="page-title">
            {{ invoice.party_name }}
          </h1>
          <p class="page-header__subtitle">
            {{ invoice.company_name }} · Created {{ invoice.created_at?.slice(0, 10) }}
          </p>
          <div class="slip-meta-row">
            <StatusBadge :status="invoice.status" />
            <select
              v-if="isAdmin"
              :value="invoice.status"
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
            <PaymentStatusBadge :status="invoice.payment_status" />
            <select
              v-if="isAdmin"
              :value="invoice.payment_status"
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
            v-if="isAdmin && invoice.payment_status !== 'paid'"
            class="btn-primary"
            @click="updatePaymentStatus('paid')"
          >
            Mark Paid
          </button>
          <button
            v-if="isAdmin"
            class="btn-danger"
            @click="deleteInvoice"
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
            {{ currencySymbol }}{{ invoice.grand_total }}
          </p>
        </div>
        <div class="summary-card">
          <p class="summary-card__label">
            Status
          </p>
          <div class="mt-3">
            <StatusBadge :status="invoice.status" />
          </div>
        </div>
        <div class="summary-card">
          <p class="summary-card__label">
            Created Date
          </p>
          <p class="summary-card__value">
            {{ invoice.created_at?.slice(0, 10) }}
          </p>
        </div>
      </div>

      <section class="page">
        <div class="flex items-center justify-between mb-3">
          <h2 class="section-label">
            Invoice Items
          </h2>
          <button
            v-if="isAdmin"
            class="btn-primary"
            @click="showModal = true"
          >
            + Add Duty Slip
          </button>
        </div>

        <p
          v-if="invoice.trips?.length === 0"
          class="empty-text"
        >
          No duty slips yet — add one above.
        </p>

        <InvoiceItemsTable
          v-else
          :trips="invoice.trips"
          :grand-total="invoice.grand_total"
          :currency-symbol="currencySymbol"
          :get-base-rate="getBaseRate"
          :get-rate-label="getRateLabel"
          @edit="openTripEditor"
          @delete="deleteTrip"
        />
      </section>

      <section
        v-if="isAdmin && unassigned.length > 0"
        class="section-card"
      >
        <div class="flex items-center justify-between mb-3">
          <h2 class="section-label">
            Unassigned Duty Slips for {{ invoice.party_name }}
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
          Only {{ invoice.invoice_type }} duty slips are shown here so this invoice stays type-specific.
        </p>
        <div class="selection-list">
          <label
            v-for="trip in unassigned"
            :key="trip.id"
            class="selection-item"
          >
            <input
              v-model="selected"
              type="checkbox"
              :value="trip.id"
              class="accent-[var(--accent-blue)]"
            >
            <span class="data-table__muted">
              {{ trip.date }} · {{ trip.car_name }} · {{ currencySymbol }}{{ trip.row_total }}
            </span>
          </label>
        </div>
      </section>
    </div>


    <!-- ── PRINT / INVOICE VIEW ───────────────────────────────────── -->
    <div class="print-only invoice">
      <div class="letterhead">
        <div class="letterhead-left">
          <div class="letterhead-brand">
            <img
              :src="bizSettings?.logo || defaultLogoPath"
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
            Ref: #{{ formatSlipId(invoice.id) }}
          </p>
          <p
            class="invoice-status"
            :class="statusPrintClass"
          >
            {{ invoice.status?.toUpperCase() }}
          </p>
          <p
            class="invoice-status"
            :class="paymentStatusPrintClass"
          >
            PAYMENT: {{ invoice.payment_status?.toUpperCase() }}
          </p>
        </div>
      </div>
      <div class="invoice-party">
        <p class="invoice-label">
          Billed To
        </p>
        <p class="invoice-party-name">
          {{ invoice.party_name }}
        </p>
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
        <tbody>
          <tr
            v-for="trip in invoice.trips"
            :key="trip.id"
          >
            <td>{{ trip.date }}</td>
            <td>{{ formatTripType(trip) }}</td>
            <td>{{ trip.car_name }}</td>
            <td>{{ formatTotalHrs(trip) }}</td>
            <td>{{ trip.extra_hrs }}</td>
            <td>{{ trip.total_kms }}</td>
            <td>{{ trip.extra_kms }}</td>
            <td>{{ currencySymbol }}{{ trip.driver_bhatta }}</td>
            <td>{{ currencySymbol }}{{ trip.parking }}</td>
            <td>{{ currencySymbol }}{{ trip.row_total }}</td>
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
              {{ currencySymbol }}{{ invoice.grand_total }}
            </td>
          </tr>
        </tfoot>
      </table>

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
  <TripFormModal
    v-if="showModal"
    :party-name="invoice?.party_name"
    :company-id="invoice?.company"
    :invoice-id="invoice?.id"
    :locked-trip-type="invoice?.invoice_type"
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
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api'
import TripFormModal from '../components/TripFormModal.vue'
import InvoiceItemsTable from '../components/InvoiceItemsTable.vue'
import { notify } from '../store/notification'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import StatusBadge from '../components/StatusBadge.vue'
import PaymentStatusBadge from '../components/PaymentStatusBadge.vue'
import { useRouter } from 'vue-router'
import { useConfirm } from '../composables/useConfirm'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { isAdmin } from '../store/auth'

const router = useRouter()

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
  confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

async function deleteInvoice() {
  const ok = await ask({
    title: `Delete "${invoice.value.party_name}"`,
    message: `This will permanently delete invoice ${formatSlipId(invoice.value.id)} and unassign all its trips. This cannot be undone.`,
    confirmLabel: 'Delete',
  })
  if (!ok) return

  try {
    await api.delete(`/invoices/${route.params.id}/`)
    notify('Invoice deleted.')
    router.push('/invoices')
  } catch {
    notify('Failed to delete invoice.', 'error')
  }
}
const statusPrintClass = computed(() => {
  const map = {
    draft:      'color: #888',
    finalised:  'color: #3b82f6',
  }
  return map[invoice.value?.status] || ''
})
const paymentStatusPrintClass = computed(() => {
  const map = {
    unpaid: 'color: #d97706',
    paid:   'color: #22c55e',
  }
  return map[invoice.value?.payment_status] || ''
})
const apiUrl = import.meta.env.VITE_API_URL || '/api'
const defaultLogoPath = '/invoicely-mark.svg'
const editingTrip = ref(null)
const route = useRoute()
const invoice = ref(null)
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

function getRateLabel(trip) {
  if (trip.trip_type === 'outstation') {
    return `${resolvedCurrencySymbol.value}${getOutstationRate(trip.car)}/km`
  }
  return `${resolvedCurrencySymbol.value}${getExtraKmRate(trip.car)}/km`
}

function formatTotalHrs(trip) {
  if (!trip.start_time || !trip.end_time) return '—'

  const [startHours, startMinutes = '0', startSeconds = '0'] = String(trip.start_time).split(':')
  const [endHours, endMinutes = '0', endSeconds = '0'] = String(trip.end_time).split(':')
  const start = new Date(0, 0, 0, Number(startHours), Number(startMinutes), Number(startSeconds))
  const end = new Date(0, 0, 0, Number(endHours), Number(endMinutes), Number(endSeconds))
  if (end < start) end.setDate(end.getDate() + 1)
  const totalHours = (end - start) / 36e5
  return Number.isInteger(totalHours) ? String(totalHours) : totalHours.toFixed(2)
}

function formatTripType(trip) {
  return trip.trip_type === 'outstation' ? 'Outstation Trip' : 'Regular Trip'
}

function openTripEditor(trip) {
  editingTrip.value = trip
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
  const logoUrl = bizSettings.value?.logo || defaultLogoPath
  const rows = (invoice.value?.trips || []).map(trip => `
    <tr>
      <td>${escapeHtml(trip.date)}</td>
      <td>${escapeHtml(formatTripType(trip))}</td>
      <td>${escapeHtml(trip.car_name)}</td>
      <td>${escapeHtml(formatTotalHrs(trip))}</td>
      <td>${escapeHtml(trip.extra_hrs)}</td>
      <td>${escapeHtml(trip.total_kms)}</td>
      <td>${escapeHtml(trip.extra_kms)}</td>
      <td>${escapeHtml(`${symbol}${trip.driver_bhatta}`)}</td>
      <td>${escapeHtml(`${symbol}${trip.parking}`)}</td>
      <td>${escapeHtml(`${symbol}${trip.row_total}`)}</td>
    </tr>
  `).join('')

  return `<!doctype html>
  <html>
    <head>
      <meta charset="utf-8">
      <title>Invoice ${escapeHtml(formatSlipId(invoice.value.id))}</title>
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
          <p class="invoice-meta">Ref: #${escapeHtml(formatSlipId(invoice.value.id))}</p>
          <p class="invoice-status">${escapeHtml(invoice.value.status?.toUpperCase())}</p>
          <p class="invoice-status">PAYMENT: ${escapeHtml(invoice.value.payment_status?.toUpperCase())}</p>
        </div>
      </div>
      <div class="invoice-party">
        <p class="invoice-label">Billed To</p>
        <p class="invoice-party-name">${escapeHtml(invoice.value.party_name)}</p>
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
            <td class="grand-total-value">${escapeHtml(`${symbol}${invoice.value.grand_total}`)}</td>
          </tr>
        </tfoot>
      </table>
      <div class="invoice-footer"><p>Thank you for your business.</p></div>
      <div class="pdf-watermark">Created with Invoicely</div>
    </body>
  </html>`
}

async function deleteTrip(id) {
  const ok = await ask({
    title: 'Delete Duty Slip',
    message: 'Are you sure you want to delete this duty slip? This cannot be undone.',
    confirmLabel: 'Delete',
  })
  if (!ok) return

  try {
    await api.delete(`/trips/${id}/`)
    await fetchInvoice()
    await fetchUnassigned()
    notify('Duty Slip deleted.')
  } catch {
    notify('Failed to delete duty slip.', 'error')
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
    const response = await fetch(`${apiUrl}/invoices/${invoice.value.id}/pdf/`)
    if (!response.ok) throw new Error('Failed to download PDF')
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `invoice-${formatSlipId(invoice.value.id)}.pdf`
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
    const response = await fetch(`${apiUrl}/invoices/${invoice.value.id}/excel/`)
    if (!response.ok) throw new Error('Failed to export Excel')
    const blob = await response.blob()
    const blobUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `invoice-${formatSlipId(invoice.value.id)}.xlsx`
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
  await api.patch(`/invoices/${route.params.id}/status/`, { status: newStatus })
  await fetchInvoice()
  notify(`Status updated to ${newStatus}.`)
}
async function updatePaymentStatus(newStatus) {
  await api.patch(`/invoices/${route.params.id}/payment-status/`, {
    payment_status: newStatus,
  })
  await fetchInvoice()
  notify(`Payment status updated to ${newStatus}.`)
}
async function fetchInvoice() {
  const res = await api.get(`/invoices/${route.params.id}/`)
  invoice.value = res.data
  if (invoice.value?.company) {
    const ratesRes = await api.get(`/companies/${invoice.value.company}/rates/`)
    companyRates.value = ratesRes.data
  } else {
    companyRates.value = []
  }
}

async function fetchUnassigned() {
  const res = await api.get('/trips/')
  unassigned.value = res.data.filter(
    t => !t.invoice && t.party_name === invoice.value.party_name && t.trip_type === invoice.value.invoice_type
  )
}

async function bulkAssign() {
  if (selected.value.length === 0) return
  await api.post(`/invoices/${route.params.id}/assign/`, {
    trip_ids: selected.value
  })
  selected.value = []
  await fetchInvoice()
  await fetchUnassigned()
  notify('Duty Slips assigned.')
}

async function onTripSaved() {
  await fetchInvoice()
  await fetchUnassigned()
  notify('Duty Slip saved.')
}

onMounted(async () => {
  const carsRes = await api.get('/cars/')
  cars.value = carsRes.data
  await fetchInvoice()
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
