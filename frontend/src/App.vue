<template>
  <div class="min-h-screen bg-gray-950 text-gray-100">

    <!-- Navbar -->
    <nav class="border-b border-gray-800 px-6 py-4 flex items-center gap-8">
      <router-link to="/" class="text-amber-400 font-mono font-bold tracking-widest text-sm uppercase">
        DutySlip
      </router-link>
      <router-link to="/entries" class="text-sm text-gray-400 hover:text-white transition-colors"
        active-class="text-white">
        Entries
      </router-link>
      <router-link to="/dutyslips" class="text-sm text-gray-400 hover:text-white transition-colors"
        active-class="text-white">
        Duty Slips
      </router-link>
      <router-link to="/cars" class="text-sm text-gray-400 hover:text-white transition-colors"
        active-class="text-white">
        Cars
      </router-link>
      <router-link to="/companies" class="text-sm text-gray-400 hover:text-white transition-colors"
            active-class="text-white">
            Companies
          </router-link>
      <div class="ml-auto">
        <router-link to="/settings" class="text-sm text-gray-400 hover:text-white transition-colors"
          active-class="text-white">
          ⚙ Settings
        </router-link>


      </div>
    </nav>

    <!-- Global Banner -->
    <div v-if="notification.message.value" class="px-6 py-3 flex items-center justify-between text-sm font-mono" :class="notification.type.value === 'success'
      ? 'bg-green-900/60 border-b border-green-700 text-green-300'
      : 'bg-red-900/60 border-b border-red-700 text-red-300'">
      <span>{{ notification.message.value }}</span>
      <button @click="clearNotification" class="text-lg leading-none opacity-60 hover:opacity-100 transition-opacity">
        ×
      </button>
    </div>

    <!-- Page Content -->
    <main class="px-6 py-8 max-w-7xl mx-auto">
      <router-view />
    </main>

  </div>
</template>

<script setup>
import { notification, clearNotification } from './store/notification'
import { onMounted } from 'vue'
import { setCurrency } from './store/currency'
import api from './api'

onMounted(async () => {
  try {
    const res = await api.get('/settings/')
    setCurrency(res.data.currency || 'USD')
  } catch (e) {
    // settings not configured yet
  }
})
</script>