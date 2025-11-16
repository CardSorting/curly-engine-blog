/**
 * SOLID Principle: Interface Segregation Principle
 * Specific composable for billing data management operations
 */
import { ref, computed, type Ref } from 'vue'
import { useBilling } from './useApi'
import { useTenantStore } from '@/stores/tenant'
import type { SubscriptionPlan, Invoice, PaymentMethod } from '@/types/api'

interface UseBillingDataReturn {
  plans: Ref<SubscriptionPlan[]>
  invoices: Ref<Invoice[]>
  paymentMethods: Ref<PaymentMethod[]>
  plansLoading: Ref<boolean>
  invoicesLoading: Ref<boolean>
  methodsLoading: Ref<boolean>
  error: Ref<string | null>
  loadPlans: () => Promise<void>
  loadInvoices: (limit?: number) => Promise<void>
  loadPaymentMethods: () => Promise<void>
  refreshInvoices: () => Promise<void>
}

export function useBillingData(): UseBillingDataReturn {
  const tenantStore = useTenantStore()
  const { getSubscriptionPlans, getInvoices, getPaymentMethods } = useBilling()

  const plans = ref<SubscriptionPlan[]>([])
  const invoices = ref<Invoice[]>([])
  const paymentMethods = ref<PaymentMethod[]>([])

  const plansLoading = ref(false)
  const invoicesLoading = ref(false)
  const methodsLoading = ref(false)
  const error = ref<string | null>(null)

  const currentAccount = computed(() => tenantStore.currentAccount)

  const loadPlans = async (): Promise<void> => {
    plansLoading.value = true
    error.value = null

    try {
      const response = await getSubscriptionPlans()
      plans.value = response as SubscriptionPlan[]
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load plans'
      error.value = errorMessage
      console.error('Error loading plans:', err)
    } finally {
      plansLoading.value = false
    }
  }

  const loadInvoices = async (limit: number = 20): Promise<void> => {
    if (!currentAccount.value?.id) return

    invoicesLoading.value = true

    try {
      const response = await getInvoices(currentAccount.value.id, limit)
      invoices.value = response as Invoice[]
    } catch (err: unknown) {
      console.error('Error loading invoices:', err)
      // Don't set error here as it's not critical
    } finally {
      invoicesLoading.value = false
    }
  }

  const loadPaymentMethods = async (): Promise<void> => {
    if (!currentAccount.value?.id) return

    methodsLoading.value = true

    try {
      const response = await getPaymentMethods(currentAccount.value.id)
      paymentMethods.value = response as PaymentMethod[]
    } catch (err: unknown) {
      console.error('Error loading payment methods:', err)
      // Don't set error here as it's not critical
    } finally {
      methodsLoading.value = false
    }
  }

  const refreshInvoices = async (): Promise<void> => {
    const currentLength = invoices.value.length
    await loadInvoices(currentLength || 20)
  }

  return {
    plans,
    invoices,
    paymentMethods,
    plansLoading,
    invoicesLoading,
    methodsLoading,
    error,
    loadPlans,
    loadInvoices,
    loadPaymentMethods,
    refreshInvoices,
  }
}
