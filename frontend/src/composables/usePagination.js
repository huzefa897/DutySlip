import { ref, computed, watch } from 'vue'

export function usePagination(sourceList, perPage = 10) {
  const currentCount = ref(perPage)

  // reset to first page when source list changes (e.g. filters applied)
  watch(sourceList, () => {
    currentCount.value = perPage
  })

  const paginated = computed(() =>
    sourceList.value.slice(0, currentCount.value)
  )

  const hasMore = computed(() =>
    currentCount.value < sourceList.value.length
  )

  const remaining = computed(() =>
    sourceList.value.length - currentCount.value
  )

  function loadMore() {
    currentCount.value += perPage
  }

  function reset() {
    currentCount.value = perPage
  }

  return { paginated, hasMore, remaining, loadMore, reset }
}