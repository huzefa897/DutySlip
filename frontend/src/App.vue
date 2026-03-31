<template>
  <div class="min-h-screen bg-gray-950 text-gray-100">

    <!-- Navbar -->
    <nav class="border-b border-gray-800 px-6 py-4 flex items-center gap-8">
      <span class="text-amber-400 font-mono font-bold tracking-widest text-sm uppercase">
        DutySlip
      </span>
      <router-link
        to="/"
        class="text-sm text-gray-400 hover:text-white transition-colors"
        active-class="text-white"
      >
        Entries
      </router-link>
      <router-link
        to="/dutyslips"
        class="text-sm text-gray-400 hover:text-white transition-colors"
        active-class="text-white"
      >
        Duty Slips
      </router-link>
    </nav>

    <!-- Page Content -->
    <main class="px-6 py-8 max-w-7xl mx-auto">
      <router-view />
    </main>

  </div>
</template>