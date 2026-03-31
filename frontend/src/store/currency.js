import { ref, computed } from 'vue'

const currency = ref('USD')

export const currencySymbol = computed(() =>
  currency.value === 'INR' ? '₹' : '$'
)

export function setCurrency(val) {
  currency.value = val
}