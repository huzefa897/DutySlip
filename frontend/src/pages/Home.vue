<template>
  <div>

    <!-- Hero -->
    <div class="mb-10">
      <h1 class="text-3xl font-mono font-bold text-white tracking-tight">
        Welcome back<span class="text-amber-400">.</span>
      </h1>
      <p class="text-gray-500 text-sm font-mono mt-2">
        {{ today }} · {{ bizName }}
      </p>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">Duty Slips</p>
        <p class="text-3xl font-mono font-bold text-white">{{ stats.totalSlips }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">Total Entries</p>
        <p class="text-3xl font-mono font-bold text-white">{{ stats.totalEntries }}</p>
      </div>
      <div class="bg-gray-900 border border-gray-800 rounded-lg p-5">
        <p class="text-xs font-mono text-gray-500 uppercase tracking-wider mb-2">Total Revenue</p>
        <p class="text-3xl font-mono font-bold text-amber-400">
          {{ currencySymbol }}{{ stats.totalRevenue }}
        </p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="mb-10">
      <h2 class="text-xs font-mono text-gray-500 uppercase tracking-wider mb-3">Quick Actions</h2>
      <div class="flex flex-wrap gap-3">
        <router-link
          to="/entries/create"
          class="bg-amber-400 text-gray-950 text-sm font-bold px-5 py-2.5 rounded hover:bg-amber-300 transition-colors"
        >
          + New Entry
        </router-link>
        <router-link
          to="/dutyslips/create"
          class="bg-gray-800 border border-gray-700 text-white text-sm font-bold px-5 py-2.5 rounded hover:bg-gray-700 transition-colors"
        >
          + New Duty Slip
        </router-link>
      </div>
    </div>

    <!-- Recent Duty Slips + Recent Entries side by side -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

      <!-- Recent Duty Slips -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-mono text-gray-500 uppercase tracking-wider">Recent Duty Slips</h2>
          <router-link to="/dutyslips" class="text-xs text-amber-400 hover:text-amber-300 font-mono transition-colors">
            View all →
          </router-link>
        </div>

        <p v-if="recentSlips.length === 0" class="text-gray-600 text-sm">No duty slips yet.</p>

        <div class="space-y-2">
          <router-link
            v-for="slip in recentSlips"
            :key="slip.id"
            :to="`/dutyslips/${slip.id}`"
            class="flex items-center justify-between bg-gray-900 border border-gray-800 rounded p-4 hover:border-amber-400/40 transition-colors"
          >
            <div>
              <p class="text-white text-sm font-medium">{{ slip.party_name }}</p>
              <p class="text-gray-500 text-xs font-mono mt-0.5">
                {{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-amber-400 font-mono font-bold text-sm">
                {{ currencySymbol }}{{ slip.grand_total }}
              </p>
              <p class="text-gray-600 text-xs font-mono mt-0.5">
                {{ slip.entries?.length ?? 0 }} entries
              </p>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Recent Entries -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-xs font-mono text-gray-500 uppercase tracking-wider">Recent Entries</h2>
          <router-link to="/entries" class="text-xs text-amber-400 hover:text-amber-300 font-mono transition-colors">
            View all →
          </router-link>
        </div>

        <p v-if="recentEntries.length === 0" class="text-gray-600 text-sm">No entries yet.</p>

        <div class="space-y-2">
          <div
            v-for="entry in recentEntries"
            :key="entry.id"
            class="flex items-center justify-between bg-gray-900 border border-gray-800 rounded p-4"
          >
            <div>
              <p class="text-white text-sm font-medium">{{ entry.party_name }}</p>
              <p class="text-gray-500 text-xs font-mono mt-0.5">
                {{ entry.date }} · {{ entry.car_name }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-amber-400 font-mono font-bold text-sm">
                {{ currencySymbol }}{{ entry.row_total }}
              </p>
              <p class="text-xs font-mono mt-0.5">
                <span
                  v-if="entry.duty_slip"
                  class="text-green-500"
                >assigned</span>
                <span v-else class="text-gray-600">unassigned</span>
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'

const allSlips = ref([])
const allEntries = ref([])
const bizName = ref('')

const today = new Date().toLocaleDateString('en-AU', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

const recentSlips = computed(() => allSlips.value.slice(0, 5))
const recentEntries = computed(() => allEntries.value.slice(0, 5))

const stats = computed(() => {
  const totalRevenue = allSlips.value
    .reduce((sum, s) => sum + parseFloat(s.grand_total || 0), 0)
    .toFixed(2)
  return {
    totalSlips: allSlips.value.length,
    totalEntries: allEntries.value.length,
    totalRevenue,
  }
})

onMounted(async () => {
  const [slipsRes, entriesRes, settingsRes] = await Promise.all([
    api.get('/dutyslips/'),
    api.get('/entries/'),
    api.get('/settings/'),
  ])
  allSlips.value = slipsRes.data
  allEntries.value = entriesRes.data
  bizName.value = settingsRes.data?.name || ''
})
</script>