<template>
  <nav class="floating-nav">
    <div class="floating-nav__inner">
      <div
        v-for="item in items"
        :key="item.label"
        class="floating-nav__item"
      >
        <router-link
          :to="item.to"
          class="floating-nav__link"
          :class="{ 'is-active': isActive(item) }"
        >
          <svg
            class="floating-nav__icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <path :d="item.icon" />
          </svg>
          <span class="floating-nav__label">{{ item.label }}</span>
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { label: 'Home', to: '/', match: ['/'], icon: 'M3 10.5 12 3l9 7.5M5 9.5V21h14V9.5' },
  { label: 'Duty Slips', to: '/duty-slips', match: ['/duty-slips', '/duty-slips/create'], icon: 'M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01' },
  { label: 'Invoices', to: '/invoices', match: ['/invoices', '/invoices/create'], dynamic: /^\/invoices\/[^/]+$/, icon: 'M7 3h7l5 5v13H7zM14 3v5h5M9 13h6M9 17h6' },
  { label: 'Cars', to: '/cars', match: ['/cars'], icon: 'M5 16l1-5 3-4h6l3 4 1 5M6 16h12M8 19h.01M16 19h.01' },
  { label: 'Companies', to: '/companies', match: ['/companies'], icon: 'M4 21V7l8-4 8 4v14M9 21V11h6v10M8 8h.01M16 8h.01' },
  { label: 'Settings', to: '/settings', match: ['/settings'], icon: 'M12 3v2.2M12 18.8V21M4.93 4.93l1.56 1.56M17.51 17.51l1.56 1.56M3 12h2.2M18.8 12H21M4.93 19.07l1.56-1.56M17.51 6.49l1.56-1.56M15.5 12A3.5 3.5 0 1 1 8.5 12A3.5 3.5 0 0 1 15.5 12z' },
]

function isActive(item) {
  if (item.match.includes(route.path)) return true
  if (item.dynamic && item.dynamic.test(route.path)) return true
  return false
}
</script>
