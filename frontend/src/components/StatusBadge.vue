<template>
  <span
    class="status-badge"
    :class="styles[status]"
  >
    {{ labels[status] }}
  </span>
</template>

<script setup>
defineProps({ status: String })

const labels = { draft: 'Draft', finalised: 'Finalised' }
const styles = {
  draft: 'status-badge--draft',
  finalised: 'status-badge--finalised',
}
</script>
