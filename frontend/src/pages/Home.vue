<template>
  <div>
    <!-- Hero -->
    <div class="hero">
      <h1 class="hero-title">
        Welcome back<span class="hero-dot">.</span>
      </h1>
      <p class="hero-sub">
        {{ today }} · {{ bizName }}
      </p>
    </div>

    <!-- Stats Row -->
    <div class="stats-grid">
      <div class="stat-card">
        <p class="stat-label">
          Duty Slips
        </p>
        <p class="stat-value">
          {{ stats.totalSlips }}
        </p>
      </div>
      <div class="stat-card">
        <p class="stat-label">
          Total Entries
        </p>
        <p class="stat-value">
          {{ stats.totalEntries }}
        </p>
      </div>
      <div class="stat-card">
        <p class="stat-label">
          Total Revenue
        </p>
        <p class="stat-value stat-value--amber">
          {{ currencySymbol }}{{ stats.totalRevenue }}
        </p>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h2 class="section-label">
        Quick Actions
      </h2>
      <div class="quick-actions-row">
        <router-link
          to="/entries/create"
          class="btn-primary"
        >
          + New Entry
        </router-link>
        <router-link
          to="/dutyslips/create"
          class="btn-secondary"
        >
          + New Duty Slip
        </router-link>
      </div>
    </div>

    <!-- Recent Duty Slips + Recent Entries side by side -->
    <div class="two-col">
      <!-- Recent Duty Slips -->
      <div>
        <div class="list-header">
          <h2 class="section-label">
            Recent Duty Slips
          </h2>
          <router-link
            to="/dutyslips"
            class="view-all"
          >
            View all →
          </router-link>
        </div>

        <p
          v-if="recentSlips.length === 0"
          class="empty-text"
        >
          No duty slips yet.
        </p>

        <div class="card-list">
          <router-link
            v-for="slip in recentSlips"
            :key="slip.id"
            :to="`/dutyslips/${slip.id}`"
            class="list-card"
          >
            <div>
              <p class="card-id">
                {{ formatSlipId(slip.id) }}
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
              <p class="card-entries">
                {{ slip.entries?.length ?? 0 }} entries
              </p>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Recent Entries -->
      <div>
        <div class="list-header">
          <h2 class="section-label">
            Recent Entries
          </h2>
          <router-link
            to="/entries"
            class="view-all"
          >
            View all →
          </router-link>
        </div>

        <p
          v-if="recentEntries.length === 0"
          class="empty-text"
        >
          No entries yet.
        </p>

        <div class="card-list">
          <div
            v-for="entry in recentEntries"
            :key="entry.id"
            class="list-card list-card--static"
          >
            <div>
              <p class="card-name">
                {{ entry.party_name }}
              </p>
              <p class="card-meta">
                {{ entry.date }} · {{ entry.car_name }}
              </p>
            </div>
            <div class="card-right">
              <p class="card-amount">
                {{ currencySymbol }}{{ entry.row_total }}
              </p>
              <p class="card-status">
                <span
                  v-if="entry.duty_slip"
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { currencySymbol } from '../store/currency'
import { formatSlipId } from '../utils/formatId'

const allSlips   = ref([])
const allEntries = ref([])
const bizName    = ref('')

const today = new Date().toLocaleDateString('en-AU', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
})

const recentSlips   = computed(() => allSlips.value.slice(0, 5))
const recentEntries = computed(() => allEntries.value.slice(0, 5))

const stats = computed(() => {
  const totalRevenue = allSlips.value
    .reduce((sum, s) => sum + parseFloat(s.grand_total || 0), 0)
    .toFixed(2)
  return {
    totalSlips: allSlips.value.length,
    totalEntries: allEntries.value.length,
    totalRevenue,
  }
})

onMounted(async () => {
  const [slipsRes, entriesRes, settingsRes] = await Promise.all([
    api.get('/dutyslips/'),
    api.get('/entries/'),
    api.get('/settings/'),
  ])
  allSlips.value   = slipsRes.data
  allEntries.value = entriesRes.data
  bizName.value    = settingsRes.data?.name || ''
})
</script>

<style scoped>
/* Hero */
.hero {
  margin-bottom: 2.5rem;
}

.hero-title {
  font-family: monospace;
  font-size: 1.875rem;
  font-weight: 700;
  color: #ffffff;
  letter-spacing: -0.025em;
}

.hero-dot {
  color: #fbbf24;
}

.hero-sub {
  color: #6b7280;
  font-size: 0.875rem;
  font-family: monospace;
  margin-top: 0.5rem;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

@media (min-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.stat-card {
  background-color: #111827;
  border: 1px solid #1f2937;
  border-radius: 0.5rem;
  padding: 1.25rem;
}

.stat-label {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-family: monospace;
  font-size: 1.875rem;
  font-weight: 700;
  color: #ffffff;
}

.stat-value--amber {
  color: #fbbf24;
}

/* Quick Actions */
.quick-actions {
  margin-bottom: 2.5rem;
}

.quick-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn-primary {
  background-color: #fbbf24;
  color: #030712;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.625rem 1.25rem;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #fcd34d;
}

.btn-secondary {
  background-color: #1f2937;
  border: 1px solid #374151;
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.625rem 1.25rem;
  border-radius: 0.25rem;
  text-decoration: none;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #374151;
}

/* Section label */
.section-label {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Two column layout */
.two-col {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .two-col {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* List header */
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.view-all {
  font-family: monospace;
  font-size: 0.75rem;
  color: #fbbf24;
  text-decoration: none;
  transition: color 0.2s;
}

.view-all:hover {
  color: #fcd34d;
}

.empty-text {
  color: #4b5563;
  font-size: 0.875rem;
}

/* Card list */
.card-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.list-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #111827;
  border: 1px solid #1f2937;
  border-radius: 0.25rem;
  padding: 1rem;
  text-decoration: none;
  transition: border-color 0.2s;
}

.list-card:not(.list-card--static):hover {
  border-color: rgba(251, 191, 36, 0.4);
}

.card-id {
  font-family: monospace;
  font-size: 0.75rem;
  color: rgba(251, 191, 36, 0.7);
  margin-bottom: 0.125rem;
}

.card-name {
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 500;
}

.card-meta {
  color: #6b7280;
  font-family: monospace;
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

.card-right {
  text-align: right;
}

.card-amount {
  color: #fbbf24;
  font-family: monospace;
  font-weight: 700;
  font-size: 0.875rem;
}

.card-entries {
  color: #4b5563;
  font-family: monospace;
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

.card-status {
  font-family: monospace;
  font-size: 0.75rem;
  margin-top: 0.125rem;
}

.status--assigned {
  color: #22c55e;
}

.status--unassigned {
  color: #4b5563;
}
</style>