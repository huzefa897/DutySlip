<template>
  <div class="page items-center">
    <button
      class="back-btn self-start"
      @click="$router.back()"
    >
      ← Back
    </button>
    <div class="w-full max-w-4xl">
      <div class="page-header">
        <div class="page-header__content">
          <span class="page-header__eyebrow">Invoices</span>
          <h1 class="page-title">
            Create a new invoice
          </h1>
          <p class="page-header__subtitle">
            Select a company and party, then choose the invoice type.
          </p>
        </div>
      </div>

      <form
        class="section-card form w-full"
        @submit.prevent="submit"
      >
        <!-- Company Name -->
        <div class="field">
          <label class="label">Company Name</label>
          <AutocompleteInput
            v-model="selectedCompanyName"
            :suggestions="companySuggestions"
            placeholder="Search company name..."
            required
          />
        </div>

        <!-- Party Name -->
        <div class="field">
          <label class="label">Party Name</label>
          <AutocompleteInput
            v-model="selectedPartyName"
            :suggestions="partySuggestions"
            :readonly="!form.company"
            :allow-add="!!form.company"
            :placeholder="form.company ? 'Search or add party name...' : 'Select company first...'"
            required
            @add="addParty"
          />
          <p
            v-if="form.company && partyOptions.length === 0 && !selectedPartyName"
            class="upload-hint"
          >
            No parties yet — type a name and click "+ Add" to create one.
          </p>
        </div>

        <!-- Invoice Type -->
        <div class="field">
          <label class="label">Invoice Type</label>
          <div class="toggle-group">
            <button
              type="button"
              class="toggle-btn"
              :class="{ 'toggle-btn--regular': form.invoice_type === 'regular' }"
              @click="form.invoice_type = 'regular'"
            >
              Regular
            </button>
            <button
              type="button"
              class="toggle-btn"
              :class="{ 'toggle-btn--outstation': form.invoice_type === 'outstation' }"
              @click="form.invoice_type = 'outstation'"
            >
              Outstation
            </button>
          </div>
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
            :disabled="submitting || !form.company || !form.party"
            class="btn-primary"
          >
            {{ submitting ? 'Creating...' : 'Create Invoice' }}
          </button>
          <router-link
            to="/invoices"
            class="btn-cancel px-2 py-2"
          >
            Cancel
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'
import { notify } from '../store/notification'
import AutocompleteInput from '../components/AutoCompleteInput.vue'

const router = useRouter()

const companies = ref([])
const partyOptions = ref([])
const selectedCompanyName = ref('')
const selectedPartyName = ref('')
const submitting = ref(false)
const error = ref('')

const form = ref({
  company: '',
  party: '',
  invoice_type: 'regular',
})

const companySuggestions = computed(() => companies.value.map(c => c.name))
const partySuggestions = computed(() => partyOptions.value.map(p => p.name))

watch(selectedCompanyName, (name) => {
  const found = companies.value.find(c => c.name === name)
  form.value.company = found?.id || ''
  selectedPartyName.value = ''
  form.value.party = ''
  partyOptions.value = []
  if (found) fetchParties(found.id)
})

watch(selectedPartyName, (name) => {
  const found = partyOptions.value.find(p => p.name === name)
  form.value.party = found?.id || ''
})

async function fetchParties(companyId) {
  try {
    const res = await api.get(`/companies/${companyId}/invoice-parties/`)
    partyOptions.value = res.data
  } catch {
    partyOptions.value = []
  }
}

async function addParty(name) {
  try {
    const res = await api.post(`/companies/${form.value.company}/invoice-parties/`, { name })
    partyOptions.value = [...partyOptions.value, res.data].sort((a, b) => a.name.localeCompare(b.name))
    selectedPartyName.value = res.data.name
    form.value.party = res.data.id
  } catch {
    notify('Failed to add party.', 'error')
  }
}

async function submit() {
  submitting.value = true
  error.value = ''
  try {
    const res = await api.post('/invoices/', {
      company: form.value.company,
      party: form.value.party,
      invoice_type: form.value.invoice_type,
    })
    router.push(`/invoices/${res.data.id}`)
    notify('Invoice created.')
  } catch (e) {
    error.value = e.response?.data
      ? Object.values(e.response.data).flat().join(' ')
      : 'Something went wrong'
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  const res = await api.get('/companies/')
  companies.value = res.data
})
</script>
