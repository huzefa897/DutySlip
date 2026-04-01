<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-mono font-bold text-white">Duty Slips</h1>
      <router-link
        to="/dutyslips/create"
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
      >
        + New Duty Slip
      </router-link>
    </div>

    <!-- Filters -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
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
        v-model="filters.status"
        class="bg-gray-900 border border-gray-800 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
      >
        <option value="">All Statuses</option>
        <option value="draft">Draft</option>
        <option value="finalised">Finalised</option>
        <option value="paid">Paid</option>
      </select>
    </div>

    <!-- Filter summary -->
    <div class="flex items-center justify-between mb-4">
      <p class="text-xs font-mono text-gray-500">
        Showing {{ filteredSlips.length }} of {{ slips.length }} duty slips
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

    <p v-else-if="filteredSlips.length === 0" class="text-gray-500 text-sm">
      No duty slips match your filters.
    </p>

    <div v-else class="space-y-3">
      <router-link
        v-for="slip in filteredSlips"
        :key="slip.id"
        :to="`/dutyslips/${slip.id}`"
        class="block bg-gray-900 border border-gray-800 rounded p-4 hover:border-amber-400/50 transition-colors"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs font-mono text-amber-400/70 mb-0.5">{{ formatSlipId(slip.id) }}</p>
            <p class="text-white font-medium">{{ slip.party_name }}</p>
            <div class="flex items-center gap-2 mt-1">
              <p class="text-gray-500 text-xs font-mono">
                {{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}
              </p>
              <StatusBadge :status="slip.status" />
            </div>
          </div>
          <div class="text-right">
            <p class="text-amber-400 font-mono font-bold">
              {{ currencySymbol }}{{ slip.grand_total }}
            </p>
            <p class="text-gray-600 text-xs font-mono mt-1">
              {{ slip.entries?.length ?? 0 }} entries
            </p>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import StatusBadge from '../components/StatusBadge.vue'

const slips = ref([])
const companies = ref([])
const loading = ref(true)

const filters = ref({
  party_name: '',
  company: '',
  status: '',
})

const isFiltered = computed(() =>
  Object.values(filters.value).some(v => v !== '')
)

const filteredSlips = computed(() => {
  return slips.value.filter(s => {
    if (filters.value.party_name &&
      !s.party_name.toLowerCase().includes(filters.value.party_name.toLowerCase()))
      return false
    if (filters.value.company && s.company !== filters.value.company)
      return false
    if (filters.value.status && s.status !== filters.value.status)
      return false
    return true
  })
})

function clearFilters() {
  filters.value = { party_name: '', company: '', status: '' }
}

async function fetchData() {
  try {
    const [slipsRes, companiesRes] = await Promise.all([
      api.get('/dutyslips/'),
      api.get('/companies/'),
    ])
    slips.value = slipsRes.data
    companies.value = companiesRes.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)
</script>
