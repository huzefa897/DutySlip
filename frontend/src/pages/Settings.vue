<template>
  <div class="max-w-xl">
    <button
      @click="$router.back()"
      class="text-xs text-gray-500 hover:text-white font-mono transition-colors mb-4 flex items-center gap-1"
    >
      ← Back
    </button>
    <h1 class="text-xl font-mono font-bold text-white mb-6">Business Settings</h1>

    <div v-if="loading" class="text-gray-500 text-sm">Loading...</div>

    <form v-else @submit.prevent="submit" class="space-y-5">

      <!-- Logo Preview -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-2">Logo</label>
        <div class="flex items-center gap-4">
          <img
            v-if="logoPreview || currentLogo"
            :src="logoPreview || `http://127.0.0.1:8000${currentLogo}`"
            class="h-16 object-contain bg-white rounded p-1"
            alt="Logo"
          />
          <div
            v-else
            class="h-16 w-32 bg-gray-800 border border-gray-700 rounded flex items-center justify-center"
          >
            <span class="text-gray-600 text-xs font-mono">No logo</span>
          </div>
          <div>
            <input
              type="file"
              accept="image/*"
              @change="onLogoChange"
              class="hidden"
              ref="fileInput"
            />
            <button
              type="button"
              @click="$refs.fileInput.click()"
              class="text-xs bg-gray-800 border border-gray-700 text-gray-300 px-3 py-2 rounded hover:bg-gray-700 transition-colors"
            >
              Upload Logo
            </button>
            <p class="text-gray-600 text-xs mt-1">PNG, JPG recommended</p>
          </div>
        </div>
      </div>

      <!-- Business Name -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Business Name</label>
        <input v-model="form.name" type="text" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- ABN -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">ABN</label>
        <input v-model="form.abn" type="text" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Address -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Address</label>
        <textarea v-model="form.address" rows="2" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Phone -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Phone</label>
        <input v-model="form.phone" type="text" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Email -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Email</label>
        <input v-model="form.email" type="email" required
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
      </div>

      <!-- Currency -->
      <div>
        <label class="block text-xs text-gray-400 font-mono mb-1">Currency</label>
        <select v-model="form.currency"
          class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400">
          <option value="USD">Dollar ($)</option>
          <option value="INR">Rupee (₹)</option>
        </select>
      </div>

      <!-- Submit -->
      <div class="flex gap-3 pt-2">
        <button type="submit" :disabled="submitting"
          class="bg-amber-400 text-gray-950 text-sm font-bold px-6 py-2 rounded hover:bg-amber-300 transition-colors disabled:opacity-50">
          {{ submitting ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>
<!-- Backup & Restore -->
<div class="border-t border-gray-800 pt-6 mt-6">
  <h2 class="text-sm font-mono font-bold text-white mb-1">Backup & Restore</h2>
  <p class="text-xs text-gray-500 font-mono mb-4">
    Export all your data as a JSON file, or restore from a previous backup.
  </p>

  <div class="space-y-4">

    <!-- Export -->
    <div class="bg-gray-900 border border-gray-800 rounded p-4">
      <p class="text-sm text-white font-medium mb-1">Export Backup</p>
      <p class="text-xs text-gray-500 font-mono mb-3">
        Downloads a JSON file containing all companies, cars, duty slips and entries.
      </p>
      
       <a href="http://127.0.0.1:8000/api/backup/"
        download
        class="inline-block bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono"
      >
        ⬇ Download Backup
      </a>
    </div>

    <!-- Import -->
    <div class="bg-gray-900 border border-gray-800 rounded p-4">
      <p class="text-sm text-white font-medium mb-1">Restore from Backup</p>
      <p class="text-xs text-gray-500 font-mono mb-1">
        Upload a previously exported JSON backup file.
      </p>
      <p class="text-xs text-red-400 font-mono mb-3">
        ⚠ Warning — this will replace ALL existing data.
      </p>

      <div class="flex items-center gap-3">
        <input
          type="file"
          accept=".json"
          @change="onBackupFileChange"
          class="hidden"
          ref="backupFileInput"
        />
        <button
          type="button"
          @click="$refs.backupFileInput.click()"
          class="bg-gray-800 border border-gray-700 text-gray-300 text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono"
        >
          Choose File
        </button>
        <span class="text-xs text-gray-500 font-mono">
          {{ backupFile ? backupFile.name : 'No file chosen' }}
        </span>
        <button
          v-if="backupFile"
          type="button"
          @click="restoreBackup"
          :disabled="restoring"
          class="bg-red-700 hover:bg-red-600 text-white text-sm font-bold px-4 py-2 rounded transition-colors disabled:opacity-50"
        >
          {{ restoring ? 'Restoring...' : 'Restore' }}
        </button>
      </div>
    </div>

  </div>
</div>

<!-- Confirm restore dialog -->
<ConfirmDialog
  :visible="confirmVisible"
  :title="confirmTitle"
  :message="confirmMessage"
  :confirm-label="confirmLabel"
  :destructive="destructive"
  @confirm="onConfirm"
  @cancel="onCancel"
/>
    </form>
  </div>

  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { notify } from '../store/notification'
import { setCurrency } from '../store/currency'


const loading = ref(true)
const submitting = ref(false)
const currentLogo = ref('')
const logoPreview = ref('')
const logoFile = ref(null)
const fileInput = ref(null)
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const backupFile = ref(null)
const backupFileInput = ref(null)
const restoring = ref(false)
const form = ref({
  name: '',
  abn: '',
  address: '',
  phone: '',
  email: '',
  currency: 'USD',
})

function onLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  logoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

async function submit() {
  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('name', form.value.name)
    payload.append('abn', form.value.abn)
    payload.append('address', form.value.address)
    payload.append('phone', form.value.phone)
    payload.append('email', form.value.email)
    payload.append('currency', form.value.currency)
    if (logoFile.value) payload.append('logo', logoFile.value)

    const res = await api.patch('/settings/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    currentLogo.value = res.data.logo || ''
    logoFile.value = null
    logoPreview.value = ''
    setCurrency(res.data.currency)
    notify('Settings saved successfully.')

  } catch (e) {
    notify(
      e.response?.data
        ? Object.values(e.response.data).flat().join(' ')
        : 'Failed to save settings.',
      'error'
    )
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  try {
    const res = await api.get('/settings/')
    form.value = {
      name: res.data.name || '',
      abn: res.data.abn || '',
      address: res.data.address || '',
      phone: res.data.phone || '',
      email: res.data.email || '',
      currency: res.data.currency || 'USD',
    }
    currentLogo.value = res.data.logo || ''
  } finally {
    loading.value = false
  }
})

function onBackupFileChange(e) {
  backupFile.value = e.target.files[0] || null
}

async function restoreBackup() {
  const ok = await ask({
    title: 'Restore Backup',
    message: 'This will permanently delete ALL existing data and replace it with the backup. This cannot be undone. Are you absolutely sure?',
    confirmLabel: 'Yes, Restore',
    destructive: true,
  })
  if (!ok) return

  restoring.value = true
  try {
    const text = await backupFile.value.text()
    await api.post('/restore/', JSON.parse(text), {
      headers: { 'Content-Type': 'application/json' }
    })
    notify('Backup restored successfully. Reloading...')
    setTimeout(() => window.location.reload(), 1500)
  } catch (e) {
    notify(
      e.response?.data?.error || 'Restore failed. Make sure the file is a valid backup.',
      'error'
    )
  } finally {
    restoring.value = false
    backupFile.value = null
  }
}
</script>
