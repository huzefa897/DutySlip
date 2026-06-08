import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, isAdmin } from '../store/auth'

import Home           from '../pages/Home.vue'
import TripList       from '../pages/TripList.vue'
import CreateTrip     from '../pages/CreateTrip.vue'
import InvoiceList    from '../pages/InvoiceList.vue'
import InvoiceDetail  from '../pages/InvoiceDetail.vue'
import CreateInvoice  from '../pages/CreateInvoice.vue'
import Cars           from '../pages/Cars.vue'
import Settings       from '../pages/Settings.vue'
import BackupSettings from '../pages/BackupSettings.vue'
import Companies      from '../pages/Companies.vue'
import Login          from '../pages/Login.vue'
import AcceptInvite   from '../pages/AcceptInvite.vue'
import ResetPassword  from '../pages/ResetPassword.vue'
import ResetPasswordConfirm from '../pages/ResetPasswordConfirm.vue'
import Users          from '../pages/Users.vue'

const routes = [
  // ── Public auth pages ────────────────────────────────────────
  { path: '/login',                        component: Login },
  { path: '/auth/accept-invite',           component: AcceptInvite },
  { path: '/auth/reset-password',          component: ResetPassword },
  { path: '/auth/reset-password/confirm',  component: ResetPasswordConfirm },

  // ── Authenticated (all roles) ────────────────────────────────
  { path: '/',             component: Home,        meta: { requiresAuth: true } },
  { path: '/duty-slips',   component: TripList,    meta: { requiresAuth: true } },
  { path: '/invoices',     component: InvoiceList, meta: { requiresAuth: true } },
  { path: '/invoices/:id', component: InvoiceDetail, meta: { requiresAuth: true } },

  // ── Admin only ───────────────────────────────────────────────
  { path: '/duty-slips/create', component: CreateTrip,     meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/invoices/create',   component: CreateInvoice,  meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/cars',              component: Cars,           meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/settings',          component: Settings,       meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/settings/backup',   component: BackupSettings, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/companies',         component: Companies,      meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/users',             component: Users,          meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  if (to.meta.requiresAdmin && !isAdmin.value) {
    return next('/')
  }
  next()
})

export default router
