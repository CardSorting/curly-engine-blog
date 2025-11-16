/**
 * SOLID Principle: Interface Segregation Principle
 * Specific composable for billing overview operations
 */
import { ref, computed, type Ref } from 'vue'
import { useBilling } from './useApi'
import { useTenantStore } from '@/stores/tenant'
import type { BillingAnalytics, BillingAlert } from '@/types/api'

interface UseBillingOverviewReturn {
  analytics: Ref<BillingAnalytics | null>
  alerts: Ref<BillingAlert[]>
  loading: Ref<boolean>
  error: Ref<string | null>
  loadOverview: () => Promise<void>
  refreshOverview: () => Promise<void>
}

export function useBillingOverview(): UseBillingOverviewReturn {
  const tenantStore = useTenantStore()
  const { getBillingAnalytics, getBillingAlerts } = useBilling()

  const analytics = ref<BillingAnalytics | null>(null)
  const alerts = ref<BillingAlert[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const currentAccount = computed(() => tenantStore.currentAccount)

  const loadOverview = async (): Promise<void> => {
    if (!currentAccount.value?.id) return

    loading.value = true
    error.value = null

    try {
      const [analyticsResponse, alertsResponse] = await Promise.all([
        getBillingAnalytics(currentAccount.value.id),
        getBillingAlerts(currentAccount.value.id)
      ])

      analytics.value = analyticsResponse as BillingAnalytics
      alerts.value = alertsResponse as BillingAlert[]
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load billing overview'
      error.value = errorMessage
      console.error('Error loading billing overview:', err)
    } finally {
      loading.value = false
    }
  }

  const refreshOverview = async (): Promise<void> => {
    await loadOverview()
  }

  return {
    analytics,
    alerts,
    loading,
    error,
    loadOverview,
    refreshOverview,
  }
}
