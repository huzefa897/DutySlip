<template>
  <section class="table-card">
    <div class="table-shell">
      <table class="data-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Car</th>
            <th>Total KMs</th>
            <th>Row Total</th>
            <th class="data-table__actions">
              Actions
            </th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="entry in entries"
            :key="entry.id"
          >
            <tr class="expandable-row">
              <td class="data-table__numeric data-table__muted">
                {{ entry.date }}
              </td>
              <td>{{ entry.entry_type === 'outstation' ? 'Outstation' : 'Regular' }}</td>
              <td class="data-table__muted">
                {{ entry.car_name }}
              </td>
              <td class="data-table__numeric data-table__muted">
                {{ entry.total_kms }}
              </td>
              <td class="data-table__numeric data-table__accent">
                {{ currencySymbol }}{{ entry.row_total }}
              </td>
              <td
                class="data-table__actions"
                @click.stop
              >
                <div class="data-table__actions-group data-table__actions-group--compact">
                  <button
                    type="button"
                    class="icon-btn"
                    :aria-expanded="isEntryExpanded(entry.id)"
                    aria-label="Toggle invoice item details"
                    @click="toggleEntryExpanded(entry.id)"
                  >
                    <span
                      class="expand-arrow"
                      :class="{ 'expand-arrow--open': isEntryExpanded(entry.id) }"
                    >⌄</span>
                  </button>
                  <RowActionMenu
                    @edit="$emit('edit', entry)"
                    @delete="$emit('delete', entry.id)"
                  />
                </div>
              </td>
            </tr>
            <tr
              v-if="isEntryExpanded(entry.id)"
              class="expanded-row"
            >
              <td
                colspan="6"
                class="expanded-row__cell"
              >
                <div class="expanded-panel">
                  <div class="expanded-panel__section">
                    <span class="expanded-panel__section-title">Distance</span>
                    <div class="expanded-panel__grid">
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Start KMs</span>
                        <span class="expanded-panel__value">{{ entry.start_kms }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">End KMs</span>
                        <span class="expanded-panel__value">{{ entry.end_kms }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Total KMs</span>
                        <span class="expanded-panel__value">{{ entry.total_kms }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="expanded-panel__section">
                    <span class="expanded-panel__section-title">Time</span>
                    <div class="expanded-panel__grid">
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Start Time</span>
                        <span class="expanded-panel__value">{{ entry.entry_type === 'outstation' ? '—' : entry.start_time }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">End Time</span>
                        <span class="expanded-panel__value">{{ entry.entry_type === 'outstation' ? '—' : entry.end_time }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Extra Hours</span>
                        <span class="expanded-panel__value">{{ entry.entry_type === 'outstation' ? '—' : entry.extra_hrs }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="expanded-panel__section">
                    <span class="expanded-panel__section-title">Charges</span>
                    <div class="expanded-panel__grid">
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Base Rate</span>
                        <span class="expanded-panel__value">{{ entry.entry_type === 'outstation' ? '—' : `${currencySymbol}${getBaseRate(entry.car)}` }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Rate</span>
                        <span class="expanded-panel__value">{{ getRateLabel(entry) }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">KM Cost</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ entry.extra_kms_amount }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Extra Hours Cost</span>
                        <span class="expanded-panel__value">{{ entry.entry_type === 'outstation' ? '—' : `${currencySymbol}${entry.extra_hrs_amount}` }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Bhatta</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ entry.driver_bhatta }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Parking</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ entry.parking }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Row Total</span>
                        <span class="expanded-panel__value expanded-panel__value--accent">{{ currencySymbol }}{{ entry.row_total }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
        <tfoot>
          <tr>
            <td
              colspan="5"
              class="data-table__actions"
            >
              GRAND TOTAL
            </td>
            <td class="data-table__numeric data-table__accent">
              {{ currencySymbol }}{{ grandTotal }}
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import RowActionMenu from './RowActionMenu.vue'

defineProps({
  entries: { type: Array, default: () => [] },
  grandTotal: { type: [String, Number], required: true },
  currencySymbol: { type: String, required: true },
  getBaseRate: { type: Function, required: true },
  getRateLabel: { type: Function, required: true },
})

defineEmits(['edit', 'delete'])

const expandedEntryIds = ref([])

function isEntryExpanded(entryId) {
  return expandedEntryIds.value.includes(entryId)
}

function toggleEntryExpanded(entryId) {
  if (isEntryExpanded(entryId)) {
    expandedEntryIds.value = expandedEntryIds.value.filter(id => id !== entryId)
    return
  }
  expandedEntryIds.value = [...expandedEntryIds.value, entryId]
}
</script>
