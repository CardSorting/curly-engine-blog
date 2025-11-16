<template>
  <AdminLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Account & Billing</h1>
        <p class="mt-2 text-gray-600">Manage your account settings, subscription, and billing information.</p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading account information...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600 mb-4">{{ error }}</p>
        <Button @click="loadInitialData" variant="primary">
          Try Again
        </Button>
      </div>

      <div v-else class="space-y-8">
        <!-- Current Subscription Status -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900 flex items-center">
              <CreditCardIcon class="h-5 w-5 mr-2" />
              Current Subscription
            </h2>
          </div>
          <div class="p-6">
            <div class="flex items-center justify-between mb-4">
              <div>
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ subscriptionStatus?.subscription_plan?.name || 'Free Trial' }}
                </h3>
                <p class="text-sm text-gray-500">
                  {{ subscriptionStatus?.subscription_status === 'trialing' ? 'Free Trial' :
                      subscriptionStatus?.subscription_status === 'active' ? 'Active Subscription' :
                      subscriptionStatus?.subscription_status || 'Inactive' }}
                </p>
              </div>
              <div class="text-right">
                <div :class="[
                  'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                  getStatusBadgeClass(subscriptionStatus?.subscription_status)
                ]">
                  {{ getStatusLabel(subscriptionStatus?.subscription_status) }}
                </div>
                <p v-if="subscriptionStatus?.trial_ends_at" class="text-xs text-gray-500 mt-1">
                  Trial ends: {{ formatDate(subscriptionStatus.trial_ends_at) }}
                </p>
                <p v-if="subscriptionStatus?.subscription_ends_at" class="text-xs text-gray-500 mt-1">
                  Renews: {{ formatDate(subscriptionStatus.subscription_ends_at) }}
                </p>
              </div>
            </div>

            <!-- Usage Stats -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Articles</h4>
                <div class="flex items-center justify-between">
                  <span class="text-2xl font-bold text-gray-900">
                    {{ subscriptionStatus?.usage?.articles?.current || 0 }}
                  </span>
                  <span class="text-sm text-gray-500">
                    of {{ subscriptionStatus?.usage?.articles?.limit || 10 }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full"
                    :style="{
                      width: `${Math.min(100, ((subscriptionStatus?.usage?.articles?.current || 0) / (subscriptionStatus?.usage?.articles?.limit || 10)) * 100)}%`
                    }"
                  ></div>
                </div>
              </div>

              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Team Members</h4>
                <div class="flex items-center justify-between">
                  <span class="text-2xl font-bold text-gray-900">
                    {{ subscriptionStatus?.usage?.users?.current || 1 }}
                  </span>
                  <span class="text-sm text-gray-500">
                    of {{ subscriptionStatus?.usage?.users?.limit || 1 }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    class="bg-green-600 h-2 rounded-full"
                    :style="{
                      width: `${Math.min(100, ((subscriptionStatus?.usage?.users?.current || 1) / (subscriptionStatus?.usage?.users?.limit || 1)) * 100)}%`
                    }"
                  ></div>
                </div>
              </div>

              <div class="bg-gray-50 rounded-lg p-4">
                <h4 class="text-sm font-medium text-gray-900 mb-2">Storage</h4>
                <div class="flex items-center justify-between">
                  <span class="text-2xl font-bold text-gray-900">
                    {{ (subscriptionStatus?.usage?.storage?.current || 0) }}MB
                  </span>
                  <span class="text-sm text-gray-500">
                    of {{ subscriptionStatus?.usage?.storage?.limit || 100 }}MB
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    class="bg-purple-600 h-2 rounded-full"
                    :style="{
                      width: `${Math.min(100, ((subscriptionStatus?.usage?.storage?.current || 0) / (subscriptionStatus?.usage?.storage?.limit || 100)) * 100)}%`
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Subscription Plans -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900 flex items-center">
              <SparklesIcon class="h-5 w-5 mr-2" />
              Available Plans
            </h2>
            <p class="text-sm text-gray-600 mt-1">Upgrade your plan to unlock more features and capabilities.</p>
          </div>
          <div class="p-6">
            <!-- Existing Loading/Empty States -->
            <div v-if="plansLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p class="mt-4 text-gray-600">Loading subscription plans...</p>
            </div>

            <div v-else-if="subscriptionPlans.length === 0" class="text-center py-8">
              <SparklesIcon class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">No plans available</h3>
              <p class="mt-1 text-sm text-gray-500">Contact support for subscription options.</p>
            </div>

            <!-- Plans Grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div
                v-for="plan in subscriptionPlans"
                :key="plan.id"
                class="border border-gray-200 rounded-lg p-6 cursor-pointer transition-all"
                :class="[
                  subscriptionStatus?.subscription_plan?.id === plan.id
                    ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500'
                    : 'hover:border-gray-300'
                ]"
                @click="selectedPlanId = plan.id"
              >
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg font-semibold text-gray-900">{{ plan.name }}</h3>
                  <div class="flex items-center">
                    <input
                      :id="`plan-${plan.id}`"
                      type="radio"
                      :value="plan.id"
                      v-model="selectedPlanId"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      :checked="subscriptionStatus?.subscription_plan?.id === plan.id"
                    />
                  </div>
                </div>

                <p class="text-sm text-gray-600 mb-4">{{ plan.description }}</p>

                <div class="mb-4">
                  <div class="text-2xl font-bold text-gray-900">
                    ${{ billingCycle === 'yearly' ? plan.yearly_price : plan.monthly_price }}
                    <span class="text-sm font-normal text-gray-500">
                      / {{ billingCycle === 'yearly' ? 'year' : 'month' }}
                    </span>
                  </div>
                  <p v-if="billingCycle === 'yearly' && plan.monthly_price > 0" class="text-xs text-green-600 mt-1">
                    Save ${{ ((plan.monthly_price * 12) - plan.yearly_price) }} yearly
                  </p>
                </div>

                <div class="space-y-2">
                  <div class="flex items-center text-sm">
                    <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                    Up to {{ plan.max_articles }} articles
                  </div>
                  <div class="flex items-center text-sm">
                    <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                    Up to {{ plan.max_users }} team members
                  </div>
                  <div class="flex items-center text-sm">
                    <CheckIcon class="h-4 w-4 text-green-500 mr-2" />
                    {{ plan.max_storage_mb }}MB storage
                  </div>
                </div>

                <div v-if="subscriptionStatus?.subscription_plan?.id === plan.id" class="mt-4 p-2 bg-blue-100 rounded-md">
                  <p class="text-xs text-blue-800 font-medium">Current Plan</p>
                </div>
              </div>
            </div>

            <!-- Billing Cycle Toggle -->
            <div v-if="subscriptionPlans.length > 0" class="mt-6 flex justify-center">
              <div class="flex items-center space-x-4">
                <button
                  @click="billingCycle = 'monthly'"
                  :class="[
                    'px-4 py-2 text-sm font-medium rounded-md',
                    billingCycle === 'monthly'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  ]"
                >
                  Monthly
                </button>
                <button
                  @click="billingCycle = 'yearly'"
                  :class="[
                    'px-4 py-2 text-sm font-medium rounded-md',
                    billingCycle === 'yearly'
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-200 text-blue-700'
                  ]"
                >
                  Yearly
                  <span class="ml-1 px-1 py-0.5 text-xs bg-green-100 text-green-800 rounded">Save 20%</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900">Manage Subscription</h2>
          </div>
          <div class="p-6">
            <div class="flex flex-col sm:flex-row gap-4">
              <Button
                v-if="selectedPlanId && selectedPlanId !== subscriptionStatus?.subscription_plan?.id"
                @click="upgradePlan"
                :loading="upgrading"
                variant="primary"
                class="flex items-center"
              >
                <SparklesIcon class="h-4 w-4 mr-2" />
                Upgrade Plan
              </Button>

              <Button
                v-if="subscriptionStatus?.subscription_status === 'active' || subscriptionStatus?.subscription_status === 'trialing'"
                @click="cancelSubscription"
                :loading="canceling"
                variant="danger"
                class="flex items-center"
              >
                <XMarkIcon class="h-4 w-4 mr-2" />
                Cancel Subscription
              </Button>

              <Button @click="refreshStatus" variant="outline">
                Refresh Status
              </Button>
            </div>

            <div v-if="selectedPlanId && selectedPlanId !== subscriptionStatus?.subscription_plan?.id" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
              <div class="flex">
                <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400 mr-3" />
                <div class="text-sm">
                  <p class="font-medium text-yellow-800">Plan Change Confirmation</p>
                  <p class="text-yellow-700 mt-1">
                    You are about to change your subscription plan. This will take effect immediately.
                    Depending on your current billing cycle, you may be charged a prorated amount.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Billing History -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-6 py-4 border-b border-gray-200">
            <h2 class="text-lg font-medium text-gray-900 flex items-center justify-between">
              <div class="flex items-center">
                <ClockIcon class="h-5 w-5 mr-2" />
                Billing History
              </div>
              <div class="flex space-x-2">
                <select
                  v-model="billingHistoryPeriod"
                  @change="loadBillingHistory"
                  class="text-sm border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="6">Last 6 months</option>
                  <option value="12">Last 12 months</option>
                  <option value="24">Last 2 years</option>
                </select>
              </div>
            </h2>
          </div>
          <div class="p-6">
            <!-- Loading State -->
            <div v-if="billingHistoryLoading" class="text-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p class="mt-4 text-gray-600">Loading billing history...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="!billingHistory || billingHistory.length === 0" class="text-center py-8">
              <ClockIcon class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">No billing history</h3>
              <p class="mt-1 text-sm text-gray-500">
                Your billing history will appear here once you have invoices.
              </p>
            </div>

            <!-- Billing History Table -->
            <div v-else>
              <div class="overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th class="relative px-6 py-3">
                        <span class="sr-only">Actions</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="invoice in billingHistory" :key="invoice.id" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ formatDate(invoice.date) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {{ invoice.description }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${{ invoice.amount.toFixed(2) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span :class="[
                          'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                          getBillingStatusClass(invoice.status)
                        ]">
                          {{ invoice.status }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button
                          @click="downloadInvoice(invoice)"
                          variant="outline"
                          size="sm"
                          class="mr-2"
                        >
                          <DocumentArrowDownIcon class="h-4 w-4 mr-1" />
                          Download
                        </Button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <div v-if="billingHistory && billingHistory.length > 0" class="flex items-center justify-between mt-6">
                <div class="text-sm text-gray-700">
                  Showing {{ (billingHistoryPage - 1) * billingHistoryPageSize + 1 }} to {{ Math.min(billingHistoryPage * billingHistoryPageSize, billingHistoryTotal) }} of {{ billingHistoryTotal }} invoices
                </div>
                <div class="flex space-x-2">
                  <Button
                    @click="billingHistoryPage = Math.max(1, billingHistoryPage - 1)"
                    :disabled="billingHistoryPage === 1"
                    variant="outline"
                    size="sm"
                  >
                    Previous
                  </Button>
                  <Button
                    @click="billingHistoryPage = Math.min(billingHistoryPages, billingHistoryPage + 1)"
                    :disabled="billingHistoryPage === billingHistoryPages"
                    variant="outline"
                    size="sm"
                  >
                    Next
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import Button from '@/components/ui/Button.vue'
import { useBilling } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import { notify } from '@kyvg/vue3-notification'
import type { SubscriptionPlan, SubscriptionStatus } from '@/types/api'
import {
  Cog6ToothIcon,
  CreditCardIcon,
  SparklesIcon,
  CheckIcon,
  XMarkIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  DocumentArrowDownIcon,
} from '@heroicons/vue/24/outline'

// Types
interface BillingHistoryItem {
  id: string
  date: string
  description: string
  amount: number
  status: 'paid' | 'pending' | 'failed' | 'refunded'
}

const router = useRouter()
const authStore = useAuthStore()
const tenantStore = useTenantStore()
const {
  getSubscriptionPlans,
  getAccountSubscription,
  upgradeSubscriptionPlan
} = useBilling()

// Reactive state
const loading = ref(true)
const plansLoading = ref(false)
const upgrading = ref(false)
const canceling = ref(false)
const error = ref<string | null>(null)
const selectedPlanId = ref<string | null>(null)
const billingCycle = ref<'monthly' | 'yearly'>('monthly')

// Billing History State
const billingHistoryLoading = ref(false)
const billingHistoryPeriod = ref('12')
const billingHistoryPage = ref(1)
const billingHistoryPageSize = ref(10)
const billingHistoryTotal = ref(0)

// Computed
const currentAccount = computed(() => tenantStore.currentAccount)
const billingHistoryPages = computed(() =>
  Math.ceil(billingHistoryTotal.value / billingHistoryPageSize.value)
)

// Data
const subscriptionStatus = ref<SubscriptionStatus | null>(null)
const subscriptionPlans = ref<SubscriptionPlan[]>([])
const billingHistory = ref<BillingHistoryItem[]>([])

// Methods
const loadInitialData = async () => {
  loading.value = true
  error.value = null

  try {
    if (!currentAccount.value?.id) {
      throw new Error('No account selected')
    }

    // Load subscription status and plans in parallel
    const [statusResponse, plansResponse] = await Promise.all([
      getAccountSubscription(currentAccount.value.id),
      getSubscriptionPlans(),
    ])

    subscriptionStatus.value = statusResponse as SubscriptionStatus
    subscriptionPlans.value = (plansResponse as SubscriptionPlan[]) || []

    // Set current plan as selected
    if (statusResponse?.subscription_plan?.id) {
      selectedPlanId.value = statusResponse.subscription_plan.id
    }
  } catch (err: any) {
    error.value = err?.message || 'Failed to load subscription data'
    console.error('Error loading subscription data:', err)
  } finally {
    loading.value = false
  }
}

const refreshStatus = async () => {
  loading.value = true
  plansLoading.value = true

  try {
    if (currentAccount.value?.id) {
      const statusResponse = await getAccountSubscription(currentAccount.value.id)
      subscriptionStatus.value = statusResponse as SubscriptionStatus
    }
  } catch (err: any) {
    notify({
      title: 'Error',
      text: 'Failed to refresh subscription status',
      type: 'error',
    })
  } finally {
    loading.value = false
    plansLoading.value = false
  }
}

const upgradePlan = async () => {
  if (!selectedPlanId.value || !currentAccount.value?.id) return

  upgrading.value = true

  try {
    await upgradeSubscriptionPlan(currentAccount.value.id, selectedPlanId.value)

    // Refresh subscription status
    await refreshStatus()

    notify({
      title: 'Success',
      text: 'Subscription plan upgraded successfully!',
      type: 'success',
    })

    // Reset selected plan (now it's the current plan)
    selectedPlanId.value = null
  } catch (err: any) {
    notify({
      title: 'Error',
      text: 'Failed to upgrade subscription plan',
      type: 'error',
    })
  } finally {
    upgrading.value = false
  }
}

const cancelSubscription = async () => {
  if (!currentAccount.value?.id) return

  // Show confirmation modal (in a real implementation, this would use a proper modal component)
  const confirmed = window.confirm(
    'Are you sure you want to cancel your subscription?\n\n' +
    'This will take effect at the end of your current billing period. ' +
    'You will still have access to all features until then.\n\n' +
    'You can reactivate your subscription at any time before the end of the billing period.'
  )

  if (!confirmed) return

  canceling.value = true

  try {
    // In a real implementation, this would call the billing API
    // await cancelSubscriptionPlan(currentAccount.value.id)

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Refresh subscription status to show changes
    await refreshStatus()

    notify({
      title: 'Subscription Cancelled',
      text: 'Your subscription has been cancelled and will end at the current billing period.',
      type: 'success',
    })
  } catch (err: any) {
    notify({
      title: 'Error',
      text: 'Failed to cancel subscription. Please contact support if the problem persists.',
      type: 'error',
    })
  } finally {
    canceling.value = false
  }
}

const getStatusBadgeClass = (status?: string) => {
  switch (status) {
    case 'trialing':
      return 'bg-blue-100 text-blue-800'
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'past_due':
      return 'bg-red-100 text-red-800'
    case 'canceled':
      return 'bg-gray-100 text-gray-800'
    case 'unpaid':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusLabel = (status?: string) => {
  switch (status) {
    case 'trialing':
      return 'Trial'
    case 'active':
      return 'Active'
    case 'past_due':
      return 'Past Due'
    case 'canceled':
      return 'Canceled'
    case 'unpaid':
      return 'Unpaid'
    default:
      return 'Inactive'
  }
}

const formatDate = (dateString?: string | null) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Billing History Methods
const loadBillingHistory = async () => {
  billingHistoryLoading.value = true
  try {
    if (!currentAccount.value?.id) return

    // In a real implementation, this would call an API endpoint like:
    // const response = await apiClient.get(`/accounts/${currentAccount.value.id}/billing-history/`, {
    //   params: {
    //     period: billingHistoryPeriod.value,
    //     page: billingHistoryPage.value,
    //     page_size: billingHistoryPageSize.value,
    //   }
    // })

    // For now, we'll populate with mock data based on the subscription status
    const mockData: BillingHistoryItem[] = []
    if (subscriptionStatus.value?.subscription_plan) {
      const plan = subscriptionStatus.value.subscription_plan
      if (!plan) return

      // Add current month's invoice if active
      if (subscriptionStatus.value.subscription_status === 'active' || subscriptionStatus.value.subscription_status === 'trialing') {
        mockData.push({
          id: 'inv-current-' + billingHistoryPeriod.value,
          date: new Date().toISOString().split('T')[0],
          description: `${plan.name} Subscription`,
          amount: billingCycle.value === 'yearly'
            ? plan.yearly_price as number || 0
            : plan.monthly_price as number || 0,
          status: 'paid',
        })
      }

      // Add some historical data if we have past invoices
      const months = parseInt(billingHistoryPeriod.value)
      for (let i = 1; i < Math.min(months, 6); i++) {
        const date = new Date()
        date.setMonth(date.getMonth() - i)
        mockData.push({
          id: `inv-${i}-${billingHistoryPeriod.value}`,
          date: date.toISOString().split('T')[0],
          description: `${plan.name} Subscription`,
          amount: billingCycle.value === 'yearly'
            ? plan.yearly_price as number || 0
            : plan.monthly_price as number || 0,
          status: 'paid',
        })
      }
    }

    // Filter by page
    const startIndex = (billingHistoryPage.value - 1) * billingHistoryPageSize.value
    const endIndex = startIndex + billingHistoryPageSize.value
    billingHistory.value = mockData.slice(startIndex, endIndex)
    billingHistoryTotal.value = mockData.length
  } catch (error) {
    console.error('Failed to load billing history:', error)
    // On error, keep empty array (handled by template)
  } finally {
    billingHistoryLoading.value = false
  }
}

const getBillingStatusClass = (status: string) => {
  switch (status) {
    case 'paid':
      return 'bg-green-100 text-green-800'
    case 'pending':
      return 'bg-yellow-100 text-yellow-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    case 'refunded':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const downloadInvoice = async (invoice: BillingHistoryItem) => {
  try {
    // In a real implementation, this would download the actual invoice PDF
    // For now, we'll show a placeholder message

    // Simulate download delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    notify({
      title: 'Invoice Download',
      text: 'Invoice download will be available in your account billing section.',
      type: 'info',
    })
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to download invoice',
      type: 'error',
    })
  }
}

onMounted(async () => {
  await loadInitialData()
  await loadBillingHistory()
})
</script>
