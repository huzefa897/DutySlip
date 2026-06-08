<template>
  <div class="container container--narrow">
    <button
      class="back-btn"
      @click="$router.back()"
    >
      ← Back
    </button>
    <h1 class="title">
      Business Settings
    </h1>

    <div
      v-if="loading"
      class="loading-text"
    >
      Loading...
    </div>

    <form
      v-else
      class="form"
      @submit.prevent="submit"
    >
      <!-- Logo Preview -->
      <div class="field">
        <label class="label">Logo</label>
        <div class="logo-row">
          <img
            v-if="logoPreview || currentLogo"
            :src="logoPreview || `${mediaUrl}${currentLogo}`"
            class="logo-img"
            alt="Logo"
          >
          <div
            v-else
            class="logo-placeholder"
          >
            <span class="logo-placeholder-text">No logo</span>
          </div>
          <div>
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="hidden-input"
              @change="onLogoChange"
            >
            <button
              type="button"
              class="upload-btn"
              @click="$refs.fileInput.click()"
            >
              Upload Logo
            </button>
            <p class="upload-hint">
              PNG, JPG recommended
            </p>
          </div>
        </div>
      </div>

      <!-- Business Name -->
      <div class="field">
        <label class="label">Business Name</label>
        <input
          v-model="form.name"
          type="text"
          required
          class="input"
        >
      </div>

      <!-- ABN -->
      <div class="field">
        <label class="label">ABN</label>
        <input
          v-model="form.abn"
          type="text"
          required
          class="input"
        >
      </div>

      <!-- Address -->
      <div class="field">
        <label class="label">Address</label>
        <textarea
          v-model="form.address"
          rows="2"
          required
          class="input textarea"
        />
      </div>

      <!-- Phone -->
      <div class="field">
        <label class="label">Phone</label>
        <input
          v-model="form.phone"
          type="text"
          required
          class="input"
        >
      </div>

      <!-- Email -->
      <div class="field">
        <label class="label">Email</label>
        <input
          v-model="form.email"
          type="email"
          required
          class="input"
        >
      </div>

      <!-- Currency -->
      <div class="field">
        <label class="label">Currency</label>
        <select
          v-model="form.currency"
          class="input"
        >
          <option value="USD">
            Dollar
          </option>
          <option value="INR">
            Rupee (₹)
          </option>
        </select>
      </div>

      <!-- Submit -->
      <div class="actions">
        <button
          type="submit"
          :disabled="submitting"
          class="btn-primary"
        >
          {{ submitting ? 'Saving...' : 'Save Settings' }}
        </button>
      </div>

      <!-- Backup & Restore -->
      <div class="section-divider">
        <h2 class="section-title">
          Backup & Restore
        </h2>
        <p class="section-desc">
          Export data locally or sync with GitHub.
        </p>

        <div class="backup-sections">
          <!-- Export + GitHub Push -->
          <div class="backup-card">
            <p class="card-title">
              Export Backup
            </p>
            <p class="card-desc">
              Downloads a JSON file. If GitHub is configured, also pushes to your repo automatically.
            </p>
            <div class="card-actions">
              <a
                :href="`${apiUrl}/backup/`"
                download
                class="btn-secondary"
              >
                ⬇ Download + Push
              </a>
              <button
                type="button"
                :disabled="pushing"
                class="btn-secondary"
                @click="pushToGithub"
              >
                {{ pushing ? 'Pushing...' : '⬆ Push to GitHub Only' }}
              </button>
            </div>
          </div>

          <!-- Restore from GitHub -->
          <div class="backup-card">
            <p class="card-title">
              Restore from GitHub
            </p>
            <button
              type="button"
              :disabled="loadingBackups"
              class="btn-secondary mb-3"
              @click="fetchGithubBackups"
            >
              {{ loadingBackups ? 'Loading...' : '↻ Load GitHub Backups' }}
            </button>

            <div
              v-if="githubBackups.length > 0"
              class="backup-list"
            >
              <div
                v-for="backup in githubBackups"
                :key="backup.name"
                class="backup-item"
              >
                <div>
                  <p class="backup-name">
                    {{ backup.name }}
                  </p>
                  <p class="backup-size">
                    {{ (backup.size / 1024).toFixed(1) }} KB
                  </p>
                </div>
                <button
                  class="btn-restore"
                  @click="restoreFromGithub(backup)"
                >
                  Restore
                </button>
              </div>
            </div>

            <p
              v-else-if="backupsLoaded && githubBackups.length === 0"
              class="no-backups"
            >
              No backups found in GitHub repo.
            </p>
          </div>

          <!-- Restore from local file -->
          <div class="backup-card">
            <p class="card-title">
              Restore from Local File
            </p>
            <p class="card-desc">
              Upload a previously exported JSON backup.
            </p>
            <p class="card-warn">
              ⚠ This will replace ALL existing data.
            </p>
            <div class="card-actions">
              <input
                ref="backupFileInput"
                type="file"
                accept=".json"
                class="hidden-input"
                @change="onBackupFileChange"
              >
              <button
                type="button"
                class="btn-secondary"
                @click="$refs.backupFileInput.click()"
              >
                Choose File
              </button>
              <span class="file-name">{{ backupFile ? backupFile.name : 'No file chosen' }}</span>
              <button
                v-if="backupFile"
                type="button"
                :disabled="restoring"
                class="btn-danger"
                @click="restoreLocalBackup"
              >
                {{ restoring ? 'Restoring...' : 'Restore' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </form>

    <!-- GitHub Backup Config -->
    <div class="section-divider">
      <h2 class="section-title">
        GitHub Backup
      </h2>
      <p class="section-desc">
        Connect a private GitHub repo as your backup destination.
      </p>
      <div class="form">
        <div class="field">
          <label class="label">GitHub Username</label>
          <input
            v-model="form.github_username"
            type="text"
            placeholder="e.g. huzefa"
            class="input"
          >
        </div>
        <div class="field">
          <label class="label">Repository Name</label>
          <input
            v-model="form.github_repo"
            type="text"
            placeholder="e.g. dutyslip-backups"
            class="input"
          >
        </div>
        <div class="field">
          <label class="label">
            Personal Access Token
            <span class="label-hint">(stored securely, never shown)</span>
          </label>
          <input
            v-model="form.github_token"
            type="password"
            placeholder="ghp_xxxxxxxxxxxx"
            class="input"
          >
        </div>
        <button
          type="button"
          :disabled="savingGithub"
          class="btn-secondary btn-github-save"
          @click="saveGithubSettings"
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
    await api.patch('/settings/', payload)
    form.value.github_token = ''
    notify('GitHub settings saved.')
  } catch {
    notify('Failed to save GitHub settings.', 'error')
  } finally {
    savingGithub.value = false
  }
}

const { visible: confirmVisible, title: confirmTitle, message: confirmMessage,
        confirmLabel, destructive, ask, onConfirm, onCancel } = useConfirm()

const loading         = ref(true)
const submitting      = ref(false)
const currentLogo     = ref('')
const logoPreview     = ref('')
const logoFile        = ref(null)
const fileInput       = ref(null)
const backupFile      = ref(null)
const backupFileInput = ref(null)
const restoring       = ref(false)
const pushing         = ref(false)
const loadingBackups  = ref(false)
const backupsLoaded   = ref(false)
const githubBackups   = ref([])

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

    const res = await api.patch('/settings/', payload)

    currentLogo.value = res.data.logo || ''
    logoFile.value = null
    logoPreview.value = ''
    form.value.github_token = ''
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
      name:            res.data.name            || '',
      abn:             res.data.abn             || '',
      address:         res.data.address         || '',
      phone:           res.data.phone           || '',
      email:           res.data.email           || '',
      currency:        res.data.currency        || 'USD',
      github_username: res.data.github_username || '',
      github_repo:     res.data.github_repo     || '',
      github_token:    '',
    }
    currentLogo.value = res.data.logo || ''
  } finally {
    loading.value = false
  }
})

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
