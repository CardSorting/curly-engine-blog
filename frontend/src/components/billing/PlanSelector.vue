<template>
  <!-- Plan Selector Component - Single Responsibility: Display and manage plan selection/upgrades -->
  <div class="space-y-6">
    <!-- Current Plan Display -->
    <div v-if="currentPlan" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-blue-900">Current Plan: {{ currentPlan.name }}</h3>
          <p class="text-blue-700">{{ currentPlan.description }}</p>
        </div>
        <div class="text-right">
          <p class="text-sm text-blue-600">{{ billingCycle === 'yearly' ? 'Yearly' : 'Monthly' }}</p>
          <p class="text-lg font-bold text-blue-900">
            ${{ billingCycle === 'yearly' ? currentPlan.yearly_price : currentPlan.monthly_price }}/month
          </p>
        </div>
      </div>
    </div>

    <!-- Billing Cycle Toggle -->
    <div class="flex items-center justify-center bg-gray-100 p-1 rounded-lg w-fit">
      <button
        @click="billingCycle = 'monthly'"
        :class="[
          'px-4 py-2 rounded-md text-sm font-medium transition-colors',
          billingCycle === 'monthly' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
        ]"
      >
        Monthly
      </button>
      <button
        @click="billingCycle = 'yearly'"
        :class="[
          'px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2',
          billingCycle === 'yearly' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600 hover:text-gray-900'
        ]"
      >
        Yearly
        <span class="text-xs bg-green-100 text-green-800 px-1.5 py-0.5 rounded">Save 20%</span>
      </button>
    </div>

    <!-- Plan Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="plan in availablePlans"
        :key="plan.id"
        :class="[
          'border rounded-lg p-6 cursor-pointer transition-all hover:shadow-lg',
          selectedPlan?.id === plan.id ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-gray-300',
          currentPlan?.id === plan.id ? 'bg-blue-50' : ''
        ]"
        @click="selectPlan(plan)"
      >
        <!-- Plan Header -->
        <div class="text-center mb-4">
          <CheckCircleIcon
            v-if="currentPlan?.id === plan.id"
            class="h-6 w-6 text-blue-600 mx-auto mb-2"
          />
          <h3 class="text-xl font-semibold text-gray-900 mb-1">{{ plan.name }}</h3>
          <div class="text-3xl font-bold text-gray-900 mb-1">
            ${{ billingCycle === 'yearly' ? plan.yearly_price : plan.monthly_price }}
            <span class="text-sm text-gray-500 font-normal">/month</span>
          </div>
          <p v-if="billingCycle === 'yearly'" class="text-sm text-green-600">
            Billed ${{ plan.yearly_price * 12 }}/year
          </p>
          <p class="text-sm text-gray-600">{{ plan.description }}</p>
        </div>

        <!-- Feature List -->
        <ul class="space-y-2 text-sm text-gray-600 mb-6">
          <li class="flex items-center">
            <UserIcon class="h-4 w-4 text-gray-400 mr-2" />
            Up to {{ plan.max_users }} users
          </li>
          <li class="flex items-center">
            <DocumentTextIcon class="h-4 w-4 text-gray-400 mr-2" />
            {{ plan.max_articles === -1 ? 'Unlimited' : plan.max_articles }} articles
          </li>
          <li class="flex items-center">
            <CloudIcon class="h-4 w-4 text-gray-400 mr-2" />
            {{ plan.max_storage_mb }}MB storage
          </li>
        </ul>

        <!-- Action Button -->
        <button
          :disabled="currentPlan?.id === plan.id"
          :class="[
            'w-full py-2 px-4 rounded-md text-sm font-medium transition-colors',
            currentPlan?.id === plan.id
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : selectedPlan?.id === plan.id
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          ]"
          @click.stop="currentPlan?.id !== plan.id && selectPlan(plan)"
        >
          {{ currentPlan?.id === plan.id ? 'Current Plan' : selectedPlan?.id === plan.id ? 'Selected' : 'Select Plan' }}
        </button>
      </div>
    </div>

    <!-- Upgrade Actions -->
    <div v-if="selectedPlan && currentPlan?.id !== selectedPlan.id" class="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <div class="flex items-center justify-between">
        <div>
          <h4 class="font-medium text-gray-900">Upgrade to {{ selectedPlan.name }}</h4>
          <p class="text-sm text-gray-600">
            {{ billingCycle === 'yearly' ? 'Yearly' : 'Monthly' }} billing
            <span v-if="prorationData" class="text-green-600 ml-1">
              (Prorated: ${{ prorationData.proration_amount }})
            </span>
          </p>
        </div>
        <div class="flex gap-3">
          <button
            @click="selectedPlan = null"
            class="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          <button
            @click="confirmUpgrade"
            :disabled="upgradeLoading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowRightOnRectangleIcon v-if="!upgradeLoading" class="h-4 w-4 inline mr-2" />
            {{ upgradeLoading ? 'Processing...' : 'Confirm Upgrade' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
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
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Plan selection and upgrade management
 * - Open/Closed: Easy to extend with new plan features
 * - Interface Segregation: Clean prop/emit interface
 * - Dependency Inversion: Uses composables for business logic
 */
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import {
  CheckCircleIcon,
  UserIcon,
  DocumentTextIcon,
  CloudIcon,
  ArrowRightOnRectangleIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { useSubscriptionManagement } from '@/composables/useSubscriptionManagement'
import { useBillingData } from '@/composables/useBillingData'
import { useTenantStore } from '@/stores/tenant'
import type { SubscriptionPlan, ProrationCalculation } from '@/types/api'

// Composables for business logic
const { subscriptionStatus, upgradePlan, calculateProration } = useSubscriptionManagement()
const { plans: availablePlans, loadPlans } = useBillingData()
const tenantStore = useTenantStore()

// Props define the contract
interface Props {
  showCurrentPlan?: boolean
  allowDowngrades?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showCurrentPlan: true,
  allowDowngrades: false
})

// Emits define external communication interface
const emit = defineEmits<{
  'plan-selected': [plan: SubscriptionPlan, billingCycle: 'monthly' | 'yearly']
  'upgrade-confirmed': [plan: SubscriptionPlan, billingCycle: 'monthly' | 'yearly']
}>()

// Reactive state
const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const selectedPlan = ref<SubscriptionPlan | null>(null)
const upgradeLoading = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const prorationData = ref<ProrationCalculation | null>(null)

// Computed properties
const currentPlan = computed(() => subscriptionStatus.value?.subscription_plan || null)

// Methods
const selectPlan = async (plan: SubscriptionPlan) => {
  // Prevent selecting current plan or downgrades if not allowed
  if (currentPlan.value?.id === plan.id) return
  if (!props.allowDowngrades && plan.monthly_price < (currentPlan.value?.monthly_price || 0)) return

  selectedPlan.value = plan
  upgradeLoading.value = false

  // Emit plan selection event
  emit('plan-selected', plan, billingCycle.value)

  // Pre-calculate proration for immediate feedback
  if (calculateProration) {
    calculateProration(plan, billingCycle.value)
  }
}

const confirmUpgrade = async () => {
  if (!selectedPlan.value) return

  upgradeLoading.value = true
  error.value = null

  try {
    const success = await upgradePlan(selectedPlan.value.id, billingCycle.value)
    if (success) {
      emit('upgrade-confirmed', selectedPlan.value, billingCycle.value)
      // Reset selection after successful upgrade
      selectedPlan.value = null
    } else {
      error.value = 'Failed to upgrade plan'
    }
  } catch (err: any) {
    error.value = err?.message || 'Failed to upgrade plan'
  } finally {
    upgradeLoading.value = false
  }
}

// Watch for billing cycle changes to recalculate proration
watch(billingCycle, () => {
  if (selectedPlan.value && calculateProration) {
    calculateProration(selectedPlan.value, billingCycle.value)
  }
})

// Initialize billing cycle based on current subscription
if (currentPlan.value) {
  // TODO: Determine if current subscription is yearly or monthly
  billingCycle.value = 'monthly' // Default assumption
}
</script>
