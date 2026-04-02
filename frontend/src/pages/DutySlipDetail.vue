<template>
  <div v-if="slip">

    <!-- ── SCREEN VIEW ─────────────────────────────────────────────── -->
    <div class="no-print">
      <button
        @click="$router.back()"
        class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
      >
        ← Back
      </button>
      <!-- Header -->
      <div class="flex items-start justify-between mb-8">
        <div>
          <h1 class="text-xl font-mono font-bold text-white">{{ slip.party_name }}</h1>

          <div class="flex items-center gap-3 mt-2">
  <StatusBadge :status="slip.status" />
  <select
    :value="slip.status"
    @change="updateStatus($event.target.value)"
    class="bg-gray-800 border border-gray-700 text-gray-300 text-xs font-mono px-2 py-1 rounded focus:outline-none focus:border-amber-400"
  >
    <option value="draft">Draft</option>
    <option value="finalised">Finalised</option>
    <option value="paid">Paid</option>
  </select>
</div>
          <p class="text-gray-500 text-sm font-mono mt-1">
            {{ slip.company_name }} · Created {{ slip.created_at?.slice(0, 10) }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <a :href="`${apiUrl}/dutyslips/${slip.id}/pdf/`"

  target="_blank"
  download
  class="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono"
>
  ⬇ Download PDF
</a>

          <div class="flex items-center gap-3">
  <button
    @click="deleteSlip"
    class="bg-red-900/50 border border-red-800 text-red-400 text-sm px-4 py-2 rounded hover:bg-red-900 transition-colors font-mono"
  >
    🗑 Delete
  </button>
  <button
    @click="printInvoice"
    class="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono"
  >
    🖨 Print Invoice
  </button>
</div>
          <div class="text-right">
            <p class="text-xs text-gray-500 font-mono mb-1">Grand Total</p>
            <p class="text-2xl font-mono font-bold text-amber-400">${{ slip.grand_total }}</p>
          </div>
        </div>
      </div>

      <!-- Assigned Entries Table -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-mono text-gray-400 uppercase tracking-wider">Entries</h2>
          <button
            @click="showModal = true"
            class="bg-amber-400 text-gray-950 text-xs font-bold px-3 py-1.5 rounded hover:bg-amber-300 transition-colors"
          >
            + Add Entry
          </button>
        </div>

        <p v-if="slip.entries?.length === 0" class="text-gray-600 text-sm">
          No entries yet — add one above.
        </p>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="border-b border-gray-800 text-gray-400 text-left">
                <th class="py-3 pr-4 font-mono font-normal">Date</th>
                <th class="py-3 pr-4 font-mono font-normal">Car</th>
                <th class="py-3 pr-4 font-mono font-normal">Start KMs</th>
                <th class="py-3 pr-4 font-mono font-normal">End KMs</th>
                <th class="py-3 pr-4 font-mono font-normal">Total KMs</th>
                <th class="py-3 pr-4 font-mono font-normal">Extra KMs</th>
                <th class="py-3 pr-4 font-mono font-normal">Extra Hrs</th>
                <th class="py-3 pr-4 font-mono font-normal">Bhatta</th>
                <th class="py-3 pr-4 font-mono font-normal">Parking</th>
                <th class="py-3 pr-4 font-mono font-normal">Row Total</th>
                <th class="py-3 font-mono font-normal"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                  v-for="entry in sortedEntries"
                :key="entry.id"
                class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
              >
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.date }}</td>
                <td class="py-3 pr-4 text-gray-300">{{ entry.car_name }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.start_kms }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.end_kms }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.total_kms }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.extra_kms }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.extra_hrs }}h</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ currencySymbol }}{{ entry.driver_bhatta }}</td>
                <td class="py-3 pr-4 font-mono text-gray-300">{{ currencySymbol }}{{ entry.parking }}</td>
                <td class="py-3 pr-4 font-mono text-amber-400">{{ currencySymbol }}{{ entry.row_total }}</td>
               <td class="py-3 flex items-center gap-3">
                    <button
                      @click="editingEntry = entry; showModal = true"
                      class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      Edit
                    </button>
                  
                    <button
                    @click="removeEntry(entry.id)"
                    class="text-xs text-red-500 hover:text-red-400 transition-colors"
                  >
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Bulk Assign Unassigned Entries -->
      <div class="border-t border-gray-800 pt-6" v-if="unassigned.length > 0">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-mono text-gray-400 uppercase tracking-wider">
            Unassigned Entries for {{ slip.party_name }}
          </h2>
          <button
            @click="bulkAssign"
            :disabled="selected.length === 0"
            class="bg-gray-700 text-white text-xs font-bold px-3 py-1.5 rounded hover:bg-gray-600 transition-colors disabled:opacity-30"
          >
            Assign Selected ({{ selected.length }})
          </button>
        </div>
        <div class="space-y-2">
          <label
            v-for="entry in unassigned"
            :key="entry.id"
            class="flex items-center gap-3 bg-gray-900 border border-gray-800 rounded px-4 py-3 cursor-pointer hover:border-gray-600 transition-colors"
          >
            <input
              type="checkbox"
              :value="entry.id"
              v-model="selected"
              class="accent-amber-400"
            />
            <span class="font-mono text-sm text-gray-300">
              {{ entry.date }} · {{ entry.car_name }} · {{ currencySymbol }}{{ entry.row_total }}
            </span>
          </label>
        </div>
      </div>

    </div>
    <!-- ── END SCREEN VIEW ─────────────────────────────────────────── -->


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
      />
      <h1 class="letterhead-name">{{ bizSettings?.name }}</h1>
    </div>
    <div class="letterhead-details">
      <p class="letterhead-detail">{{ bizSettings?.address }}</p>
      <p class="letterhead-detail">{{ bizSettings?.phone }} · {{ bizSettings?.email }}</p>
      <p class="letterhead-detail">ABN: {{ bizSettings?.abn }}</p>
    </div>
  </div>
  <div class="invoice-title-block">
    <h2 class="invoice-title">INVOICE</h2>
    <p class="invoice-meta">Date: {{ today }}</p>
    <p class="invoice-meta">Ref: #{{ formatSlipId(slip.id) }}</p>
      <p class="invoice-status" :class="statusPrintClass">{{ slip.status?.toUpperCase() }}</p>
  </div>
