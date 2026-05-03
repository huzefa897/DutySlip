<template>
  <span
    class="text-xs font-mono px-2 py-1 rounded"
    :class="styles[status]"
  >
    {{ labels[status] }}
  </span>
</template>

<script setup>
defineProps({ status: String })

const labels = { draft: 'Draft', finalised: 'Finalised' }
const styles = {
  draft:      'bg-gray-800 text-gray-400',
  finalised:  'bg-blue-900 text-blue-300',
}
</script>
