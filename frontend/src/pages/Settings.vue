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
          :src="logoPreview || `${mediaUrl}${currentLogo}`"
            class="h-16 object-contain bg-white rounded p-1"
            alt="Logo"
          />
          <div v-else class="h-16 w-32 bg-gray-800 border border-gray-700 rounded flex items-center justify-center">
            <span class="text-gray-600 text-xs font-mono">No logo</span>
          </div>
          <div>
            <input type="file" accept="image/*" @change="onLogoChange" class="hidden" ref="fileInput" />
            <button type="button" @click="$refs.fileInput.click()"
              class="text-xs bg-gray-800 border border-gray-700 text-gray-300 px-3 py-2 rounded hover:bg-gray-700 transition-colors">
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
      <div class="border-t border-gray-800 pt-6 mt-2">
        <h2 class="text-sm font-mono font-bold text-white mb-1">Backup & Restore</h2>
        <p class="text-xs text-gray-500 font-mono mb-4">
          Export data locally or sync with GitHub.
        </p>

        <div class="space-y-4">

          <!-- Export + GitHub Push -->
          <div class="bg-gray-900 border border-gray-800 rounded p-4">
            <p class="text-sm text-white font-medium mb-1">Export Backup</p>
            <p class="text-xs text-gray-500 font-mono mb-3">
              Downloads a JSON file. If GitHub is configured, also pushes to your repo automatically.
            </p>
            <div class="flex items-center gap-3 flex-wrap">
            <a :href="`${apiUrl}/backup/`" download


                class="inline-block bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono">
                ⬇ Download + Push
              </a>
              <button type="button" @click="pushToGithub" :disabled="pushing"
                class="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono disabled:opacity-50">
                {{ pushing ? 'Pushing...' : '⬆ Push to GitHub Only' }}
              </button>
            </div>
          </div>
<!-- Restore from GitHub -->
<div class="bg-gray-900 border border-gray-800 rounded p-4">
  <p class="text-sm text-white font-medium mb-2">Restore from GitHub</p>
  <button type="button" @click="fetchGithubBackups" :disabled="loadingBackups"
    class="bg-gray-800 border border-gray-700 text-white text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono mb-3 disabled:opacity-50">
    {{ loadingBackups ? 'Loading...' : '↻ Load GitHub Backups' }}
  </button>

  <div v-if="githubBackups.length > 0" class="space-y-2">
    <div v-for="backup in githubBackups" :key="backup.name"
      class="flex items-center justify-between bg-gray-800 rounded px-3 py-2">
      <div>
        <p class="text-xs font-mono text-white">{{ backup.name }}</p>
        <p class="text-xs font-mono text-gray-500">{{ (backup.size / 1024).toFixed(1) }} KB</p>
      </div>
      <button @click="restoreFromGithub(backup)"
        class="text-xs text-amber-400 hover:text-amber-300 font-mono transition-colors">
        Restore
      </button>
    </div>
  </div>

  <p v-else-if="backupsLoaded && githubBackups.length === 0"
    class="text-xs text-gray-600 font-mono">
    No backups found in GitHub repo.
  </p>
</div>

          <!-- Restore from local file -->
          <div class="bg-gray-900 border border-gray-800 rounded p-4">
            <p class="text-sm text-white font-medium mb-1">Restore from Local File</p>
            <p class="text-xs text-gray-500 font-mono mb-1">Upload a previously exported JSON backup.</p>
            <p class="text-xs text-red-400 font-mono mb-3">⚠ This will replace ALL existing data.</p>
            <div class="flex items-center gap-3">
              <input type="file" accept=".json" @change="onBackupFileChange" class="hidden" ref="backupFileInput" />
              <button type="button" @click="$refs.backupFileInput.click()"
                class="bg-gray-800 border border-gray-700 text-gray-300 text-sm px-4 py-2 rounded hover:bg-gray-700 transition-colors font-mono">
                Choose File
              </button>
              <span class="text-xs text-gray-500 font-mono">
                {{ backupFile ? backupFile.name : 'No file chosen' }}
              </span>
              <button v-if="backupFile" type="button" @click="restoreLocalBackup" :disabled="restoring"
                class="bg-red-700 hover:bg-red-600 text-white text-sm font-bold px-4 py-2 rounded transition-colors disabled:opacity-50">
                {{ restoring ? 'Restoring...' : 'Restore' }}
              </button>
            </div>
          </div>

        </div>
      </div>

    </form>

    <!-- GitHub Backup Config -->
<div class="border-t border-gray-800 pt-5">
  <h2 class="text-sm font-mono font-bold text-white mb-1">GitHub Backup</h2>
  <p class="text-xs text-gray-500 font-mono mb-4">
    Connect a private GitHub repo as your backup destination.
  </p>
  <div class="space-y-4">
    <div>
      <label class="block text-xs text-gray-400 font-mono mb-1">GitHub Username</label>
      <input v-model="form.github_username" type="text" placeholder="e.g. huzefa"
        class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
    </div>
    <div>
      <label class="block text-xs text-gray-400 font-mono mb-1">Repository Name</label>
      <input v-model="form.github_repo" type="text" placeholder="e.g. dutyslip-backups"
        class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
    </div>
    <div>
      <label class="block text-xs text-gray-400 font-mono mb-1">
        Personal Access Token
        <span class="text-gray-600 normal-case ml-1">(stored securely, never shown)</span>
      </label>
      <input v-model="form.github_token" type="password" placeholder="ghp_xxxxxxxxxxxx"
        class="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-amber-400" />
    </div>

    <!-- Separate GitHub save button -->
    <button
      type="button"
      @click="saveGithubSettings"
      :disabled="savingGithub"
      class="bg-gray-800 border border-gray-700 text-white text-sm font-bold px-5 py-2 rounded hover:bg-gray-700 transition-colors disabled:opacity-50"
    >
      {{ savingGithub ? 'Saving...' : 'Save GitHub Settings' }}
    </button>
  </div>
