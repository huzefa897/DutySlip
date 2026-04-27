<template>
    <div class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" @click.self="$emit('close')">
        <div class="bg-gray-900 border border-gray-800 rounded-lg w-full max-w-xl max-h-[90vh] overflow-y-auto">

            <!-- Modal Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
                <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider">
                    {{ props.entry ? 'Edit Entry' : 'New Entry' }}
                </h2>

                <button @click="$emit('close')"
                    class="text-gray-500 hover:text-white transition-colors text-xl leading-none">
                    ×
                </button>
            </div>

            <!-- Form -->
            <form @submit.prevent="submit" class="px-6 py-5 space-y-4">

                <!-- Party Name — readonly if passed in -->
                <!-- Party Name -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Party Name</label>
                    <AutocompleteInput v-model="form.party_name" :suggestions="partyNames" :readonly="!!partyName"
                        placeholder="Enter or select party name" required />
                </div>

                <!-- Company — readonly if passed in -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Company</label>
                    <select v-model="form.company" required :disabled="!!companyId"
                        class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400 disabled:opacity-60">
                        <option value="" disabled>Select company</option>
                        <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>
                </div>

                <!-- Date -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Date</label>
                    <input v-model="form.date" type="date" required
                        class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                </div>
                <!-- Entry Type -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Entry Type</label>
                    <div class="flex gap-2">
                        <button type="button" @click="form.entry_type = 'regular'"
                            class="flex-1 py-2 text-xs font-mono rounded border transition-colors" :class="form.entry_type === 'regular'
                                ? 'bg-amber-400 border-amber-400 text-gray-950 font-bold'
                                : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'">
                            Regular
                        </button>
                        <button type="button" @click="form.entry_type = 'outstation'"
                            class="flex-1 py-2 text-xs font-mono rounded border transition-colors" :class="form.entry_type === 'outstation'
                                ? 'bg-blue-500 border-blue-500 text-white font-bold'
                                : 'bg-gray-800 border-gray-700 text-gray-400 hover:border-gray-500'">
                            Outstation
                        </button>
                    </div>
                </div>

                <!-- Car -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Car</label>
                    <select v-model="form.car" required
                        class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
                        <option value="" disabled>Select car</option>
                        <option v-for="c in cars" :key="c.id" :value="c.id">
                            {{ c.name }} — {{ currencySymbol }}{{ c.base_rate }} base
                        </option>
                    </select>

                    <!-- Override indicator -->
                    <div v-if="rateOverride"
                        class="mt-2 flex items-start gap-2 bg-amber-400/10 border border-amber-400/30 rounded px-3 py-2">
                        <span class="text-amber-400 text-xs mt-0.5">⚡</span>
                        <div class="text-xs font-mono text-amber-300 space-y-0.5">
                            <p class="font-bold text-amber-400">Custom rates applied for this company</p>
                            <p v-if="rateOverride.base_rate">
                                Base: {{ currencySymbol }}{{ rateOverride.base_rate }}
                            </p>
                            <p v-if="rateOverride.extra_km_rate">
                                Extra KM: {{ currencySymbol }}{{ rateOverride.extra_km_rate }}/km
                            </p>
                            <p v-if="rateOverride.extra_hr_rate">
                                Extra HR: {{ currencySymbol }}{{ rateOverride.extra_hr_rate }}/hr
                            </p>
                        </div>
                    </div>
                </div>
                <!-- KMs -->
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">Start KMs</label>
                        <input v-model="form.start_kms" type="number" step="0.01" required
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">End KMs</label>
                        <input v-model="form.end_kms" type="number" step="0.01" required
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                </div>

                <!-- Times — regular only -->
                <div v-if="form.entry_type === 'regular'" class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">Start Time</label>
                        <input v-model="form.start_time" type="time" :required="form.entry_type === 'regular'"
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">End Time</label>
                        <input v-model="form.end_time" type="time" :required="form.entry_type === 'regular'"
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                </div>
                <!-- Outstation rate info -->
                <div v-if="form.entry_type === 'outstation' && rateOverride?.outstation_rate"
                    class="mt-2 flex items-start gap-2 bg-blue-400/10 border border-blue-400/30 rounded px-3 py-2">
                    <span class="text-blue-400 text-xs mt-0.5">⚡</span>
                    <div class="text-xs font-mono text-blue-300">
                        <p class="font-bold text-blue-400">Custom outstation rate applied</p>
                        <p>{{ currencySymbol }}{{ rateOverride.outstation_rate }}/km</p>
                    </div>
                </div>

                <!-- Charges -->
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">Driver Bhatta ($)</label>
                        <input v-model="form.driver_bhatta" type="number" step="0.01"
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                    <div>
                        <label class="block text-xs text-gray-400 font-mono mb-1">Parking ($)</label>
                        <input v-model="form.parking" type="number" step="0.01"
                            class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                    </div>
                </div>

                <!-- Notes -->
                <div>
                    <label class="block text-xs text-gray-400 font-mono mb-1">Notes (optional)</label>
                    <textarea v-model="form.notes" rows="2"
                        class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
                </div>

                <!-- Error -->
                <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

                <!-- Actions -->
                <div class="flex gap-3 pt-2">
                    <button type="submit" :disabled="submitting"
                        class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50">
                        {{ submitting ? 'Saving...' : props.entry ? 'Save Changes' : 'Save Entry' }}
                    </button>
                    <button type="button" @click="$emit('close')"
                        class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors">
                        Cancel
                    </button>
                </div>

            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import AutocompleteInput from './AutoCompleteInput.vue'
