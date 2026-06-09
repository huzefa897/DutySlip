<template>
  <div class="app-shell">
    <Transition name="banner-slide">
      <div
        v-if="notification.message.value"
        class="app-banner px-6 py-3 flex items-center justify-between text-sm"
        :class="notification.type.value === 'success'
          ? 'text-green-300'
          : 'text-red-300'"
      >
        <span>{{ notification.message.value }}</span>
        <button
          class="text-lg leading-none opacity-60 hover:opacity-100 transition-opacity"
          @click="clearNotification"
        >
          ×
        </button>
      </div>
    </Transition>

    <!-- Page Content -->
    <main class="app-main">
      <router-view v-slot="{ Component, route }">
        <Transition
          name="route-fade"
          mode="out-in"
        >
          <div
            :key="route.fullPath"
            class="app-route-view"
          >
            <component :is="Component" />
          </div>
        </Transition>
      </router-view>
    </main>

    <BottomNav v-if="isAuthenticated" />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import BottomNav from './components/BottomNav.vue'
import { notification, clearNotification } from './store/notification'
import { setCurrency } from './store/currency'
import { isAuthenticated } from './store/auth'
import api from './api'

async function fetchSettings() {
  if (!isAuthenticated.value) return
  try {
    const res = await api.get('/settings/')
    setCurrency(res.data.currency || 'USD')
  } catch {
    // settings not configured yet or no access
  }
}

onMounted(fetchSettings)
watch(isAuthenticated, fetchSettings)
</script>
