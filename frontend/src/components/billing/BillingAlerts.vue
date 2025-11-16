<template>
  <!-- Billing Alerts Component - Single Responsibility: Display billing alerts and notifications -->
  <div v-if="alerts && alerts.length > 0" class="mb-8">
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
      <div class="flex">
        <BellAlertIcon class="h-5 w-5 text-yellow-400 flex-shrink-0" />
        <div class="ml-3">
          <h3 class="text-sm font-medium text-yellow-800">Billing Alerts</h3>
          <div class="mt-2 text-sm text-yellow-700">
            <div
              v-for="alert in alerts"
              :key="alert.type"
              class="mb-1 flex items-start"
            >
              <ExclamationTriangleIcon
                v-if="alert.severity === 'error'"
                class="h-4 w-4 text-red-500 mt-0.5 mr-2 flex-shrink-0"
              />
              <ExclamationCircleIcon
                v-else
                class="h-4 w-4 text-yellow-500 mt-0.5 mr-2 flex-shrink-0"
              />
              <span :class="alert.severity === 'error' ? 'text-red-700 font-medium' : 'text-yellow-800'">
                {{ alert.message }}
              </span>
              <button
                v-if="alert.action_required"
                @click="handleAlertAction(alert)"
                class="ml-2 text-blue-600 hover:text-blue-800 underline text-xs"
              >
                {{ getActionText(alert) }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Only displays billing alerts
 * - Open/Closed: Can handle new alert types without modification
 * - Interface Segregation: Specific interface for alert operations
 * - Liskov Substitution: Can be replaced with different alert display implementations
 */
import { defineProps, defineEmits } from 'vue'
import { BellAlertIcon, ExclamationTriangleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import type { BillingAlert } from '@/types/api'

// Props define the contract
interface Props {
  alerts: BillingAlert[]
}

const props = defineProps<Props>()

// Emits define the communication interface
const emit = defineEmits<{
  actionClicked: [alert: BillingAlert]
}>()

// Business logic for alert handling
const getActionText = (alert: BillingAlert): string => {
  switch (alert.type) {
    case 'trial_ending':
      return 'Upgrade Now'
    case 'usage_warning':
      return 'Manage Usage'
    case 'payment_failed':
      return 'Update Payment'
    default:
      return 'Take Action'
  }
}

const handleAlertAction = (alert: BillingAlert): void => {
  emit('actionClicked', alert)
}
</script>
