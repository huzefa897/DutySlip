<template>
  <div class="page">
    <button
      class="back-btn"
      @click="$router.back()"
    >
      ← Back
    </button>
    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Cars</span>
        <h1 class="page-title">
          Fleet pricing
        </h1>
      </div>
      <button
        class="btn-primary"
        @click="openCreate"
      >
        + New Car
      </button>
    </div>

    <p
      v-if="loading"
      class="empty-text"
    >
      Loading...
    </p>

    <p
      v-else-if="cars.length === 0"
      class="empty-text"
    >
      No cars yet. Add your first one.
    </p>

    <section
      v-else
      class="table-card"
    >
      <div class="table-shell">
        <table class="data-table">
          <thead>
            <tr>
              <th>
                Name
              </th>
              <th>
                Base Rate
              </th>
              <th>
                Extra KM Rate
              </th>
              <th>
                Extra Hr Rate
              </th>
              <th>
                Outstation Rate
              </th>
              <th class="data-table__actions" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="car in cars"
              :key="car.id"
            >
              <td>
                {{ car.name }}
              </td>
              <td class="data-table__numeric data-table__accent">
                {{ currencySymbol }}{{ car.base_rate }}
              </td>
              <td class="data-table__numeric data-table__muted">
                {{ currencySymbol }}{{ car.extra_km_rate }}/km
              </td>
              <td class="data-table__numeric data-table__muted">
                {{ currencySymbol }}{{ car.extra_hr_rate }}/hr
              </td>
              <td class="data-table__numeric data-table__muted">
                {{ currencySymbol }}{{ car.outstation_rate }}/km
              </td>
              <td class="data-table__actions">
                <div class="data-table__actions-group data-table__actions-group--compact">
                  <RowActionMenu
                    @edit="openEdit(car)"
                    @delete="deleteCar(car)"
                  />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Modal -->
    <div
      v-if="showModal"
      class="modal-overlay"
      @click.self="closeModal"
    >
      <div class="modal-card">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ editingCar ? 'Edit Car' : 'New Car' }}
          </h2>
          <button
            class="btn-cancel text-xl leading-none"
            @click="closeModal"
          >
            ×
          </button>
        </div>

        <form
          class="modal-body form"
          @submit.prevent="submit"
        >
          <div class="field">
            <label class="label">Car Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="e.g. Ute, Camry, HiAce"
              class="field-control"
            >
          </div>

          <div class="field">
            <label class="label">Base Rate ({{ currencySymbol }})</label>
            <input
              v-model="form.base_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 100.00"
              class="field-control"
            >
          </div>

          <div class="field">
            <label class="label">Extra KM Rate ({{ currencySymbol }} per km over 80)</label>
            <input
              v-model="form.extra_km_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 1.20"
              class="field-control"
            >
          </div>

          <div class="field">
            <label class="label">Extra Hour Rate ({{ currencySymbol }} per hr over 8)</label>
            <input
              v-model="form.extra_hr_rate"
              type="number"
              step="0.01"
              required
              placeholder="e.g. 12.00"
              class="field-control"
            >
          </div>
          <div class="field">
            <label class="label">Outstation Rate ({{ currencySymbol }} per km)</label>
            <input
              v-model="form.outstation_rate"
              type="number"
              step="0.01"
              placeholder="e.g. 2.00"
              class="field-control"
            >
          </div>

          <p
            v-if="error"
            class="error"
          >
            {{ error }}
          </p>

          <div class="actions">
            <button
              type="submit"
              :disabled="submitting"
              class="btn-primary"
            >
              {{ submitting ? 'Saving...' : editingCar ? 'Save Changes' : 'Create Car' }}
            </button>
            <button
              type="button"
              class="btn-cancel px-2 py-2"
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
import RowActionMenu from '../components/RowActionMenu.vue'

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
