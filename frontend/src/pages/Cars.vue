<template>
  <div>
    <button
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
      @click="$router.back()"
    >
      ← Back
    </button>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-mono font-bold text-white">
        Cars
      </h1>
      <button
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
        @click="openCreate"
      >
        + New Car
      </button>
    </div>

    <p
      v-if="loading"
      class="text-gray-500 text-sm"
    >
      Loading...
    </p>

    <p
      v-else-if="cars.length === 0"
      class="text-gray-500 text-sm"
    >
      No cars yet. Add your first one.
    </p>

    <div
      v-else
      class="overflow-x-auto"
    >
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-gray-800 text-gray-400 text-left">
            <th class="py-3 pr-6 font-mono font-normal">
              Name
            </th>
            <th class="py-3 pr-6 font-mono font-normal">
              Base Rate
            </th>
            <th class="py-3 pr-6 font-mono font-normal">
              Extra KM Rate
            </th>
            <th class="py-3 pr-6 font-mono font-normal">
              Extra Hr Rate
            </th>
            <th class="py-3 pr-6 font-mono font-normal">
              Outstation Rate
            </th>

            <th class="py-3 font-mono font-normal" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="car in cars"
            :key="car.id"
            class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
          >
            <td class="py-3 pr-6 text-white font-medium">
              {{ car.name }}
            </td>
            <td class="py-3 pr-6 font-mono text-amber-400">
              {{ currencySymbol }}{{ car.base_rate }}
            </td>
            <td class="py-3 pr-6 font-mono text-gray-300">
              {{ currencySymbol }}{{ car.extra_km_rate }}/km
            </td>
            <td class="py-3 pr-6 font-mono text-gray-300">
              {{ currencySymbol }}{{ car.extra_hr_rate }}/hr
            </td>
            <td class="py-3 pr-6 font-mono text-gray-300">
              {{ currencySymbol }}{{ car.outstation_rate }}/km
            </td>
            <td class="py-3 flex items-center gap-4">
              <button
                class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                @click="openEdit(car)"
              >
                Edit
              </button>
              <button
                class="text-xs text-red-500 hover:text-red-400 transition-colors"
                @click="deleteCar(car)"
              >
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4"
      @click.self="closeModal"
    >
      <div class="bg-gray-900 border border-gray-800 rounded-lg w-full max-w-md">
        <!-- Modal Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <h2 class="text-sm font-mono font-bold text-white uppercase tracking-wider">
            {{ editingCar ? 'Edit Car' : 'New Car' }}
          </h2>
          <button
            class="text-gray-500 hover:text-white transition-colors text-xl leading-none"
            @click="closeModal"
          >
            ×
          </button>
        </div>

        <!-- Form -->
        <form
          class="px-6 py-5 space-y-4"
          @submit.prevent="submit"
        >
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Car Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="e.g. Ute, Camry, HiAce"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            >
          </div>

          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Base Rate ($)</label>
            <input
              v-model="form.base_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 100.00"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            >
          </div>

          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Extra KM Rate ($ per km over 80)</label>
            <input
              v-model="form.extra_km_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 1.20"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            >
          </div>

          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Extra Hour Rate ($ per hr over 8)</label>
            <input
              v-model="form.extra_hr_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 12.00"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            >
          </div>
          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Outstation Rate ($ per km)</label>
            <input
              v-model="form.outstation_rate"
              type="number"
              step="0.01"
              placeholder="e.g. 2.00"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            >
          </div>

          <p
            v-if="error"
            class="text-red-400 text-sm"
          >
            {{ error }}
          </p>

          <div class="flex gap-3 pt-2">
            <button
              type="submit"
              :disabled="submitting"
              class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50"
            >
              {{ submitting ? 'Saving...' : editingCar ? 'Save Changes' : 'Create Car' }}
            </button>
            <button
              type="button"
              class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors"
              @click="closeModal"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
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
import { ref, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { notify } from '../store/notification'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
  confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const cars = ref([])
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)
const error = ref('')
const editingCar = ref(null)

const form = ref({
  name: '',
  base_rate: '',
  extra_km_rate: '',
  extra_hr_rate: '',
  outstation_rate: '',
})

async function fetchCars() {
  try {
    const res = await api.get('/cars/')
    cars.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingCar.value = null
  form.value = { name: '', base_rate: '', extra_km_rate: '', extra_hr_rate: '', outstation_rate: '' }
  error.value = ''
  showModal.value = true
}
function openEdit(car) {
  editingCar.value = car
  form.value = {
    name: car.name,
    base_rate: car.base_rate,
    extra_km_rate: car.extra_km_rate,
    extra_hr_rate: car.extra_hr_rate,
    outstation_rate: car.outstation_rate,
  }
  error.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingCar.value = null
  error.value = ''
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    if (editingCar.value) {
      const res = await api.put(`/cars/${editingCar.value.id}/`, form.value)
      const idx = cars.value.findIndex(c => c.id === editingCar.value.id)
      cars.value[idx] = res.data
      notify('Car updated successfully.')
    } else {
      const res = await api.post('/cars/', form.value)
      cars.value.push(res.data)
      notify('Car created successfully.')
    }
    closeModal()
  } catch (e) {
    const msg = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : 'Something went wrong'
    error.value = msg
  } finally {
    submitting.value = false
  }
}

async function deleteCar(car) {
  const ok = await ask({
    title: `Delete "${car.name}"`,
    message: `This will permanently delete the ${car.name}. This cannot be undone.`,
    confirmLabel: 'Delete',
  })
  if (!ok) return
  try {
    await api.delete(`/cars/${car.id}/`)
    cars.value = cars.value.filter(c => c.id !== car.id)
    notify(`"${car.name}" deleted.`)
  } catch (e) {
    notify(e.response?.data?.error || 'Cannot delete — car is used in existing entries.', 'error')
  }
}

onMounted(fetchCars)
</script>