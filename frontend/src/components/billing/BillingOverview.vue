<template>
  <!-- Billing Overview Component - Single Responsibility: Display billing status and usage -->
  <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
    <!-- Header with subscription details -->
    <div class="flex items-center justify-between mb-4">
      <div>
        <h3 class="text-xl font-semibold text-gray-900">
          {{ subscriptionStatus?.subscription_plan?.name || 'Free Trial' }}
        </h3>
        <p class="text-sm text-gray-600 mt-1">
          {{ getStatusDescription(subscriptionStatus?.subscription_status) }}
        </p>
      </div>
      <div class="text-right">
        <div :class="[
          'inline-flex px-3 py-1 text-sm font-semibold rounded-full',
          getStatusBadgeClass(subscriptionStatus?.subscription_status)
        ]">
          {{ getStatusLabel(subscriptionStatus?.subscription_status) }}
        </div>
        <div class="mt-2 text-xs text-gray-500">
          <p v-if="subscriptionStatus?.trial_ends_at">
            Trial ends: {{ formatDate(subscriptionStatus.trial_ends_at) }}
          </p>
          <p v-if="subscriptionStatus?.subscription_ends_at && !isTrialing">
            Next billing: {{ formatDate(subscriptionStatus.subscription_ends_at) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Usage Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
      <div
        v-for="metric in usageMetrics"
        :key="metric.key"
        class="bg-white rounded-lg p-4 shadow-sm"
      >
        <div class="flex items-center justify-between mb-2">
          <h4 class="text-sm font-medium text-gray-900">{{ metric.label }}</h4>
          <component :is="metric.icon" class="h-4 w-4 text-gray-400" />
        </div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-2xl font-bold text-gray-900">
            {{ metric.current }}
          </span>
          <span class="text-sm text-gray-500">
            / {{ metric.limit }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3">
          <div
            :class="[
              'h-3 rounded-full transition-all duration-300',
              getUsageBarColor(metric.percentage)
            ]"
            :style="{ width: `${metric.percentage}%` }"
          ></div>
        </div>
        <!-- Usage warning -->
        <p v-if="metric.percentage >= 80" class="text-xs mt-2" :class="metric.percentage >= 95 ? 'text-red-600' : 'text-yellow-600'">
          {{ metric.percentage >= 95 ? 'Limit almost reached' : 'Approaching limit' }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Only displays billing overview and usage stats
 * - Open/Closed: Can be extended with new metrics without modifying existing logic
 * - Interface Segregation: Props are specific to billing overview needs
 * - Dependency Inversion: Depends on abstractions (props) not concrete implementations
 */
import { computed, defineProps } from 'vue'
import { DocumentTextIcon, UsersIcon, CpuChipIcon } from '@heroicons/vue/24/outline'
import type { SubscriptionStatus } from '@/types/api'

// Props interface defines the contract
interface Props {
  subscriptionStatus: SubscriptionStatus | null
}

const props = defineProps<Props>()

// Computed properties for business logic separation
const isTrialing = computed(() => props.subscriptionStatus?.subscription_status === 'trialing')

const usageMetrics = computed(() => {
  const status = props.subscriptionStatus
  if (!status) return []

  return [
    {
      key: 'articles',
      label: 'Articles',
      icon: DocumentTextIcon,
      current: status.usage.articles.current,
      limit: status.usage.articles.limit,
      percentage: (status.usage.articles.current / status.usage.articles.limit) * 100
    },
    {
      key: 'users',
      label: 'Team Members',
      icon: UsersIcon,
      current: status.usage.users.current,
      limit: status.usage.users.limit,
      percentage: (status.usage.users.current / status.usage.users.limit) * 100
    },
    {
      key: 'storage',
      label: 'Storage',
      icon: CpuChipIcon,
      current: `${(status.usage.storage.current)}MB`,
      limit: `${status.usage.storage.limit}MB`,
      percentage: (status.usage.storage.current / status.usage.storage.limit) * 100
    }
  ]
})

// Business logic methods
const getStatusBadgeClass = (status?: string): string => {
  switch (status) {
    case 'trialing': return 'bg-blue-100 text-blue-800'
    case 'active': return 'bg-green-100 text-green-800'
    case 'past_due': return 'bg-red-100 text-red-800'
    case 'canceled': return 'bg-gray-100 text-gray-800'
    case 'unpaid': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

const getStatusLabel = (status?: string): string => {
  switch (status) {
    case 'trialing': return 'Trial'
    case 'active': return 'Active'
    case 'past_due': return 'Past Due'
    case 'canceled': return 'Canceled'
    case 'unpaid': return 'Unpaid'
    default: return 'Inactive'
  }
}

const getStatusDescription = (status?: string): string => {
  switch (status) {
    case 'trialing': return 'Free Trial - Upgrade to unlock more features'
    case 'active': return 'Active Subscription - All features available'
    case 'past_due': return 'Payment due - Please update payment method'
    case 'canceled': return 'Subscription canceled - Limited access'
    case 'unpaid': return 'Payment failed - Service restricted'
    default: return 'No active subscription'
  }
}

const getUsageBarColor = (percentage: number): string => {
  if (percentage >= 95) return 'bg-red-500'
  if (percentage >= 80) return 'bg-yellow-500'
  return 'bg-green-500'
}

const formatDate = (dateString?: string | null): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Component emits for parent communication (Open/Closed Principle)
defineEmits<{
  refresh: []
}>()
</script>
