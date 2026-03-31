<template>
  <div class="max-w-2xl">
    <button
      @click="$router.back()"
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
    >
      ← Back
    </button>
    <h1 class="text-xl font-mono font-bold text-white mb-6">New Duty Slip</h1>

    <form @submit.prevent="submit" class="space-y-5">

      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Party Name</label>
        <input v-model="form.party_name" type="text" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Company</label>
        <select v-model="form.company" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
          <option value="" disabled>Select company</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

      <div class="flex gap-3">
        <button type="submit" :disabled="submitting"
          class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50">
          {{ submitting ? 'Creating...' : 'Create Duty Slip' }}
        </button>
        <router-link to="/dutyslips"
          class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
          Cancel
        </router-link>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const companies = ref([])
const submitting = ref(false)
const error = ref('')

const form = ref({ party_name: '', company: '' })

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const res = await api.post('/dutyslips/', form.value)
    router.push(`/dutyslips/${res.data.id}`)
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Something went wrong')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const res = await api.get('/companies/')
  companies.value = res.data
})
</script>