<template>
  <!--
    Refactored SettingsView using SOLID Principles:
    - Single Responsibility: This view orchestrates billing components without owning business logic
    - Open/Closed: New billing features can be added by composing new components
    - Liskov Substitution: Components are interchangeable and follow consistent interfaces
    - Interface Segregation: Each component has specific, focused interfaces
    - Dependency Inversion: Depends on abstractions (composables) not concrete implementations
  -->
  <AdminLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Account & Billing</h1>
        <p class="mt-2 text-gray-600">Manage your account settings, subscription, and billing information with industry-standard features.</p>
      </div>

      <!-- Loading State -->
      <div v-if="billingOverview.loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading billing information...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="billingOverview.error" class="text-center py-12">
        <div class="text-red-600 mb-4">{{ billingOverview.error }}</div>
        <Button @click="handleRefresh" variant="primary">
          Try Again
        </Button>
      </div>

      <!-- Main Billing Dashboard -->
      <div v-else class="space-y-8">
        <!-- SOLID Components: Each handles one responsibility -->
        <BillingAlerts
          :alerts="billingOverview.alerts.value"
          @action-clicked="handleAlertAction"
          @dismiss-alert="handleDismissAlert"
        />

        <!-- Tabbed Interface -->
        <div class="bg-white shadow rounded-lg">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex space-x-8 px-6" aria-label="Billing Tabs">
              <BillingTabButton
                v-for="tab in tabs"
                :key="tab.id"
                :tab="tab"
                :active="activeTab === tab.id"
                @click="activeTab = tab.id"
              />
            </nav>
          </div>

          <div class="p-6">
            <!-- Overview Tab - Uses composed components -->
            <div v-if="activeTab === 'overview'" class="space-y-6">
              <BillingOverview
                :subscription-status="subscriptionStatus"
                @refresh="handleRefresh"
              />

              <!-- Quick Actions - Following Open/Closed principle -->
              <BillingQuickActions
                :can-upgrade="canUpgrade"
                :subscription-status="subscriptionStatus"
                @upgrade-clicked="switchToPlansTab"
                @billing-clicked="activeTab = 'billing'"
                @analytics-clicked="activeTab = 'analytics'"
                @coupon-clicked="handleCouponAction"
              />
            </div>

            <!-- Plans Tab -->
            <div v-if="activeTab === 'plans'">
              <PlanSelector
                :plans="subscriptionPlans"
                :subscription-status="subscriptionStatus"
                :billing-cycle="billingCycle"
                @billing-cycle-changed="billingCycle = $event"
                @plan-selected="handlePlanSelection"
                @upgrade-confirmed="handleUpgradePlan"
              />
            </div>

            <!-- Billing Tab -->
            <div v-if="activeTab === 'billing'">
              <InvoiceHistory
                :invoices="invoices"
                :loading="invoicesLoading"
                @load-more="loadMoreInvoices"
                @download-invoice="handleDownloadInvoice"
              />
            </div>

            <!-- Analytics Tab -->
            <div v-if="activeTab === 'analytics'">
              <BillingAnalytics
                :analytics="billingOverview.analytics.value"
                @refresh="billingOverview.refreshOverview()"
              />
            </div>

            <!-- Settings Tab -->
            <div v-if="activeTab === 'settings'">
              <BillingSettings
                :subscription-status="subscriptionStatus"
                :can-cancel="canCancel"
                :can-reactivate="canReactivate"
                :can-pause="canPause"
                :payment-methods="paymentMethods"
                @cancel-subscription="handleCancelSubscription"
                @reactivate-subscription="handleReactivateSubscription"
                @pause-subscription="handlePauseSubscription"
                @resume-subscription="handleResumeSubscription"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Modals - Could be extracted to separate components following SRP -->
      <BillingModals
        :show-proration-modal="showProrationModal"
        :show-cancel-modal="showCancelConfirm"
        :show-pause-modal="showPauseModal"
        :show-coupon-modal="showCouponModal"
        :proration-calculation="prorationCalculation"
        :cancel-immediately="cancelImmediately"
        @confirm-upgrade="handleConfirmUpgrade"
        @cancel-upgrade="showProrationModal = false"
        @confirm-cancel="handleConfirmCancel"
        @cancel-cancel="showCancelConfirm = false"
        @confirm-pause="handleConfirmPause"
        @cancel-pause="showPauseModal = false"
        @apply-coupon="handleApplyCoupon"
        @cancel-coupon="showCouponModal = false"
      />
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
/**
 * SOLID Refactored SettingsView:
 * - Single Responsibility: Orchestrates billing components and state management
 * - Open/Closed: New billing features added via component composition
 * - Liskov Substitution: Components follow consistent interfaces
 * - Interface Segregation: Specific composables for specific billing operations
 * - Dependency Inversion: Depends on abstractions (composables) not concrete implementations
 */
