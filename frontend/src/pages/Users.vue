<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">
        Users
      </h1>
      <button
        class="btn-primary"
        @click="showInvite = true"
      >
        + Invite User
      </button>
    </div>

    <!-- User list -->
    <div class="card-list">
      <div
        v-for="user in users"
        :key="user.id"
        class="user-card"
      >
        <div class="user-info">
          <p class="user-name">
            {{ user.name || user.email }}
          </p>
          <p class="user-email">
            {{ user.email }}
          </p>
          <div class="user-meta">
            <span
              class="status-badge"
              :class="`status-badge--${user.role}`"
            >{{ user.role }}</span>
            <span
              v-if="!user.is_active"
              class="status-badge status-badge--deactivated"
            >Deactivated</span>
          </div>
          <p
            v-if="user.role === 'client' && user.companies.length"
            class="user-companies"
          >
            {{ user.companies.map(c => c.name).join(', ') }}
          </p>
        </div>

        <div class="user-actions">
          <button
            class="btn-secondary btn-sm"
            @click="openEdit(user)"
          >
            Edit
          </button>
          <button
            class="btn-secondary btn-sm"
            @click="toggleActive(user)"
          >
            {{ user.is_active ? 'Deactivate' : 'Reactivate' }}
          </button>
        </div>
      </div>

      <p
        v-if="!loading && users.length === 0"
        class="empty-state"
      >
        No users yet.
      </p>
    </div>

    <!-- Invite modal -->
    <div
      v-if="showInvite"
      class="modal-overlay"
      @click.self="showInvite = false"
    >
      <div class="modal-box">
        <h2 class="modal-title">
          Invite User
        </h2>
        <form @submit.prevent="sendInvite">
          <div class="field">
            <label class="label">Email</label>
            <input
              v-model="inviteForm.email"
              type="email"
              class="input"
              placeholder="email@example.com"
              required
            >
          </div>
          <div class="field">
            <label class="label">Role</label>
            <select
              v-model="inviteForm.role"
              class="input"
            >
              <option value="client">
                Client
              </option>
              <option value="admin">
                Admin
              </option>
            </select>
          </div>
          <p
            v-if="inviteError"
            class="error-text"
          >
            {{ inviteError }}
          </p>
          <div class="modal-actions">
            <button
              type="button"
              class="btn-secondary"
              @click="showInvite = false"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="inviting"
            >
              {{ inviting ? 'Sending…' : 'Send Invite' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit modal -->
    <div
      v-if="editUser"
      class="modal-overlay"
      @click.self="editUser = null"
    >
      <div class="modal-box">
        <h2 class="modal-title">
          Edit {{ editUser.email }}
        </h2>
        <form @submit.prevent="saveEdit">
          <div class="field">
            <label class="label">Role</label>
            <select
              v-model="editForm.role"
              class="input"
            >
              <option value="client">
                Client
              </option>
              <option value="admin">
                Admin
              </option>
            </select>
          </div>

          <div
            v-if="editForm.role === 'client'"
            class="field"
          >
            <label class="label">Assigned Companies</label>
            <div class="checkbox-list">
              <label
                v-for="c in allCompanies"
                :key="c.id"
                class="checkbox-item"
              >
                <input
                  v-model="editForm.company_ids"
                  type="checkbox"
                  :value="c.id"
                >
                {{ c.name }}
              </label>
            </div>
          </div>

          <p
            v-if="editError"
            class="error-text"
          >
            {{ editError }}
          </p>
          <div class="modal-actions">
            <button
              type="button"
              class="btn-secondary"
              @click="editUser = null"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn-primary"
              :disabled="saving"
            >
              {{ saving ? 'Saving…' : 'Save' }}
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

const users       = ref([])
const allCompanies = ref([])
const loading     = ref(true)

const showInvite  = ref(false)
const inviteForm  = ref({ email: '', role: 'client' })
const inviteError = ref('')
const inviting    = ref(false)

const editUser    = ref(null)
const editForm    = ref({ role: 'client', company_ids: [] })
const editError   = ref('')
const saving      = ref(false)

onMounted(async () => {
  await Promise.all([fetchUsers(), fetchCompanies()])
  loading.value = false
})

async function fetchUsers() {
  try {
    const res = await api.get('/auth/users/')
    users.value = res.data
  } catch {
    notify('Failed to load users.', 'error')
  }
}

async function fetchCompanies() {
  try {
    const res = await api.get('/companies/')
    allCompanies.value = res.data
  } catch (e) {
    // Silence error
  }
}

async function sendInvite() {
  inviting.value = true
  inviteError.value = ''
  try {
    await api.post('/auth/invite/', inviteForm.value)
    notify(`Invite sent to ${inviteForm.value.email}.`)
    showInvite.value = false
    inviteForm.value = { email: '', role: 'client' }
  } catch (e) {
    inviteError.value = e.response?.data?.error || 'Failed to send invite.'
  } finally {
    inviting.value = false
  }
}

function openEdit(user) {
  editUser.value = user
  editForm.value = {
    role: user.role,
    company_ids: user.companies.map(c => c.id),
  }
  editError.value = ''
}

async function saveEdit() {
  saving.value = true
  editError.value = ''
  try {
    await api.patch(`/auth/users/${editUser.value.id}/`, { role: editForm.value.role })
    if (editForm.value.role === 'client') {
      await api.put(`/auth/users/${editUser.value.id}/companies/`, {
        company_ids: editForm.value.company_ids,
      })
    }
    await fetchUsers()
    notify('User updated.')
    editUser.value = null
  } catch (e) {
    editError.value = e.response?.data?.error || 'Failed to save.'
  } finally {
    saving.value = false
  }
}

async function toggleActive(user) {
  try {
    await api.patch(`/auth/users/${user.id}/`, { is_active: !user.is_active })
    await fetchUsers()
    notify(user.is_active ? 'User deactivated.' : 'User reactivated.')
  } catch {
    notify('Failed to update user.', 'error')
  }
}
</script>

<style scoped>
.user-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  background: var(--surface, rgba(255,255,255,0.04));
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  margin-bottom: 10px;
}
.user-name { font-weight: 600; margin: 0 0 2px; }
.user-email { font-size: 13px; color: rgba(255,255,255,0.5); margin: 0 0 6px; }
.user-meta { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 4px; }
.user-companies { font-size: 12px; color: rgba(255,255,255,0.4); margin: 0; }
.user-actions { display: flex; gap: 8px; flex-shrink: 0; }
.status-badge--admin { background: rgba(99,102,241,0.2); color: #a5b4fc; }
.status-badge--client { background: rgba(34,197,94,0.15); color: #86efac; }
.status-badge--deactivated { background: rgba(239,68,68,0.15); color: #fca5a5; }
.btn-sm { padding: 6px 12px; font-size: 13px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 100; padding: 24px; }
.modal-box { background: var(--surface, #1a1a2e); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 28px; width: 100%; max-width: 420px; }
.modal-title { font-size: 18px; font-weight: 600; margin: 0 0 20px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 20px; }
.checkbox-list { display: flex; flex-direction: column; gap: 8px; max-height: 200px; overflow-y: auto; }
.checkbox-item { display: flex; align-items: center; gap: 8px; font-size: 14px; cursor: pointer; }
.error-text { color: #f87171; font-size: 13px; margin: 4px 0 0; }
.empty-state { text-align: center; color: rgba(255,255,255,0.4); padding: 40px 0; }
</style>
