<template>
  <!-- Billing Modals Component - Single Responsibility: Modal dialogs for billing operations -->
  <div>
    <!-- Apply Coupon Modal -->
    <div
      v-if="showCouponModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Apply Coupon</h3>
          <button @click="closeCouponModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <form @submit.prevent="applyCoupon" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Coupon Code</label>
            <input
              v-model="couponCode"
              type="text"
              placeholder="Enter coupon code"
              required
              :disabled="applyingCoupon"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
          </div>

          <div v-if="couponError" class="text-sm text-red-600">
            {{ couponError }}
          </div>

          <div v-if="couponSuccess" class="text-sm text-green-600">
            Coupon applied successfully! {{- couponDiscount }}
          </div>

          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeCouponModal"
              :disabled="applyingCoupon"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="applyingCoupon || !couponCode.trim()"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ applyingCoupon ? 'Applying...' : 'Apply Coupon' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Confirm Downgrade Modal -->
    <div
      v-if="showDowngradeModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Confirm Plan Change</h3>
          <button @click="closeDowngradeModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <div class="mb-6">
          <div class="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
            <div class="flex">
              <ExclamationTriangleIcon class="h-5 w-5 text-yellow-400" />
              <div class="ml-3">
                <h4 class="text-sm font-medium text-yellow-800">Downgrade Confirmation</h4>
                <div class="mt-2 text-sm text-yellow-700">
                  <p>You are about to downgrade from <strong>{{ currentPlan?.name }}</strong> to <strong>{{ targetPlan?.name }}</strong>.</p>
                  <ul class="mt-2 list-disc pl-5 space-y-1">
                    <li>Some features may become unavailable</li>
                    <li>Your usage limits will be reduced</li>
                    <li>This change takes effect immediately</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Plan Comparison -->
          <div class="bg-gray-50 rounded-lg p-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <h5 class="font-medium text-gray-900 mb-2">Current Plan</h5>
                <div class="text-sm text-gray-600 space-y-1">
                  <div><strong>{{ currentPlan?.name }}</strong></div>
                  <div>{{ currentPlan?.max_users }} users</div>
                  <div>{{ currentPlan?.max_articles === -1 ? 'Unlimited' : currentPlan?.max_articles }} articles</div>
                  <div>{{ currentPlan?.max_storage_mb }}MB storage</div>
                </div>
              </div>
              <div>
                <h5 class="font-medium text-gray-900 mb-2">New Plan</h5>
                <div class="text-sm text-gray-600 space-y-1">
                  <div><strong>{{ targetPlan?.name }}</strong></div>
                  <div>{{ targetPlan?.max_users }} users</div>
                  <div>{{ targetPlan?.max_articles === -1 ? 'Unlimited' : targetPlan?.max_articles }} articles</div>
                  <div>{{ targetPlan?.max_storage_mb }}MB storage</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button
            @click="closeDowngradeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="confirmDowngrade"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700"
          >
            Confirm Downgrade
          </button>
        </div>
      </div>
    </div>

    <!-- Cancel Subscription Modal -->
    <div
      v-if="showCancelModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-lg w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Cancel Subscription</h3>
          <button @click="closeCancelModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <div class="mb-6">
          <div class="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <div class="flex">
              <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
              <div class="ml-3">
                <h4 class="text-sm font-medium text-red-800">Subscription Cancellation</h4>
                <div class="mt-2 text-sm text-red-700">
                  <p>Are you sure you want to cancel your subscription?</p>
                  <p class="mt-1">You will lose access to premium features and your data may be permanently deleted.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="space-y-3">
            <div>
              <label class="flex items-center">
                <input
                  v-model="cancelImmediately"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-900">Cancel immediately (lose access right away)</span>
              </label>
              <p class="text-xs text-gray-500 ml-6 mt-1">
                Uncheck to cancel at the end of the current billing period
              </p>
            </div>
            <div>
              <label class="flex items-center">
                <input
                  v-model="understandConsequences"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-2 text-sm text-gray-900">I understand the consequences of cancellation</span>
              </label>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3">
          <button
            @click="closeCancelModal"
            :disabled="cancelling"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            Keep Subscription
          </button>
          <button
            @click="confirmCancel"
            :disabled="cancelling || !understandConsequences"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ cancelling ? 'Cancelling...' : 'Cancel Subscription' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Message Modal -->
    <div
      v-if="showMessageModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <CheckCircleIcon
              v-if="messageType === 'success'"
              class="h-6 w-6 text-green-500 mr-2"
            />
            <ExclamationTriangleIcon
              v-else
              class="h-6 w-6 text-red-500 mr-2"
            />
            <h3 class="text-lg font-medium text-gray-900">{{ messageTitle }}</h3>
          </div>
          <button @click="closeMessageModal" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>

        <p class="text-gray-600 mb-4">{{ messageContent }}</p>

        <div class="flex justify-end">
          <button
            @click="closeMessageModal"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
          >
            OK
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Modal dialogs for billing operations
 * - Open/Closed: Easy to add new modal types
 * - Interface Segregation: Clean modal management interface
 * - Dependency Inversion: Uses composables for business logic
 */