import { ref, computed, onMounted, provide } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import Button from '@/components/ui/Button.vue'
import { notify } from '@kyvg/vue3-notification'

// SOLID Components - Each with single responsibility
import BillingAlerts from '@/components/billing/BillingAlerts.vue'
import BillingOverview from '@/components/billing/BillingOverview.vue'
import BillingQuickActions from '@/components/billing/BillingQuickActions.vue'
import BillingTabButton from '@/components/billing/BillingTabButton.vue'
import PlanSelector from '@/components/billing/PlanSelector.vue'
import InvoiceHistory from '@/components/billing/InvoiceHistory.vue'
import BillingAnalytics from '@/components/billing/BillingAnalytics.vue'
import BillingSettings from '@/components/billing/BillingSettings.vue'
import BillingModals from '@/components/billing/BillingModals.vue'

// SOLID Composables - Interface Segregation Principle
import { useBillingOverview } from '../../composables/useBillingOverview'
import { useSubscriptionManagement } from '../../composables/useSubscriptionManagement'
import { useBillingData } from '../../composables/useBillingData'

import type {
  SubscriptionStatus,
  SubscriptionPlan,
  Invoice,
  PaymentMethod,
  ProrationCalculation
} from '@/types/api'

// Icons - Could be abstracted to a shared icons module
import {
  EyeIcon,
  SparklesIcon,
  CreditCardIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline'

// =============== STATE MANAGEMENT (Single Responsibility) ===============

// Tab management
type TabId = 'overview' | 'plans' | 'billing' | 'analytics' | 'settings'

const activeTab = ref<TabId>('overview')
const tabs = [
  { id: 'overview' as TabId, name: 'Overview', icon: EyeIcon },
  { id: 'plans' as TabId, name: 'Plans', icon: SparklesIcon },
  { id: 'billing' as TabId, name: 'Billing', icon: CreditCardIcon },
  { id: 'analytics' as TabId, name: 'Analytics', icon: ChartBarIcon },
  { id: 'settings' as TabId, name: 'Settings', icon: Cog6ToothIcon },
]

// SOLID Composables - Dependency Inversion Principle
const billingOverview = useBillingOverview()
const subscriptionManagement = useSubscriptionManagement()
const billingData = useBillingData()

// Local state for UI orchestration
const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const selectedPlanId = ref<string | null>(null)

// Modal states
const showProrationModal = ref(false)
const showCancelConfirm = ref(false)
const showPauseModal = ref(false)
const showCouponModal = ref(false)
const cancelImmediately = ref(false)
const prorationCalculation = ref<ProrationCalculation | null>(null)

// =============== COMPUTED PROPERTIES (Business Logic Separation) ===============

// Data composition from composables
const subscriptionStatus = computed(() => subscriptionManagement.subscriptionStatus.value)
const subscriptionPlans = computed(() => billingData.plans.value)
const invoices = computed(() => billingData.invoices.value)
const invoicesLoading = computed(() => billingData.invoicesLoading.value)
const paymentMethods = computed(() => billingData.paymentMethods.value)

// Business logic computed properties
const canUpgrade = computed(() =>
  subscriptionStatus.value?.subscription_status === 'trialing' ||
  subscriptionStatus.value?.subscription_status === 'active' ||
  subscriptionStatus.value?.subscription_status === 'past_due'
)

const canCancel = computed(() =>
  subscriptionStatus.value?.subscription_status === 'active' ||
  subscriptionStatus.value?.subscription_status === 'trialing'
)

const canReactivate = computed(() =>
  subscriptionStatus.value?.subscription_status === 'canceled'
)

const canPause = computed(() =>
  subscriptionStatus.value?.subscription_status === 'active'
)

// =============== LIFECYCLE METHODS ===============

onMounted(async () => {
  await Promise.all([
    billingOverview.loadOverview(),
    billingData.loadPlans(),
    billingData.loadInvoices(20),
    billingData.loadPaymentMethods(),
    subscriptionManagement.loadSubscription(),
  ])
})

// =============== EVENT HANDLERS (Single Responsibility) ===============

const handleRefresh = async () => {
  await Promise.all([
    billingOverview.refreshOverview(),
    billingData.refreshInvoices(),
    subscriptionManagement.refreshSubscription(),
  ])
}

const handleAlertAction = (alert: any) => {
  // Route alert actions to appropriate tabs/handlers
  switch (alert.type) {
    case 'trial_ending':
      activeTab.value = 'plans'
      break
    case 'usage_warning':
      activeTab.value = 'analytics'
      break
    case 'payment_failed':
      activeTab.value = 'settings'
      break
  }
}

const handleDismissAlert = (alert: any) => {
  // Handle alert dismissal - could be persisted to backend
  console.log('Alert dismissed:', alert)
}

const switchToPlansTab = () => {
  activeTab.value = 'plans'
}

// Plan management
const handlePlanSelection = (plan: SubscriptionPlan) => {
  selectedPlanId.value = plan.id
}

const handleUpgradePlan = async (plan: SubscriptionPlan) => {
  // Calculate proration first (Open/Closed principle - extensible)
  await calculateProration(plan)
  selectedPlanId.value = plan.id
  showProrationModal.value = true
}

const handleConfirmUpgrade = async () => {
  if (!selectedPlanId.value) return

  // Use composable for business logic (Dependency Inversion)
  const success = await subscriptionManagement.upgradePlan(
    selectedPlanId.value,
    billingCycle.value
  )

  if (success) {
    showProrationModal.value = false
    selectedPlanId.value = null
    notify({
      title: 'Success',
      text: 'Plan upgraded successfully!',
      type: 'success',
    })
    await handleRefresh()
  }
}

// Invoice management
const loadMoreInvoices = () => {
  const currentLength = invoices.value.length
  billingData.loadInvoices(currentLength + 20)
}

const handleDownloadInvoice = (invoice: Invoice) => {
  // Open invoice URL or trigger download
  if (invoice.hosted_invoice_url) {
    window.open(invoice.hosted_invoice_url, '_blank')
  } else if (invoice.invoice_pdf) {
    // Create download link
    const link = document.createElement('a')
    link.href = invoice.invoice_pdf
    link.download = `invoice-${invoice.id}.pdf`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// Subscription management
const handleCancelSubscription = () => {
  showCancelConfirm.value = true
}

const handleConfirmCancel = async () => {
  const success = await subscriptionManagement.cancelSubscription(cancelImmediately.value)
  if (success) {
    showCancelConfirm.value = false
    notify({
      title: 'Subscription Cancelled',
      text: `Your subscription has been cancelled${cancelImmediately.value ? ' immediately' : ' at the end of the billing period'}.`,
      type: 'success',
    })
    await handleRefresh()
  }
}

const handleReactivateSubscription = async () => {
  const success = await subscriptionManagement.reactivateSubscription()
  if (success) {
    notify({
      title: 'Subscription Reactivated',
      text: 'Your subscription has been reactivated successfully.',
      type: 'success',
    })
    await handleRefresh()
  }
}

const handlePauseSubscription = () => {
  showPauseModal.value = true
}

const handleConfirmPause = async () => {
  const success = await subscriptionManagement.pauseSubscription()
  if (success) {
    showPauseModal.value = false
    notify({
      title: 'Subscription Paused',
      text: 'Your subscription has been paused.',
      type: 'success',
    })
    await handleRefresh()
  }
}

const handleResumeSubscription = async () => {
  const success = await subscriptionManagement.resumeSubscription()
  if (success) {
    notify({
      title: 'Subscription Resumed',
      text: 'Your subscription has been resumed.',
      type: 'success',
    })
    await handleRefresh()
  }
}

// Coupon management
const handleCouponAction = () => {
  showCouponModal.value = true
}

const handleApplyCoupon = async (couponCode: string) => {
  const result = await subscriptionManagement.applyCoupon(couponCode)
  if (result.success) {
    showCouponModal.value = false
    notify({
      title: 'Coupon Applied',
      text: 'Discount has been applied to your subscription.',
      type: 'success',
    })
    await handleRefresh()
  } else {
    notify({
      title: 'Invalid Coupon',
      text: result.error || 'Could not apply coupon.',
      type: 'error',
    })
  }
}

// Utility methods (could be extracted to shared utilities)
const calculateProration = async (plan: SubscriptionPlan) => {
  if (!subscriptionStatus.value) return

  prorationCalculation.value = await subscriptionManagement.calculateProration(
    plan,
    billingCycle.value
  )
}

// Dependency Injection - Provide context to child components (Dependency Inversion)
provide('billingContext', {
  subscriptionStatus,
  billingCycle,
  canUpgrade,
  canCancel,
  canReactivate,
  canPause,
})
</script>

<style scoped>
/* Component-specific styles could go here */
</style>
