<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Dashboard</span>
        <h1 class="page-title">
          Revenue at a glance
        </h1>
        <p class="page-header__subtitle">
          {{ today }} · {{ activeCompany?.name || bizName || 'Business overview' }}
        </p>
      </div>
      <div
        v-if="isAdmin"
        class="quick-actions-row"
      >
        <router-link
          to="/invoices/create"
          class="btn-primary"
        >
          + Create Invoice
        </router-link>
        <router-link
          to="/duty-slips/create"
          class="btn-secondary"
        >
          + New Duty Slip
        </router-link>
      </div>
    </div>

    <div
      v-if="isClient && !activeCompany"
      class="empty-state-container"
    >
      <div class="empty-state">
        <div class="empty-state__icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M4 21V7l8-4 8 4v14M9 21V11h6v10" />
          </svg>
        </div>
        <h2 class="empty-state__title">
          Select a Company
        </h2>
        <p class="empty-state__text">
          Please select a company from the header to view its dashboard.
        </p>
      </div>
    </div>

    <template v-else>
      <div class="stats-grid">
        <div class="stat-card">
          <p class="stat-label">
            Revenue This Month
          </p>
          <p class="stat-value stat-value--accent">
            {{ currencySymbol }}{{ stats.monthRevenue }}
          </p>
          <p class="stat-meta">
            {{ stats.monthSlips }} invoices created this month
          </p>
        </div>
        <div class="stat-card">
          <p class="stat-label">
            Paid Invoices
          </p>
          <p class="stat-value">
            {{ stats.paidSlips }}
          </p>
          <p class="stat-meta">
            Fully settled invoices
          </p>
        </div>
        <div class="stat-card">
          <p class="stat-label">
            Pending Invoices
          </p>
          <p class="stat-value">
            {{ stats.pendingSlips }}
          </p>
          <p class="stat-meta">
            Awaiting payment
          </p>
        </div>
        <div class="stat-card">
          <p class="stat-label">
            Draft Invoices
          </p>
          <p class="stat-value">
            {{ stats.draftSlips }}
          </p>
          <p class="stat-meta">
            Not yet finalised
          </p>
        </div>
      </div>

      <div class="two-col">
        <section class="section-card">
          <div class="list-header">
            <h2 class="section-label">
              Recent Invoices
            </h2>
            <router-link
              to="/invoices"
              class="view-all"
            >
              View all →
            </router-link>
          </div>

          <p
            v-if="recentSlips.length === 0"
            class="empty-text"
          >
            No invoices yet.
          </p>

          <div class="card-list">
            <router-link
              v-for="slip in recentSlips"
              :key="slip.id"
              :to="`/invoices/${slip.id}`"
              class="list-card"
            >
              <div>
                <p class="card-id">
                  INV-{{ formatSlipId(slip.id) }}
                </p>
                <p class="card-name">
                  {{ slip.party_name }}
                </p>
                <p class="card-meta">
                  {{ slip.company_name }} · {{ slip.created_at?.slice(0, 10) }}
                </p>
              </div>
              <div class="card-right">
                <p class="card-amount">
                  {{ currencySymbol }}{{ slip.grand_total }}
                </p>
                <PaymentStatusBadge :status="slip.payment_status" />
              </div>
            </router-link>
          </div>
        </section>

        <section class="section-card">
          <div class="list-header">
            <h2 class="section-label">
              Recent Duty Slips
            </h2>
            <router-link
              to="/duty-slips"
              class="view-all"
            >
              View all →
            </router-link>
          </div>

          <p
            v-if="recentTrips.length === 0"
            class="empty-text"
          >
            No duty slips yet.
          </p>

          <div class="card-list">
            <div
              v-for="trip in recentTrips"
              :key="trip.id"
              class="list-card list-card--static"
            >
              <div>
                <p class="card-name">
                  {{ trip.party_name }}
                </p>
                <p class="card-meta">
                  {{ trip.date }} · {{ trip.car_name }}
                </p>
              </div>
              <div class="card-right">
                <p class="card-amount">
                  {{ currencySymbol }}{{ trip.row_total }}
                </p>
                <p class="card-status">
                  <span
                    v-if="trip.invoice"
                    class="status--assigned"
                  >assigned</span>
                  <span
                    v-else
                    class="status--unassigned"
                  >unassigned</span>
                </p>
              </div>
            </div>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import PaymentStatusBadge from '../components/PaymentStatusBadge.vue'
import { isAdmin, isClient, activeCompany } from '../store/auth'

const allSlips  = ref([])
const allTrips  = ref([])
const bizName   = ref('')

const today = new Date().toLocaleDateString('en-AU', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

const recentSlips  = computed(() => allSlips.value.slice(0, 5))
const recentTrips  = computed(() => allTrips.value.slice(0, 5))

const stats = computed(() => {
  const now = new Date()
  const currentMonthSlips = allSlips.value.filter((slip) => {
    if (!slip.created_at) return false
    const created = new Date(slip.created_at)
    return created.getMonth() === now.getMonth() && created.getFullYear() === now.getFullYear()
  })

  const monthRevenue = currentMonthSlips
    .reduce((sum, s) => sum + parseFloat(s.grand_total || 0), 0)
    .toFixed(2)

  return {
    monthRevenue,
    monthSlips: currentMonthSlips.length,
    paidSlips: allSlips.value.filter((slip) => slip.payment_status === 'paid').length,
    pendingSlips: allSlips.value.filter((slip) => slip.payment_status === 'unpaid').length,
    draftSlips: allSlips.value.filter((slip) => slip.status === 'draft').length,
  }
})

onMounted(async () => {
  if (isClient.value && !activeCompany.value) return

  const params = isClient.value && activeCompany.value
    ? { company: activeCompany.value.id }
    : {}

  const [slipsRes, tripsRes, settingsRes] = await Promise.all([
    api.get('/invoices/', { params }),
    api.get('/trips/', { params }),
    api.get('/settings/'),
  ])
  allSlips.value  = slipsRes.data
  allTrips.value  = tripsRes.data
  bizName.value   = settingsRes.data?.name || ''
})
</script>

<style scoped>
.empty-state-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.empty-state {
  text-align: center;
  max-width: 320px;
}

.empty-state__icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 24px;
  color: rgba(255,255,255,0.1);
}

.empty-state__title {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 12px;
}

.empty-state__text {
  font-size: 14px;
  color: rgba(255,255,255,0.5);
  line-height: 1.6;
}
</style>
