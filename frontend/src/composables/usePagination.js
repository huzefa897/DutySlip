import { ref, computed, watch } from 'vue'

export function usePagination(sourceList, perPage = 10) {
  const currentPage = ref(1)

  watch(sourceList, () => {
    currentPage.value = 1
  })

  const totalPages = computed(() =>
    Math.max(1, Math.ceil(sourceList.value.length / perPage))
  )

  const pageStart = computed(() =>
    sourceList.value.length === 0 ? 0 : (currentPage.value - 1) * perPage + 1
  )

  const pageEnd = computed(() =>
    Math.min(currentPage.value * perPage, sourceList.value.length)
  )

  const paginated = computed(() =>
    sourceList.value.slice(pageStart.value - 1, pageEnd.value)
  )

  const hasPrev = computed(() =>
    currentPage.value > 1
  )

  const hasNext = computed(() =>
    currentPage.value < totalPages.value
  )

  function goToPage(page) {
    currentPage.value = Math.min(Math.max(page, 1), totalPages.value)
  }

  function prevPage() {
    goToPage(currentPage.value - 1)
  }

  function nextPage() {
    goToPage(currentPage.value + 1)
  }

  function reset() {
    currentPage.value = 1
  }

  return {
    paginated,
    currentPage,
    totalPages,
    pageStart,
    pageEnd,
    hasPrev,
    hasNext,
    goToPage,
    prevPage,
    nextPage,
    reset,
  }
}
