<template>
  <!-- Billing Quick Actions Component - Single Responsibility: Display action buttons for billing operations -->
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Upgrade Plan Action -->
    <button
      v-if="canUpgrade && subscriptionStatus"
      @click="$emit('upgrade-clicked')"
      class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all text-left"
    >
      <SparklesIcon class="h-6 w-6 text-blue-600 mb-2" />
      <h3 class="font-medium text-gray-900">Upgrade Plan</h3>
      <p class="text-sm text-gray-600">Access more features</p>
    </button>

    <!-- View Invoices Action -->
    <button
      @click="$emit('billing-clicked')"
      class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:border-green-300 hover:shadow-md transition-all text-left"
    >
      <CreditCardIcon class="h-6 w-6 text-green-600 mb-2" />
      <h3 class="font-medium text-gray-900">View Invoices</h3>
      <p class="text-sm text-gray-600">Billing history & downloads</p>
    </button>

    <!-- Analytics Action -->
    <button
      @click="$emit('analytics-clicked')"
      class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all text-left"
    >
      <ChartBarIcon class="h-6 w-6 text-purple-600 mb-2" />
      <h3 class="font-medium text-gray-900">Analytics</h3>
      <p class="text-sm text-gray-600">Usage insights</p>
    </button>

    <!-- Apply Coupon Action -->
    <button
      @click="$emit('coupon-clicked')"
      class="bg-white p-4 rounded-lg shadow-sm border border-gray-200 hover:border-yellow-300 hover:shadow-md transition-all text-left"
    >
      <TagIcon class="h-6 w-6 text-yellow-600 mb-2" />
      <h3 class="font-medium text-gray-900">Apply Coupon</h3>
      <p class="text-sm text-gray-600">Discount codes</p>
    </button>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Only displays quick action buttons
 * - Open/Closed: Easy to add new action buttons without modification
 * - Interface Segregation: Simple prop interface, event-based communication
 * - Dependency Inversion: No tight coupling to parent component logic
 */
import { defineProps, defineEmits } from 'vue'
import { SparklesIcon, CreditCardIcon, ChartBarIcon, TagIcon } from '@heroicons/vue/24/outline'
import type { SubscriptionStatus } from '@/types/api'

// Props define the contract
interface Props {
  canUpgrade: boolean
  subscriptionStatus: SubscriptionStatus | null
}

defineProps<Props>()

// Emits define external communication interface
defineEmits<{
  'upgrade-clicked': []
  'billing-clicked': []
  'analytics-clicked': []
  'coupon-clicked': []
}>()
</script>