import { ref, defineExpose, defineProps, defineEmits } from 'vue'
import {
  XMarkIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import { useSubscriptionManagement } from '@/composables/useSubscriptionManagement'
import type { SubscriptionPlan, CouponValidation } from '@/types/api'

// Props define the contract
interface Props {
  currentPlan?: SubscriptionPlan | null
  targetPlan?: SubscriptionPlan | null
}

const props = withDefaults(defineProps<Props>(), {
  currentPlan: null,
  targetPlan: null
})

// Emits define external communication interface
const emit = defineEmits<{
  'coupon-applied': [validation: CouponValidation]
  'plan-changed': [plan: SubscriptionPlan]
  'subscription-cancelled': []
  'modal-closed': [modalType: string]
}>()

// Composables for business logic
const { applyCoupon: applyCouponComposable, cancelSubscription } = useSubscriptionManagement()

// Modal states
const showCouponModal = ref(false)
const showDowngradeModal = ref(false)
const showCancelModal = ref(false)
const showMessageModal = ref(false)

// Form states
const couponCode = ref('')
const cancelImmediately = ref(false)
const understandConsequences = ref(false)

// Operational states
const applyingCoupon = ref(false)
const cancelling = ref(false)

// Message states
const messageTitle = ref('')
const messageContent = ref('')
const messageType = ref<'success' | 'error'>('success')
const couponError = ref('')
const couponSuccess = ref('')
const couponDiscount = ref('')

// Methods
const openCouponModal = () => {
  showCouponModal.value = true
  couponCode.value = ''
  couponError.value = ''
  couponSuccess.value = ''
}

const closeCouponModal = () => {
  showCouponModal.value = false
  couponCode.value = ''
  couponError.value = ''
  couponSuccess.value = ''
  emit('modal-closed', 'coupon')
}

const applyCoupon = async () => {
  if (!couponCode.value.trim()) return

  applyingCoupon.value = true
  couponError.value = ''
  couponSuccess.value = ''

  try {
    const result = await applyCouponComposable(couponCode.value.trim())
    if (result.success) {
      couponSuccess.value = 'Coupon applied successfully!'
      couponDiscount.value = ' Discount applied to your subscription.'
      emit('coupon-applied', result)
      // Close modal after a short delay to show success message
      setTimeout(() => {
        closeCouponModal()
      }, 1500)
    } else {
      couponError.value = result.error || 'Invalid coupon code'
    }
  } catch (err: any) {
    couponError.value = err?.message || 'Failed to apply coupon'
  } finally {
    applyingCoupon.value = false
  }
}

const openDowngradeModal = (targetPlan: SubscriptionPlan) => {
  showDowngradeModal.value = true
  // targetPlan would be set via props
}

const closeDowngradeModal = () => {
  showDowngradeModal.value = false
  emit('modal-closed', 'downgrade')
}

const confirmDowngrade = async () => {
  if (!props.targetPlan) return

  // TODO: Implement plan change logic
  emit('plan-changed', props.targetPlan)
  showMessageModal.value = true
  messageTitle.value = 'Plan Changed'
  messageContent.value = `Your plan has been changed to ${props.targetPlan.name}.`
  messageType.value = 'success'
  closeDowngradeModal()
}

const openCancelModal = () => {
  showCancelModal.value = true
  cancelImmediately.value = false
  understandConsequences.value = false
}

const closeCancelModal = () => {
  showCancelModal.value = false
  cancelImmediately.value = false
  understandConsequences.value = false
  emit('modal-closed', 'cancel')
}

const confirmCancel = async () => {
  if (!understandConsequences.value) return

  cancelling.value = true

  try {
    const success = await cancelSubscription(cancelImmediately.value)
    if (success) {
      emit('subscription-cancelled')
      showMessageModal.value = true
      messageTitle.value = 'Subscription Cancelled'
      messageContent.value = cancelImmediately.value
        ? 'Your subscription has been cancelled immediately.'
        : 'Your subscription has been cancelled and will end at the current billing period.'
      messageType.value = 'success'
      closeCancelModal()
    } else {
      showMessageModal.value = true
      messageTitle.value = 'Cancellation Failed'
      messageContent.value = 'There was an error cancelling your subscription. Please try again.'
      messageType.value = 'error'
    }
  } catch (err: any) {
    showMessageModal.value = true
    messageTitle.value = 'Cancellation Failed'
    messageContent.value = err?.message || 'There was an error cancelling your subscription.'
    messageType.value = 'error'
  } finally {
    cancelling.value = false
  }
}

const closeMessageModal = () => {
  showMessageModal.value = false
  emit('modal-closed', 'message')
}

// Expose modal control methods for parent components
defineExpose({
  openCouponModal,
  openDowngradeModal,
  openCancelModal
})
</script>