</div>

<!-- Billed To -->
<div class="invoice-party">
  <p class="invoice-label">Billed To</p>
  <p class="invoice-party-name">{{ slip.company_name }}</p>
  <p class="invoice-party-sub">{{ slip.party_name }}</p>
</div>

      <!-- Party Info -->
      <div class="invoice-party">
        <p class="invoice-label">Billed To</p>
        <p class="invoice-party-name">{{ slip.party_name }}</p>
      </div>

      <!-- Entries Table -->
      <table class="invoice-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Car</th>
            <th>Start KMs</th>
            <th>End KMs</th>
            <th>Total KMs</th>
            <th>Extra KMs</th>
            <th>Extra KMs ($)</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Extra Hrs</th>
            <th>Extra Hrs ($)</th>
            <th>Base Rate</th>
            <th>Bhatta</th>
            <th>Parking</th>
            <th>Row Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in slip.entries" :key="entry.id">
            <td>{{ entry.date }}</td>
            <td>{{ entry.car_name }}</td>
            <td>{{ entry.start_kms }}</td>
            <td>{{ entry.end_kms }}</td>
            <td>{{ entry.total_kms }}</td>
            <td>{{ entry.extra_kms }}</td>
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
            <td colspan="14" class="grand-total-label">GRAND TOTAL</td>
            <td class="grand-total-value">{{ currencySymbol }}{{ slip.grand_total }}</td>
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

  <p v-else class="text-gray-500 text-sm">Loading...</p>

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
  } catch (e) {
    notify('Failed to delete duty slip.', 'error')
  }
}

const mediaUrl = import.meta.env.VITE_MEDIA_URL || ''
const apiUrl = import.meta.env.VITE_API_URL || '/api'
const editingEntry = ref(null)
const route = useRoute()
const slip = ref(null)
const unassigned = ref([])
const selected = ref([])
const showModal = ref(false)
const companyAbn = ref('')
const cars = ref([])
const bizSettings = ref(null)
const sortedEntries = computed(() => {
  if (!slip.value?.entries) return []
  return [...slip.value.entries].sort((a, b) => new Date(a.date) - new Date(b.date))
})


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
async function fetchSlip() {
  const res = await api.get(`/dutyslips/${route.params.id}/`)
  slip.value = res.data
  // fetch company ABN
  const companyRes = await api.get(`/companies/`)
  const company = companyRes.data.find(c => c.id === res.data.company)
  companyAbn.value = company?.abn || ''
}

async function fetchUnassigned() {
  const res = await api.get('/entries/')
  unassigned.value = res.data.filter(
    e => !e.duty_slip && e.party_name === slip.value.party_name
  )
}

async function removeEntry(entryId) {
  await api.post(`/dutyslips/${route.params.id}/remove/${entryId}/`)
  await fetchSlip()
  await fetchUnassigned()
notify('Entry removed from duty slip.')

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
.print-only { display: none; }

/* ── Hide screen view when printing ── */
@media print {
  .no-print { display: none !important; }
  .print-only { display: block !important; }
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