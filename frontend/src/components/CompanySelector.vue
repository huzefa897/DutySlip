<template>
  <div
    class="client-company-pill"
    :class="{ 'is-open': isOpen, 'is-empty': companies.length === 0 }"
    :title="selectedCompany?.name || 'No companies'"
  >
    <span class="client-company-pill__initial">{{ companyInitial }}</span>
    <svg
      class="client-company-pill__chevron"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.4"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path :d="isOpen ? 'm18 15-6-6-6 6' : 'm6 9 6 6 6-6'" />
    </svg>

    <label
      class="sr-only"
      for="client-company-select"
    >Select company</label>
    <template v-if="companies.length > 1">
      <select
        id="client-company-select"
        class="client-company-pill__select"
        :value="selectedCompany?.id"
        @change="handleSelect"
        @focus="isOpen = true"
        @blur="isOpen = false"
      >
        <option
          v-for="c in companies"
          :key="c.id"
          :value="c.id"
        >
          {{ c.name }}
        </option>
      </select>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import api from '../api'
import { activeCompany, setActiveCompany } from '../store/auth'

const companies = ref([])
const isOpen = ref(false)

const selectedCompany = computed(() => {
  if (activeCompany.value) return activeCompany.value
  return companies.value[0] || null
})

const companyInitial = computed(() => {
  const name = selectedCompany.value?.name?.trim()
  return name ? name.charAt(0).toUpperCase() : '?'
})

async function fetchCompanies() {
  try {
    const res = await api.get('/companies/')
    companies.value = res.data

    if (companies.value.length === 0) {
      setActiveCompany(null)
    } else if (activeCompany.value) {
      const stillExists = companies.value.find(c => c.id === activeCompany.value.id)
      if (!stillExists) {
        setActiveCompany(companies.value[0])
      }
    } else {
      setActiveCompany(companies.value[0])
    }
  } catch (e) {
    console.error('Failed to fetch companies for selector', e)
  }
}

function handleSelect(e) {
  const id = parseInt(e.target.value)
  const company = companies.value.find(c => c.id === id)
  if (!company) return
  setActiveCompany(company)
  window.location.reload() // Simplest way to ensure all data re-filters
}

onMounted(() => {
  fetchCompanies()
})
</script>

<style scoped>
.client-company-pill {
  position: relative;
  width: 52px;
  height: 52px;
  border-radius: 999px;
  border: 2px solid rgba(96, 165, 250, 0.55);
  background:
    radial-gradient(circle at 35% 25%, rgba(139, 92, 246, 0.22), transparent 45%),
    rgba(31, 41, 65, 0.82);
  box-shadow:
    0 0 20px rgba(96, 165, 250, 0.16),
    inset 0 0 18px rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(18px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  overflow: hidden;
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.client-company-pill:hover {
  border-color: #22d3ee;
  box-shadow:
    0 0 22px rgba(34, 211, 238, 0.22),
    inset 0 0 18px rgba(255, 255, 255, 0.06);
  transform: translateY(-1px);
}

.client-company-pill.is-open {
  border-color: #8b5cf6;
  box-shadow:
    0 0 24px rgba(139, 92, 246, 0.24),
    inset 0 0 18px rgba(255, 255, 255, 0.06);
}

.client-company-pill.is-empty {
  opacity: 0.62;
}

.client-company-pill__initial {
  font-size: 20px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.client-company-pill__chevron {
  width: 13px;
  height: 13px;
  color: #94a3b8;
  margin-top: -2px;
}

.client-company-pill__select {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 520px) {
  .client-company-pill {
    width: 50px;
    height: 50px;
  }

  .client-company-pill__initial {
    font-size: 19px;
  }

  .client-company-pill__chevron {
    width: 12px;
    height: 12px;
  }
}
</style>
