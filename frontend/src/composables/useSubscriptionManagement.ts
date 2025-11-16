/**
 * SOLID Principle: Interface Segregation Principle
 * Specific composable for subscription management operations
 */
import { ref, computed, type Ref } from 'vue'
import { useBilling } from './useApi'
import { useTenantStore } from '@/stores/tenant'
import type {
  SubscriptionStatus,
  SubscriptionPlan,
  ProrationCalculation,
  CouponValidation
} from '@/types/api'

interface UseSubscriptionManagementReturn {
  subscriptionStatus: Ref<SubscriptionStatus | null>
  loading: Ref<boolean>
  error: Ref<string | null>
  loadSubscription: () => Promise<void>
  refreshSubscription: () => Promise<void>
  upgradePlan: (planId: string, billingType: string) => Promise<boolean>
  cancelSubscription: (cancelImmediately: boolean) => Promise<boolean>
  reactivateSubscription: () => Promise<boolean>
  pauseSubscription: () => Promise<boolean>
  resumeSubscription: () => Promise<boolean>
  applyCoupon: (couponCode: string) => Promise<CouponValidation>
  calculateProration: (plan: SubscriptionPlan, billingType: string) => Promise<ProrationCalculation>
}

export function useSubscriptionManagement(): UseSubscriptionManagementReturn {
  const tenantStore = useTenantStore()
  const {
    getAccountSubscription,
    upgradeSubscriptionPlan,
    cancelSubscription,
    reactivateSubscription,
    pauseSubscription,
    resumeSubscription,
    applyCoupon,
    calculateProration
  } = useBilling()

  const subscriptionStatus = ref<SubscriptionStatus | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentAccount = computed(() => tenantStore.currentAccount)

  const loadSubscription = async (): Promise<void> => {
    if (!currentAccount.value?.id) return

    loading.value = true
    error.value = null

    try {
      const status = await getAccountSubscription(currentAccount.value.id)
      subscriptionStatus.value = status as SubscriptionStatus
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load subscription'
      error.value = errorMessage
      console.error('Error loading subscription:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshSubscription = async (): Promise<void> => {
    await loadSubscription()
  }

  const upgradePlan = async (planId: string, billingType: string): Promise<boolean> => {
    if (!currentAccount.value?.id) return false

    try {
      await upgradeSubscriptionPlan(currentAccount.value.id, planId, billingType as 'monthly' | 'yearly')
      await refreshSubscription() // Refresh after successful upgrade
      return true
    } catch (err: unknown) {
      console.error('Error upgrading plan:', err)
      return false
    }
  }

  const cancelSubscriptionFn = async (cancelImmediately: boolean): Promise<boolean> => {
    if (!currentAccount.value?.id) return false

    try {
      await cancelSubscription(currentAccount.value.id, cancelImmediately)
      await refreshSubscription()
      return true
    } catch (err: unknown) {
      console.error('Error canceling subscription:', err)
      return false
    }
  }

  const reactivateSubscriptionFn = async (): Promise<boolean> => {
    if (!currentAccount.value?.id) return false

    try {
      await reactivateSubscription(currentAccount.value.id)
      await refreshSubscription()
      return true
    } catch (err: unknown) {
      console.error('Error reactivating subscription:', err)
      return false
    }
  }

  const pauseSubscriptionFn = async (): Promise<boolean> => {
    if (!currentAccount.value?.id) return false

    try {
      await pauseSubscription(currentAccount.value.id)
      await refreshSubscription()
      return true
    } catch (err: unknown) {
      console.error('Error pausing subscription:', err)
      return false
    }
  }

  const resumeSubscriptionFn = async (): Promise<boolean> => {
    if (!currentAccount.value?.id) return false

    try {
      await resumeSubscription(currentAccount.value.id)
      await refreshSubscription()
      return true
    } catch (err: unknown) {
      console.error('Error resuming subscription:', err)
      return false
    }
  }

  const applyCouponFn = async (couponCode: string): Promise<CouponValidation> => {
    if (!currentAccount.value?.id) {
      return { success: false, error: 'No account selected' }
    }

    try {
      const result = await applyCoupon(currentAccount.value.id, couponCode)
      return result as CouponValidation
    } catch (err: unknown) {
      console.error('Error applying coupon:', err)
      return { success: false, error: 'Failed to apply coupon' }
    }
  }

  const calculateProrationFn = async (plan: SubscriptionPlan, billingType: string): Promise<ProrationCalculation> => {
    if (!currentAccount.value?.id) {
      return { proration_amount: 0, currency: 'usd', description: 'No account selected' }
    }

    try {
      const result = await calculateProration(currentAccount.value.id, plan.id, billingType as 'monthly' | 'yearly')
      return result as ProrationCalculation
    } catch (err: unknown) {
      console.error('Error calculating proration:', err)
      return { proration_amount: 0, currency: 'usd', description: 'Could not calculate proration' }
    }
  }

  return {
    subscriptionStatus,
    loading,
    error,
    loadSubscription,
    refreshSubscription,
    upgradePlan,
    cancelSubscription: cancelSubscriptionFn,
    reactivateSubscription: reactivateSubscriptionFn,
    pauseSubscription: pauseSubscriptionFn,
    resumeSubscription: resumeSubscriptionFn,
    applyCoupon: applyCouponFn,
    calculateProration: calculateProrationFn,
  }
}
