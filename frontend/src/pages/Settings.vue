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
        <span class="page-header__eyebrow">Settings</span>
        <h1 class="page-title">
          Business Settings
        </h1>
        <p class="page-header__subtitle">
          Configure your business details, logo, and currency.
        </p>
      </div>
      <router-link
        to="/settings/backup"
        class="btn-secondary"
      >
        Backup Settings
      </router-link>
    </div>

    <div
      v-if="loading"
      class="empty-text"
    >
      Loading...
    </div>

    <section
      v-else
      class="section-card settings-form"
    >
      <form
        class="form"
        @submit.prevent="submit"
      >
        <!-- Logo -->
        <div class="field">
          <label class="label">Logo</label>
          <div class="logo-row">
            <img
              v-if="logoPreview || currentLogo"
              :src="logoPreview || currentLogo"
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

        <div class="actions">
          <button
            type="submit"
            :disabled="submitting"
            class="btn-primary"
          >
            {{ submitting ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import { notify } from '../store/notification'
import { setCurrency } from '../store/currency'

const loading     = ref(true)
const submitting  = ref(false)
const currentLogo = ref('')
const logoPreview = ref('')
const logoFile    = ref(null)
const fileInput   = ref(null)

const form = ref({
  name:     '',
  abn:      '',
  address:  '',
  phone:    '',
  email:    '',
  currency: 'USD',
})

function onLogoChange(e) {
  const file = e.target.files[0]
  if (!file) return
  logoFile.value    = file
  logoPreview.value = URL.createObjectURL(file)
}

async function submit() {
  submitting.value = true
  try {
    const payload = new FormData()
    payload.append('name',     form.value.name)
    payload.append('abn',      form.value.abn)
    payload.append('address',  form.value.address)
    payload.append('phone',    form.value.phone)
    payload.append('email',    form.value.email)
    payload.append('currency', form.value.currency)
    if (logoFile.value) payload.append('logo', logoFile.value)

    const res = await api.patch('/settings/', payload)
    currentLogo.value = res.data.logo || ''
    logoFile.value    = null
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
      name:     res.data.name     || '',
      abn:      res.data.abn      || '',
      address:  res.data.address  || '',
      phone:    res.data.phone    || '',
      email:    res.data.email    || '',
      currency: res.data.currency || 'USD',
    }
    currentLogo.value = res.data.logo || ''
  } finally {
    loading.value = false
  }
})
</script>
