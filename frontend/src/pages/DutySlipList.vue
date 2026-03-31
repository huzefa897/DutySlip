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

    <p v-if="loading" class="text-gray-500 text-sm">Loading...</p>

    <p v-else-if="slips.length === 0" class="text-gray-500 text-sm">
      No duty slips yet.
    </p>

    <div v-else class="space-y-3">
      <router-link
        v-for="slip in slips"
        :key="slip.id"
        :to="`/dutyslips/${slip.id}`"
        class="block bg-gray-900 border border-gray-800 rounded p-4 hover:border-amber-400/50 transition-colors"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white font-medium">{{ slip.party_name }}</p>
            <p class="text-gray-500 text-xs font-mono mt-1">
              {{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}
            </p>
          </div>
          <div class="text-right">
            <p class="text-amber-400 font-mono font-bold">${{ slip.grand_total }}</p>
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
import { ref, onMounted } from 'vue'
import api from '../api'

const slips = ref([])
const loading = ref(true)

async function fetchSlips() {
  try {
    const res = await api.get('/dutyslips/')
    slips.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(fetchSlips)
</script>