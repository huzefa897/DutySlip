<template>
  <div class="page">
    <div class="page-header">
      <div class="page-header__content">
        <span class="page-header__eyebrow">Dashboard</span>
        <h1 class="page-title">
          Revenue at a glance
        </h1>
        <p class="page-header__subtitle">
          {{ today }} · {{ bizName || 'Business overview' }}
        </p>
      </div>
      <div class="quick-actions-row">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'
import PaymentStatusBadge from '../components/PaymentStatusBadge.vue'

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
  const [slipsRes, tripsRes, settingsRes] = await Promise.all([
    api.get('/invoices/'),
    api.get('/trips/'),
    api.get('/settings/'),
  ])
  allSlips.value  = slipsRes.data
  allTrips.value  = tripsRes.data
  bizName.value   = settingsRes.data?.name || ''
})
</script>