// ── 1. Props first ────────────────────────────────────────────
const props = defineProps({
    partyName: String,
    companyId: Number,
    dutySlipId: Number,
    entry: Object,
})

const emit = defineEmits(['close', 'saved'])

// ── 2. Refs ───────────────────────────────────────────────────
const cars = ref([])
const companies = ref([])
const submitting = ref(false)
const error = ref('')
const rateOverride = ref(null)

// ── 3. Form (needs props, so must come after defineProps) ─────
const form = ref({
    party_name: props.entry?.party_name || props.partyName || '',
    company: props.entry?.company || props.companyId || '',
    date: props.entry?.date || '',
    car: props.entry?.car || '',
    start_kms: props.entry?.start_kms || '',
    end_kms: props.entry?.end_kms || '',
    start_time: props.entry?.start_time || '',
    end_time: props.entry?.end_time || '',
    driver_bhatta: props.entry?.driver_bhatta || '0',
    parking: props.entry?.parking || '0',
    entry_type: props.entry?.entry_type || 'regular',
    notes: props.entry?.notes || '',
})

// ── 4. Watch (needs form, so must come after form ref) ────────
watch(
    () => [form.value.company, form.value.car],
    async ([companyId, carId]) => {
        rateOverride.value = null
        if (!companyId || !carId) return
        try {
            const res = await api.get(`/companies/${companyId}/rates/`)
            const match = res.data.find(r => r.car === carId)
            rateOverride.value = match || null
        } catch {
            rateOverride.value = null
        }
    }
)
const partyNames = ref([])

watch(
    () => form.value.company,
    async (companyId) => {
        partyNames.value = []
        if (!companyId) return
        try {
            const res = await api.get(`/companies/${companyId}/parties/`)
            partyNames.value = res.data
        } catch {
            partyNames.value = []
        }
    },
    { immediate: true } // ← run on mount too if company is pre-filled
)
// ── 5. Functions ──────────────────────────────────────────────
async function submit() {
    submitting.value = true
    error.value = ''
    try {
        let res
        if (props.entry) {
            res = await api.put(`/entries/${props.entry.id}/`, form.value)
        } else {
            const payload = { ...form.value }
            if (props.dutySlipId) payload.duty_slip = props.dutySlipId
            res = await api.post('/entries/', payload)
        }
        emit('saved', res.data)
        emit('close')
    } catch (e) {
        error.value = e.response?.data
            ? Object.values(e.response.data).flat().join(' ')
            : 'Something went wrong'
    } finally {
        submitting.value = false
    }
}

// ── 6. Lifecycle ──────────────────────────────────────────────
onMounted(async () => {
    const [carsRes, companiesRes] = await Promise.all([
        api.get('/cars/'),
        api.get('/companies/'),
    ])
    cars.value = carsRes.data
    companies.value = companiesRes.data

    // check override on load if editing an existing entry
    if (props.entry?.company && props.entry?.car) {
        try {
            const res = await api.get(`/companies/${props.entry.company}/rates/`)
            const match = res.data.find(r => r.car === props.entry.car)
            rateOverride.value = match || null
        } catch {
            rateOverride.value = null
        }
    }
})
</script>