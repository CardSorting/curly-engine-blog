<template>
  <!-- Billing Analytics Component - Single Responsibility: Display billing analytics and usage insights -->
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">Billing Analytics</h2>
        <p class="text-gray-600">Usage insights and billing overview</p>
      </div>
      <button
        @click="refreshAnalytics"
        :disabled="loading"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
      >
        <ArrowPathIcon
          v-if="!loading"
          class="h-4 w-4 mr-2"
        />
        <ArrowPathIcon
          v-else
          class="h-4 w-4 mr-2 animate-spin"
        />
        Refresh
      </button>
    </div>

    <!-- Status Overview -->
    <div v-if="analytics" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Current Status -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div
              :class="[
                'w-8 h-8 rounded-full flex items-center justify-center',
                analytics.current_status === 'active' ? 'bg-green-100' :
                analytics.current_status === 'trialing' ? 'bg-blue-100' :
                analytics.current_status === 'past_due' ? 'bg-red-100' :
                'bg-gray-100'
              ]"
            >
              <CheckCircleIcon
                v-if="analytics.current_status === 'active'"
                class="h-5 w-5 text-green-600"
              />
              <ClockIcon
                v-else-if="analytics.current_status === 'trialing'"
                class="h-5 w-5 text-blue-600"
              />
              <ExclamationTriangleIcon
                v-else-if="analytics.current_status === 'past_due'"
                class="h-5 w-5 text-red-600"
              />
              <XMarkIcon
                v-else
                class="h-5 w-5 text-gray-600"
              />
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-900">Account Status</div>
            <div
              :class="[
                'text-xs',
                analytics.current_status === 'active' ? 'text-green-600' :
                analytics.current_status === 'trialing' ? 'text-blue-600' :
                analytics.current_status === 'past_due' ? 'text-red-600' :
                'text-gray-600'
              ]"
            >
              {{ getStatusDisplay(analytics.current_status) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Total Invoices -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <DocumentTextIcon class="h-5 w-5 text-blue-600" />
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-900">Total Invoices</div>
            <div class="text-xl font-bold text-gray-900">{{ analytics.total_invoices }}</div>
          </div>
        </div>
      </div>

      <!-- Next Billing Date -->
      <div class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <CalendarIcon class="h-5 w-5 text-purple-600" />
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-900">Next Billing</div>
            <div class="text-sm text-gray-600">
              {{ analytics.next_billing_date ? formatDate(analytics.next_billing_date) : 'N/A' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Trial Days Remaining -->
      <div v-if="analytics.trial_days_remaining && analytics.trial_days_remaining > 0" class="bg-white p-6 rounded-lg border border-gray-200">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
              <ClockIcon class="h-5 w-5 text-yellow-600" />
            </div>
          </div>
          <div class="ml-4">
            <div class="text-sm font-medium text-gray-900">Trial Days Left</div>
            <div class="text-xl font-bold text-yellow-600">{{ analytics.trial_days_remaining }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Usage Statistics -->
    <div v-if="analytics" class="bg-white border border-gray-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Usage Overview</h3>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Users Usage -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium text-gray-900">Users</span>
            <span class="text-gray-600">
              {{ analytics.usage_percentages.users }}% used
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :class="[
                'h-2 rounded-full transition-all duration-300',
                analytics.usage_percentages.users > 90 ? 'bg-red-500' :
                analytics.usage_percentages.users > 70 ? 'bg-yellow-500' :
                'bg-green-500'
              ]"
              :style="{ width: Math.min(analytics.usage_percentages.users, 100) + '%' }"
            ></div>
          </div>
          <div class="text-xs text-gray-500 text-right">
            {{ getUsageText('users', analytics) }}
          </div>
        </div>

        <!-- Articles Usage -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium text-gray-900">Articles</span>
            <span class="text-gray-600">
              {{ analytics.usage_percentages.articles }}% used
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :class="[
                'h-2 rounded-full transition-all duration-300',
                analytics.usage_percentages.articles > 90 ? 'bg-red-500' :
                analytics.usage_percentages.articles > 70 ? 'bg-yellow-500' :
                'bg-green-500'
              ]"
              :style="{ width: Math.min(analytics.usage_percentages.articles, 100) + '%' }"
            ></div>
          </div>
          <div class="text-xs text-gray-500 text-right">
            {{ getUsageText('articles', analytics) }}
          </div>
        </div>

        <!-- Storage Usage -->
        <div class="space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="font-medium text-gray-900">Storage</span>
            <span class="text-gray-600">
              {{ analytics.usage_percentages.storage }}% used
            </span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div
              :class="[
                'h-2 rounded-full transition-all duration-300',
                analytics.usage_percentages.storage > 90 ? 'bg-red-500' :
                analytics.usage_percentages.storage > 70 ? 'bg-yellow-500' :
                'bg-green-500'
              ]"
              :style="{ width: Math.min(analytics.usage_percentages.storage, 100) + '%' }"
            ></div>
          </div>
          <div class="text-xs text-gray-500 text-right">
            {{ getUsageText('storage', analytics) }}
          </div>
        </div>
      </div>

      <!-- Usage Warnings -->
      <div v-if="usageWarnings.length > 0" class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div class="flex">
          <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
          <div class="ml-3">
            <h4 class="text-sm font-medium text-yellow-800">Usage Warnings</h4>
            <ul class="mt-2 text-sm text-yellow-700">
              <li v-for="warning in usageWarnings" :key="warning" class="flex items-center">
                <span class="mr-2">•</span>
                {{ warning }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Current Plan Information -->
    <div v-if="currentPlan" class="bg-white border border-gray-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-4">Current Plan</h3>
      <div class="flex items-center justify-between">
        <div>
          <h4 class="text-xl font-semibold text-gray-900">{{ currentPlan.name }}</h4>
          <p class="text-gray-600">{{ currentPlan.description }}</p>
          <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
            <span>{{ currentPlan.max_users }} users</span>
            <span>{{ currentPlan.max_articles === -1 ? 'Unlimited' : currentPlan.max_articles }} articles</span>
            <span>{{ currentPlan.max_storage_mb }}MB storage</span>
          </div>
        </div>
        <div v-if="analytics" class="text-right">
          <div class="text-2xl font-bold text-gray-900">
            ${{ billingCycle === 'yearly' ? currentPlan.yearly_price : currentPlan.monthly_price }}
          </div>
          <div class="text-sm text-gray-500">per month</div>
          <div v-if="billingCycle === 'yearly'" class="text-xs text-green-600">
            Billed ${{ currentPlan.yearly_price * 12 }}/year
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !analytics" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <span class="ml-3 text-gray-600">Loading analytics...</span>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- No Analytics State -->
    <div v-else-if="!loading && !analytics" class="text-center py-12">
      <ChartBarIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-2">No Analytics Available</h3>
      <p class="text-gray-600">Analytics will be available once you have billing activity.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Billing analytics display and usage insights
 * - Open/Closed: Easy to extend with additional metrics
 * - Interface Segregation: Clean prop/emit interface
 * - Dependency Inversion: Uses composables for business logic
 */
import { ref, computed, onMounted, watch, defineProps, defineEmits } from 'vue'
import {
  CheckCircleIcon,
  DocumentTextIcon,
  CalendarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  XMarkIcon,
  ArrowPathIcon,
  ChartBarIcon
} from '@heroicons/vue/24/outline'
import { useBillingOverview } from '@/composables/useBillingOverview'
import { useSubscriptionManagement } from '@/composables/useSubscriptionManagement'
import type { BillingAnalytics } from '@/types/api'

// Props define the contract
interface Props {
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  refreshInterval: 0 // 0 = no auto-refresh
})

// Emits define external communication interface
const emit = defineEmits<{
  'analytics-refreshed': [analytics: BillingAnalytics]
}>()

// Composables for business logic
const { analytics, loadOverview, refreshOverview } = useBillingOverview()
const { subscriptionStatus } = useSubscriptionManagement()

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)
const billingCycle = ref<'monthly' | 'yearly'>('monthly') // Default assumption

// Computed properties
const currentPlan = computed(() => subscriptionStatus.value?.subscription_plan || null)

const usageWarnings = computed(() => {
  if (!analytics.value) return []

  const warnings = []
  const percentages = analytics.value.usage_percentages

  if (percentages.users > 90) warnings.push('Users usage is over 90%')
  if (percentages.articles > 90) warnings.push('Articles usage is over 90%')
  if (percentages.storage > 90) warnings.push('Storage usage is over 90%')

  return warnings
})

// Methods
const refreshAnalytics = async () => {
  loading.value = true
  error.value = null

  try {
    await refreshOverview()
    emit('analytics-refreshed', analytics.value!)
  } catch (err: unknown) {
    const errorMessage = err instanceof Error ? err.message : 'Failed to refresh analytics'
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

const getStatusDisplay = (status: string): string => {
  return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getUsageText = (type: 'users' | 'articles' | 'storage', analytics: BillingAnalytics): string => {
  if (!subscriptionStatus.value?.usage) return ''

  const usage = subscriptionStatus.value.usage
  const maxUsage = type === 'users' ? usage.users.limit :
                    type === 'articles' ? usage.articles.limit :
                    usage.storage.limit

  const currentUsage = type === 'users' ? usage.users.current :
                       type === 'articles' ? usage.articles.current :
                       usage.storage.current

  if (type === 'storage') {
    return `${currentUsage}MB / ${maxUsage}MB`
  }

  return `${currentUsage} / ${maxUsage === -1 ? 'Unlimited' : maxUsage}`
}

// Initialize component
onMounted(() => {
  if (!analytics.value) {
    loadOverview()
  }

  // Set up auto-refresh if specified
  if (props.refreshInterval > 0) {
    setInterval(refreshAnalytics, props.refreshInterval)
  }
})

// Watch for analytics changes to emit events
watch(analytics, (newAnalytics) => {
  if (newAnalytics) {
    emit('analytics-refreshed', newAnalytics)
  }
})
</script>