</div>

    <!-- Confirm dialog -->
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
import { notify } from '../store/notification'
import { setCurrency } from '../store/currency'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import { useConfirm } from '../composables/useConfirm'

const savingGithub = ref(false)
const mediaUrl = import.meta.env.VITE_MEDIA_URL || ''
const apiUrl = import.meta.env.VITE_API_URL || '/api'

async function saveGithubSettings() {
  if (!form.value.github_username || !form.value.github_repo) {
    notify('Please enter GitHub username and repo name.', 'error')
    return
  }
  savingGithub.value = true
  try {
    const payload = new FormData()
    payload.append('github_username', form.value.github_username)
    payload.append('github_repo',     form.value.github_repo)
    if (form.value.github_token) {
      payload.append('github_token', form.value.github_token)
    }
    await api.patch('/settings/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    form.value.github_token = ''
    notify('GitHub settings saved.')
  } catch (e) {
    notify('Failed to save GitHub settings.', 'error')
  } finally {
    savingGithub.value = false
  }
}

// ── Confirm dialog ────────────────────────────────────────────
const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

// ── State ─────────────────────────────────────────────────────
const loading       = ref(true)
const submitting    = ref(false)
const currentLogo   = ref('')
const logoPreview   = ref('')
const logoFile      = ref(null)
const fileInput     = ref(null)
const backupFile    = ref(null)
const backupFileInput = ref(null)
const restoring     = ref(false)
const pushing       = ref(false)
const loadingBackups = ref(false)
const backupsLoaded = ref(false)
const githubBackups = ref([])

// ── Form ──────────────────────────────────────────────────────
const form = ref({
  name:            '',
  abn:             '',
  address:         '',
  phone:           '',
  email:           '',
  currency:        'USD',
  github_username: '',
  github_repo:     '',
  github_token:    '',
})

// ── Logo ──────────────────────────────────────────────────────
function onLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  logoFile.value = file
  logoPreview.value = URL.createObjectURL(file)
}

// ── Submit settings ───────────────────────────────────────────
async function submit() {
  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('name',            form.value.name)
    payload.append('abn',             form.value.abn)
    payload.append('address',         form.value.address)
    payload.append('phone',           form.value.phone)
    payload.append('email',           form.value.email)
    payload.append('currency',        form.value.currency)
    payload.append('github_username', form.value.github_username || '')
    payload.append('github_repo',     form.value.github_repo     || '')
    if (form.value.github_token) {
      payload.append('github_token', form.value.github_token)
    }
    if (logoFile.value) payload.append('logo', logoFile.value)

    const res = await api.patch('/settings/', payload, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    currentLogo.value = res.data.logo || ''
    logoFile.value = null
    logoPreview.value = ''
    form.value.github_token = '' // clear token field after save
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

// ── Mount ─────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const res = await api.get('/settings/')
    form.value = {
      name:            res.data.name            || '',
      abn:             res.data.abn             || '',
      address:         res.data.address         || '',
      phone:           res.data.phone           || '',
      email:           res.data.email           || '',
      currency:        res.data.currency        || 'USD',
      github_username: res.data.github_username || '',
      github_repo:     res.data.github_repo     || '',
      github_token:    '', // never prefill token
    }
    currentLogo.value = res.data.logo || ''
  } finally {
    loading.value = false
  }
})

// ── Backup: local file ────────────────────────────────────────
function onBackupFileChange(e) {
  backupFile.value = e.target.files[0] || null
}

async function restoreLocalBackup() {
  const ok = await ask({
    title: 'Restore Local Backup',
    message: 'This will permanently delete ALL existing data and replace it with the backup. This cannot be undone.',
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
    notify(e.response?.data?.error || 'Restore failed. Make sure the file is a valid backup.', 'error')
  } finally {
    restoring.value = false
    backupFile.value = null
  }
}

// ── Backup: GitHub ────────────────────────────────────────────
async function pushToGithub() {
  pushing.value = true
  try {
    await api.post('/backup/github/push/')
    notify('Backup pushed to GitHub successfully.')
  } catch (e) {
    notify(e.response?.data?.error || 'Failed to push to GitHub.', 'error')
  } finally {
    pushing.value = false
  }
}

async function fetchGithubBackups() {
  loadingBackups.value = true
  backupsLoaded.value = false
  try {
    const res = await api.get('/backup/github/list/')
    githubBackups.value = res.data
    backupsLoaded.value = true
  } catch (e) {
    notify(e.response?.data?.error || 'Could not load GitHub backups.', 'error')
  } finally {
    loadingBackups.value = false
  }
}

async function restoreFromGithub(backup) {
  const ok = await ask({
    title: `Restore from ${backup.name}`,
    message: 'This will permanently replace ALL existing data with this backup. Are you absolutely sure?',
    confirmLabel: 'Yes, Restore',
    destructive: true,
  })
  if (!ok) return
  restoring.value = true
  try {
    await api.post('/backup/github/restore/', { download_url: backup.download_url })
    notify('Backup restored successfully. Reloading...')
    setTimeout(() => window.location.reload(), 1500)
  } catch (e) {
    notify(e.response?.data?.error || 'Restore failed.', 'error')
  } finally {
    restoring.value = false
  }
}
</script>