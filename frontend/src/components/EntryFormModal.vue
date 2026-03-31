<template>
  <div
    class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
    @click.self="$emit('close')"
  >
    <div class="bg-gray-900 border border-gray-800 rounded-lg w-full max-w-xl max-h-[90vh] overflow-y-auto">

      <!-- Modal Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
        <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider">
          New Entry
        </h2>
        <button @click="$emit('close')" class="text-gray-500 hover:text-white transition-colors text-xl leading-none">
          ×
        </button>
      </div>

      <!-- Form -->
      <form @submit.prevent="submit" class="px-6 py-5 space-y-4">

        <!-- Party Name — readonly if passed in -->
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Party Name</label>
          <input
            v-model="form.party_name"
            type="text"
            required
            :readonly="!!partyName"
            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 read-only:opacity-60"
          />
        </div>

        <!-- Company — readonly if passed in -->
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Company</label>
          <select
            v-model="form.company"
            required
            :disabled="!!companyId"
            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 disabled:opacity-60"
          >
            <option value="" disabled>Select company</option>
            <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
          </select>
        </div>

        <!-- Date -->
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Date</label>
          <input
            v-model="form.date"
            type="date"
            required
            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
          />
        </div>

        <!-- Car -->
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Car</label>
          <select
            v-model="form.car"
            required
            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
          >
            <option value="" disabled>Select car</option>
            <option v-for="c in cars" :key="c.id" :value="c.id">
              {{ c.name }} — ${{ c.base_rate }} base
            </option>
          </select>
        </div>

        <!-- KMs -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Start KMs</label>
            <input
              v-model="form.start_kms"
              type="number" step="0.01" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">End KMs</label>
            <input
              v-model="form.end_kms"
              type="number" step="0.01" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        <!-- Times -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Start Time</label>
            <input
              v-model="form.start_time"
              type="time" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">End Time</label>
            <input
              v-model="form.end_time"
              type="time" required
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        <!-- Charges -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Driver Bhatta ($)</label>
            <input
              v-model="form.driver_bhatta"
              type="number" step="0.01"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Parking ($)</label>
            <input
              v-model="form.parking"
              type="number" step="0.01"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>
        </div>

        <!-- Notes -->
        <div>
          <label class="block text-xs text-gray-400 font-mono mb-1">Notes (optional)</label>
          <textarea
            v-model="form.notes"
            rows="2"
            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
          />
        </div>

        <!-- Error -->
        <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

        <!-- Actions -->
        <div class="flex gap-3 pt-2">
          <button
            type="submit"
            :disabled="submitting"
            class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50"
          >
            {{ submitting ? 'Saving...' : 'Save Entry' }}
          </button>
          <button
            type="button"
            @click="$emit('close')"
            class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors"
          >
            Cancel
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const props = defineProps({
  partyName: String,   // pre-filled if opened from duty slip
  companyId: Number,   // pre-filled if opened from duty slip
  dutySlipId: Number,  // if set, entry is assigned on creation
})

const emit = defineEmits(['close', 'saved'])

const cars = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')

const form = ref({
  party_name: props.partyName || '',
  company: props.companyId || '',
  date: '',
  car: '',
  start_kms: '',
  end_kms: '',
  start_time: '',
  end_time: '',
  driver_bhatta: '0',
  parking: '0',
  notes: '',
})

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const payload = { ...form.value }
    if (props.dutySlipId) payload.duty_slip = props.dutySlipId
    const res = await api.post('/entries/', payload)
    emit('saved', res.data)
    emit('close')
  } catch (e) {
    error.value = JSON.stringify(e.response?.data || 'Something went wrong')
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const [carsRes, companiesRes] = await Promise.all([
    api.get('/cars/'),
    api.get('/companies/'),
  ])
  cars.value = carsRes.data
  companies.value = companiesRes.data
})
</script>