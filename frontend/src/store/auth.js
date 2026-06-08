import { computed, ref } from 'vue'

const ACCESS_KEY  = 'ds_access'
const REFRESH_KEY = 'ds_refresh'

function parseJwtPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

function loadFromStorage() {
  const access = localStorage.getItem(ACCESS_KEY)
  if (!access) return { access: null, refresh: null, payload: null }
  const payload = parseJwtPayload(access)
  if (payload && payload.exp * 1000 < Date.now()) {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    return { access: null, refresh: null, payload: null }
  }
  return { access, refresh: localStorage.getItem(REFRESH_KEY), payload }
}

const _initial = loadFromStorage()

// ── Reactive state ────────────────────────────────────────────
const accessToken  = ref(_initial.access)
const refreshToken = ref(_initial.refresh)
const _payload     = ref(_initial.payload)

// ── Derived ───────────────────────────────────────────────────
export const isAuthenticated = computed(() => !!accessToken.value)
export const userRole        = computed(() => _payload.value?.role ?? null)
export const isAdmin         = computed(() => userRole.value === 'admin')
export const isClient        = computed(() => userRole.value === 'client')
export const userName        = computed(() => _payload.value?.name ?? '')
export const userEmail       = computed(() => _payload.value?.email ?? '')
export const userCompanyIds  = computed(() => _payload.value?.company_ids ?? [])

// Active company — persists in sessionStorage (clears on tab close)
function loadActiveCompany() {
  try {
    const raw = sessionStorage.getItem('ds_active_company')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export const activeCompany = ref(loadActiveCompany())

export function setActiveCompany(company) {
  activeCompany.value = company
  if (company) {
    sessionStorage.setItem('ds_active_company', JSON.stringify(company))
  } else {
    sessionStorage.removeItem('ds_active_company')
  }
}

// ── Mutations ─────────────────────────────────────────────────
export function setTokens(access, refresh) {
  accessToken.value  = access
  refreshToken.value = refresh
  _payload.value     = parseJwtPayload(access)
  localStorage.setItem(ACCESS_KEY,  access)
  if (refresh) localStorage.setItem(REFRESH_KEY, refresh)
}

export function clearAuth() {
  accessToken.value  = null
  refreshToken.value = null
  _payload.value     = null
  activeCompany.value = null
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  sessionStorage.removeItem('ds_active_company')
}

// Export raw refs for API interceptor access
export { accessToken, refreshToken }
