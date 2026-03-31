<template>
  <div>
    <button
      @click="$router.back()"
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
    >
      ← Back
    </button>

    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-mono font-bold text-white">Companies</h1>
      <button
        @click="openCreate"
        class="bg-amber-400 text-gray-950 text-sm font-bold px-4 py-2 rounded hover:bg-amber-300 transition-colors"
      >
        + New Company
      </button>
    </div>

    <p v-if="loading" class="text-gray-500 text-sm">Loading...</p>

    <p v-else-if="companies.length === 0" class="text-gray-500 text-sm">
      No companies yet. Add your first one.
    </p>

    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <thead>
          <tr class="border-b border-gray-800 text-gray-400 text-left">
            <th class="py-3 pr-6 font-mono font-normal">Company Name</th>
            <th class="py-3 pr-6 font-mono font-normal">ABN</th>
            <th class="py-3 font-mono font-normal"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="company in companies"
            :key="company.id"
            class="border-b border-gray-800/50 hover:bg-gray-900 transition-colors"
          >
            <td class="py-3 pr-6 text-white font-medium">{{ company.name }}</td>
            <td class="py-3 pr-6 font-mono text-gray-400">{{ company.abn }}</td>
            <td class="py-3 flex items-center gap-4">
              <button
                @click="openEdit(company)"
                class="text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                Edit
              </button>
              <button
                @click="deleteCompany(company)"
                class="text-xs text-red-500 hover:text-red-400 transition-colors"
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
            {{ editingCompany ? 'Edit Company' : 'New Company' }}
          </h2>
          <button
            @click="closeModal"
            class="text-gray-500 hover:text-white transition-colors text-xl leading-none"
          >
            ×
          </button>
        </div>

        <!-- Form -->
        <form @submit.prevent="submit" class="px-6 py-5 space-y-4">

          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">Company Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              placeholder="e.g. Acme Transport"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>

          <div>
            <label class="block text-xs text-gray-400 font-mono mb-1">ABN</label>
            <input
              v-model="form.abn"
              type="text"
              required
              placeholder="e.g. 12 345 678 901"
              class="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400"
            />
          </div>

          <p v-if="error" class="text-red-400 text-sm">{{ error }}</p>

          <div class="flex gap-3 pt-2">
            <button
              type="submit"
              :disabled="submitting"
              class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50"
            >
              {{ submitting ? 'Saving...' : editingCompany ? 'Save Changes' : 'Create Company' }}
            </button>
            <button
              type="button"
              @click="closeModal"
              class="text-sm text-gray-400 hover:text-white px-4 py-2 transition-colors"
            >
              Cancel
            </button>
          </div>

        </form>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { notify } from '../store/notification'

const companies = ref([])
const loading = ref(true)
const showModal = ref(false)
const submitting = ref(false)
const error = ref('')
const editingCompany = ref(null)

const form = ref({ name: '', abn: '' })

async function fetchCompanies() {
  try {
    const res = await api.get('/companies/')
    companies.value = res.data
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingCompany.value = null
  form.value = { name: '', abn: '' }
  error.value = ''
  showModal.value = true
}

function openEdit(company) {
  editingCompany.value = company
  form.value = { name: company.name, abn: company.abn }
  error.value = ''
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingCompany.value = null
  error.value = ''
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    if (editingCompany.value) {
      const res = await api.put(`/companies/${editingCompany.value.id}/`, form.value)
      const idx = companies.value.findIndex(c => c.id === editingCompany.value.id)
      companies.value[idx] = res.data
      notify('Company updated successfully.')
    } else {
      const res = await api.post('/companies/', form.value)
      companies.value.push(res.data)
      notify('Company created successfully.')
    }
    closeModal()
  } catch (e) {
    error.value = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : 'Something went wrong'
  } finally {
    submitting.value = false
  }
}

async function deleteCompany(company) {
  if (!confirm(`Delete "${company.name}"?`)) return
  try {
    await api.delete(`/companies/${company.id}/`)
    companies.value = companies.value.filter(c => c.id !== company.id)
    notify(`"${company.name}" deleted.`)
  } catch (e) {
    notify(e.response?.data?.error || 'Cannot delete — company is used in existing records.', 'error')
  }
}

onMounted(fetchCompanies)
</script>