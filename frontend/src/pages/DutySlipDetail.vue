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
          <a
            :href="`${apiUrl}/dutyslips/${slip.id}/pdf/`"
            target="_blank"
            download
            class="btn-secondary"
          >
            Download PDF
          </a>
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

        <section
          v-else
          class="table-card"
        >
          <div class="table-shell">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Car</th>
                  <th>Start KMs</th>
                  <th>End KMs</th>
                  <th>Total KMs</th>
                  <th>Rate</th>
                  <th>KM Cost</th>
                  <th>Start Time</th>
                  <th>End Time</th>
                  <th>Extra Hrs</th>
                  <th>Extra Hrs Cost</th>
                  <th>Base Rate</th>
                  <th>Bhatta</th>
                  <th>Parking</th>
                  <th>Row Total</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="entry in slip.entries"
                  :key="entry.id"
                >
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.date }}
                  </td>
                  <td>{{ entry.entry_type === 'outstation' ? 'Outstation' : 'Regular' }}</td>
                  <td class="data-table__muted">
                    {{ entry.car_name }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.start_kms }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.end_kms }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.total_kms }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    <span v-if="entry.entry_type === 'outstation'">
                      {{ currencySymbol }}{{ entry.outstation_rate }}/km
                    </span>
                    <span v-else>—</span>
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ currencySymbol }}{{ entry.extra_kms_amount }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.entry_type === 'outstation' ? '—' : entry.start_time }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.entry_type === 'outstation' ? '—' : entry.end_time }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.entry_type === 'outstation' ? '—' : entry.extra_hrs }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.entry_type === 'outstation' ? '—' : `${currencySymbol}${entry.extra_hrs_amount}` }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ entry.entry_type === 'outstation' ? '—' : `${currencySymbol}${getBaseRate(entry.car)}` }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ currencySymbol }}{{ entry.driver_bhatta }}
                  </td>
                  <td class="data-table__numeric data-table__muted">
                    {{ currencySymbol }}{{ entry.parking }}
                  </td>
                  <td class="data-table__numeric data-table__accent">
                    {{ currencySymbol }}{{ entry.row_total }}
                  </td>
                </tr>
              </tbody>
              <tfoot>
                <tr>
                  <td
                    colspan="15"
                    class="data-table__actions"
                  >
                    GRAND TOTAL
                  </td>
                  <td class="data-table__numeric data-table__accent">
                    {{ currencySymbol }}{{ slip.grand_total }}
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        </section>
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
              v-if="bizSettings?.logo"
              :src="`${mediaUrl}${bizSettings.logo}`"
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
            <th>Type</th>
            <th>Car</th>
            <th>Start KMs</th>
            <th>End KMs</th>
            <th>Total KMs</th>
            <th>Extra KMs</th>
            <th>Extra KMs ({{ currencySymbol }})</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Extra Hrs</th>
            <th>Extra Hrs ({{ currencySymbol }})</th>
            <th>Base Rate</th>
            <th>Bhatta</th>
            <th>Parking</th>
            <th>Row Total</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in slip.entries"
            :key="entry.id"
          >
            <td>{{ entry.date }}</td>
            <td>{{ entry.entry_type === 'outstation' ? 'Outstation' : 'Regular' }}</td>
            <td>{{ entry.car_name }}</td>
            <td>{{ entry.start_kms }}</td>
            <td>{{ entry.end_kms }}</td>
            <td>{{ entry.total_kms }}</td>
            <td class="py-3 pr-4 font-mono text-gray-300">
              <span v-if="entry.entry_type === 'outstation'">
                {{ currencySymbol }}{{ entry.outstation_rate }}/km
              </span>
              <span v-else>{{ entry.extra_kms }}</span>
            </td>
            <td>{{ currencySymbol }}{{ entry.extra_kms_amount }}</td>
            <td>{{ entry.start_time }}</td>
            <td>{{ entry.end_time }}</td>
            <td>{{ entry.extra_hrs }}</td>
            <td>{{ currencySymbol }}{{ entry.extra_hrs_amount }}</td>
            <td>{{ currencySymbol }}{{ getBaseRate(entry.car) }}</td>
            <td>{{ currencySymbol }}{{ entry.driver_bhatta }}</td>
            <td>{{ currencySymbol }}{{ entry.parking }}</td>
            <td>{{ currencySymbol }}{{ entry.row_total }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr>
            <td
              colspan="15"
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
const editingEntry = ref(null)
const route = useRoute()
const slip = ref(null)
const unassigned = ref([])
const selected = ref([])
const showModal = ref(false)
const cars = ref([])
const bizSettings = ref(null)

const today = new Date().toLocaleDateString('en-AU', {
  day: '2-digit', month: 'long', year: 'numeric'
})

function getBaseRate(carId) {
  const car = cars.value.find(c => c.id === carId)
  return car ? car.base_rate : '—'
}

function printInvoice() {
  window.print()
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
}

async function fetchUnassigned() {
  const res = await api.get('/entries/')
  unassigned.value = res.data.filter(
    e => !e.duty_slip && e.party_name === slip.value.party_name
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
