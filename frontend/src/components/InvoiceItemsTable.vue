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
            v-for="trip in trips"
            :key="trip.id"
          >
            <tr class="expandable-row">
              <td class="data-table__numeric data-table__muted">
                {{ trip.date }}
              </td>
              <td>{{ trip.trip_type === 'outstation' ? 'Outstation' : 'Regular' }}</td>
              <td class="data-table__muted">
                {{ trip.car_name }}
              </td>
              <td class="data-table__numeric data-table__muted">
                {{ trip.total_kms }}
              </td>
              <td class="data-table__numeric data-table__accent">
                {{ currencySymbol }}{{ trip.row_total }}
              </td>
              <td
                class="data-table__actions"
                @click.stop
              >
                <div class="data-table__actions-group data-table__actions-group--compact">
                  <button
                    type="button"
                    class="icon-btn"
                    :aria-expanded="isTripExpanded(trip.id)"
                    aria-label="Toggle invoice item details"
                    @click="toggleTripExpanded(trip.id)"
                  >
                    <span
                      class="expand-arrow"
                      :class="{ 'expand-arrow--open': isTripExpanded(trip.id) }"
                    >⌄</span>
                  </button>
                  <RowActionMenu
                    @edit="$emit('edit', trip)"
                    @delete="$emit('delete', trip.id)"
                  />
                </div>
              </td>
            </tr>
            <tr
              v-if="isTripExpanded(trip.id)"
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
                        <span class="expanded-panel__value">{{ trip.start_kms }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">End KMs</span>
                        <span class="expanded-panel__value">{{ trip.end_kms }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Total KMs</span>
                        <span class="expanded-panel__value">{{ trip.total_kms }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="expanded-panel__section">
                    <span class="expanded-panel__section-title">Time</span>
                    <div class="expanded-panel__grid">
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Start Time</span>
                        <span class="expanded-panel__value">{{ trip.trip_type === 'outstation' ? '—' : trip.start_time }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">End Time</span>
                        <span class="expanded-panel__value">{{ trip.trip_type === 'outstation' ? '—' : trip.end_time }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Extra Hours</span>
                        <span class="expanded-panel__value">{{ trip.trip_type === 'outstation' ? '—' : trip.extra_hrs }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="expanded-panel__section">
                    <span class="expanded-panel__section-title">Charges</span>
                    <div class="expanded-panel__grid">
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Base Rate</span>
                        <span class="expanded-panel__value">{{ trip.trip_type === 'outstation' ? '—' : `${currencySymbol}${getBaseRate(trip.car)}` }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Rate</span>
                        <span class="expanded-panel__value">{{ getRateLabel(trip) }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">KM Cost</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ trip.extra_kms_amount }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Extra Hours Cost</span>
                        <span class="expanded-panel__value">{{ trip.trip_type === 'outstation' ? '—' : `${currencySymbol}${trip.extra_hrs_amount}` }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Bhatta</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ trip.driver_bhatta }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Parking</span>
                        <span class="expanded-panel__value">{{ currencySymbol }}{{ trip.parking }}</span>
                      </div>
                      <div class="expanded-panel__item">
                        <span class="expanded-panel__label">Row Total</span>
                        <span class="expanded-panel__value expanded-panel__value--accent">{{ currencySymbol }}{{ trip.row_total }}</span>
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
  trips: { type: Array, default: () => [] },
  grandTotal: { type: [String, Number], required: true },
  currencySymbol: { type: String, required: true },
  getBaseRate: { type: Function, required: true },
  getRateLabel: { type: Function, required: true },
})

defineEmits(['edit', 'delete'])

const expandedTripIds = ref([])

function isTripExpanded(tripId) {
  return expandedTripIds.value.includes(tripId)
}

function toggleTripExpanded(tripId) {
  if (isTripExpanded(tripId)) {
    expandedTripIds.value = expandedTripIds.value.filter(id => id !== tripId)
    return
  }
  expandedTripIds.value = [...expandedTripIds.value, tripId]
}
</script>
