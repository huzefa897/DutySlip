<template>
  <span
    class="text-xs font-mono px-2 py-1 rounded"
    :class="styles[status] || styles.unpaid"
  >
    {{ labels[status] || labels.unpaid }}
  </span>
</template>

<script setup>
defineProps({ status: String })

const labels = { unpaid: 'Unpaid', paid: 'Paid' }
const styles = {
  unpaid: 'bg-amber-900/50 text-amber-300',
  paid:   'bg-green-900 text-green-400',
}
</script>
