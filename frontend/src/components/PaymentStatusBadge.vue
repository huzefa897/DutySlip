<template>
  <span
    class="status-badge"
    :class="styles[status] || styles.unpaid"
  >
    {{ labels[status] || labels.unpaid }}
  </span>
</template>

<script setup>
defineProps({ status: String })

const labels = { unpaid: 'Unpaid', paid: 'Paid' }
const styles = {
  unpaid: 'status-badge--unpaid',
  paid: 'status-badge--paid',
}
</script>
