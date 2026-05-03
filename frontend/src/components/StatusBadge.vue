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

const labels = { draft: 'Draft', finalised: 'UnPaid / Finalised', paid: 'Paid' }
const styles = {
  draft:      'bg-gray-800 text-gray-400',
  finalised:  'bg-blue-900 text-blue-300',
  paid:       'bg-green-900 text-green-400',
}
</script>