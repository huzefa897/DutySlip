<template>
  <div>
    <div class="flex items-center justify-between mb-6">
        <button
          @click="$router.back()"
          class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
        >
          ← Back
        </button>
      <h1 class="text-xl font-mono font-bold text-white">Entries</h1>
      <router-link
        to="/entries/create"
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
      >
        + New Entry
      </router-link>
    </div>

    <!-- Loading -->
    <p v-if="loading" class="text-gray-500 text-sm">Loading...</p>

    <!-- Empty -->
    <p v-else-if="entries.length === 0" class="text-gray-500 text-sm">
      No entries yet. Create your first one.
    </p>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-gray-800 text-gray-400 text-left">
            <th class="py-3 pr-4 font-mono font-normal">Date</th>
            <th class="py-3 pr-4 font-mono font-normal">Party</th>
            <th class="py-3 pr-4 font-mono font-normal">Company</th>
            <th class="py-3 pr-4 font-mono font-normal">Car</th>
            <th class="py-3 pr-4 font-mono font-normal">KMs</th>
            <th class="py-3 pr-4 font-mono font-normal">Hrs</th>
            <th class="py-3 pr-4 font-mono font-normal">Row Total</th>
            <th class="py-3 pr-4 font-mono font-normal">Duty Slip</th>
            <th class="py-3 font-mono font-normal"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="entry in entries"
            :key="entry.id"
            class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
          >
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.date }}</td>
            <td class="py-3 pr-4 text-white">{{ entry.party_name }}</td>
            <td class="py-3 pr-4 text-gray-300">{{ entry.company_name }}</td>
            <td class="py-3 pr-4 text-gray-300">{{ entry.car_name }}</td>
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.total_kms }}</td>
            <td class="py-3 pr-4 font-mono text-gray-300">{{ entry.extra_hrs }}h extra</td>
            <td class="py-3 pr-4 font-mono text-amber-400">{{ currencySymbol }}{{ entry.row_total }}</td>
            <td class="py-3 pr-4">
              <span
                v-if="entry.duty_slip"
                class="text-xs bg-green-900 text-green-400 px-2 py-1 rounded font-mono"
              >
                #{{ entry.duty_slip }}
              </span>
              <span v-else class="text-xs text-gray-600 font-mono">unassigned</span>
            </td>
            <td class="py-3">
              <button
                @click="deleteEntry(entry.id)"
                class="text-xs text-red-500 hover:text-red-400 transition-colors"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'

const entries = ref([])
const loading = ref(true)

async function fetchEntries() {
  try {
    const res = await api.get('/entries/')
    entries.value = res.data
  } finally {
    loading.value = false
  }
}

async function deleteEntry(id) {
  if (!confirm('Delete this entry?')) return
  await api.delete(`/entries/${id}/`)
  entries.value = entries.value.filter(e => e.id !== id)
}

onMounted(fetchEntries)
</script>