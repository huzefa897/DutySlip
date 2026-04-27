<template>
  <div>
    <div class="page-header">
      <h1 class="title">Duty Slips</h1>
      <router-link to="/dutyslips/create" class="btn-primary">+ New Duty Slip</router-link>
    </div>

    <!-- Filters -->
    <div class="filters-grid">
      <input
        v-model="filters.party_name"
        type="text"
        placeholder="Search party name..."
        class="input"
      />
      <select v-model="filters.company" class="input">
        <option value="">All Companies</option>
        <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <select v-model="filters.status" class="input">
        <option value="">All Statuses</option>
        <option value="draft">Draft</option>
        <option value="finalised">Finalised</option>
        <option value="paid">Paid</option>
      </select>
    </div>

    <!-- Filter summary -->
    <div class="filter-summary">
      <p class="filter-count">
        Showing {{ filteredSlips.length }} of {{ slips.length }} duty slips
      </p>
      <button v-if="isFiltered" @click="clearFilters" class="clear-filters">
        Clear filters ×
      </button>
    </div>

    <p v-if="loading" class="empty-text">Loading...</p>
    <p v-else-if="filteredSlips.length === 0" class="empty-text">No duty slips match your filters.</p>

    <div v-else class="slip-list">
      <router-link
        v-for="slip in paginatedSlips"
        :key="slip.id"
        :to="`/dutyslips/${slip.id}`"
        class="slip-card"
      >
        <div class="slip-card-inner">
          <div class="slip-left">
            <p class="slip-id">{{ formatSlipId(slip.id) }}</p>
            <div class="slip-meta-row">
              <p class="slip-meta">{{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}</p>
              <StatusBadge :status="slip.status" />
              <span v-if="slip.slip_type === 'outstation'" class="outstation-badge">Outstation</span>
            </div>
            <p class="slip-party">{{ slip.party_name }}</p>
          </div>
          <div class="slip-right">
            <div class="slip-totals">
              <p class="slip-amount">{{ currencySymbol }}{{ slip.grand_total }}</p>
              <p class="slip-entries">{{ slip.entries?.length ?? 0 }} entries</p>
            </div>
            <button @click="deleteSlip(slip, $event)" class="btn-delete">Delete</button>
          </div>
        </div>
      </router-link>
    </div>

    <!-- Load More -->
    <div v-if="hasMore" class="load-more-row">
      <button @click="loadMore" class="btn-load-more">
        Load more ({{ remaining }} remaining)
      </button>
    </div>

    <p v-else-if="paginatedSlips.length > 10" class="all-loaded">
      All {{ filteredSlips.length }} duty slips loaded
    </p>

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
import StatusBadge from '../components/StatusBadge.vue'
import { usePagination } from '../composables/usePagination'
import { useConfirm } from '../composables/useConfirm'
import { notify } from '../store/notification'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

async function deleteSlip(slip, e) {
  e.preventDefault()
  e.stopPropagation()
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
  } catch (e) {
    notify('Failed to delete duty slip.', 'error')
  }
}

const slips     = ref([])
const companies = ref([])
const loading   = ref(true)

const filters = ref({ party_name: '', company: '', status: '' })

const isFiltered = computed(() => Object.values(filters.value).some(v => v !== ''))

const filteredSlips = computed(() =>
  slips.value.filter(s => {
    if (filters.value.party_name &&
        !s.party_name.toLowerCase().includes(filters.value.party_name.toLowerCase())) return false
    if (filters.value.company && s.company !== filters.value.company) return false
    if (filters.value.status && s.status !== filters.value.status) return false
    return true
  })
)

function clearFilters() {
  filters.value = { party_name: '', company: '', status: '' }
}

const { paginated: paginatedSlips, hasMore, remaining, loadMore } = usePagination(filteredSlips)

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

<style scoped>
/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.title {
  font-family: monospace;
  font-size: 1.25rem;
  font-weight: 700;
  color: #ffffff;
}

.btn-primary {
  background-color: #fbbf24;
  color: #030712;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #fcd34d;
}

/* Filters */
.filters-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .filters-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.input {
  background-color: #111827;
  border: 1px solid #1f2937;
  border-radius: 0.25rem;
  padding: 0.5rem 0.75rem;
  color: #ffffff;
  font-size: 0.875rem;
  font-family: monospace;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
  width: 100%;
}

.input::placeholder {
  color: #4b5563;
}

.input:focus {
  border-color: #fbbf24;
}

/* Filter summary */
.filter-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.filter-count {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6b7280;
}

.clear-filters {
  background: none;
  border: none;
  font-family: monospace;
  font-size: 0.75rem;
  color: #fbbf24;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.clear-filters:hover {
  color: #fcd34d;
}

.empty-text {
  color: #6b7280;
  font-size: 0.875rem;
}

/* Slip list */
.slip-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.slip-card {
  display: block;
  background-color: #111827;
  border: 1px solid #1f2937;
  border-radius: 0.25rem;
  padding: 1rem;
  text-decoration: none;
  transition: border-color 0.2s;
  position: relative;
}

.slip-card:hover {
  border-color: rgba(251, 191, 36, 0.5);
}

.slip-card-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.slip-left {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.slip-id {
  font-family: monospace;
  font-size: 0.75rem;
  color: rgba(251, 191, 36, 0.7);
}

.slip-meta-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.125rem;
}

.slip-meta {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6b7280;
}

.outstation-badge {
  font-family: monospace;
  font-size: 0.75rem;
  background-color: #1e3a5f;
  color: #93c5fd;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

.slip-party {
  color: #ffffff;
  font-weight: 500;
  font-size: 0.9375rem;
}

.slip-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.slip-totals {
  text-align: right;
}

.slip-amount {
  font-family: monospace;
  font-weight: 700;
  color: #fbbf24;
}

.slip-entries {
  font-family: monospace;
  font-size: 0.75rem;
  color: #4b5563;
  margin-top: 0.25rem;
}

.btn-delete {
  background: none;
  border: none;
  font-size: 0.75rem;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
  transition: color 0.2s;
}

.btn-delete:hover {
  color: #f87171;
}

/* Load more */
.load-more-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1.5rem;
}

.btn-load-more {
  background-color: #111827;
  border: 1px solid #1f2937;
  color: #9ca3af;
  font-family: monospace;
  font-size: 0.875rem;
  padding: 0.625rem 1.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
}

.btn-load-more:hover {
  color: #ffffff;
  border-color: #4b5563;
}

.all-loaded {
  text-align: center;
  font-family: monospace;
  font-size: 0.75rem;
  color: #4b5563;
  margin-top: 1.5rem;
}
</style>