import { ref, type Ref } from 'vue'
import { apiClient } from '@/services/api/config'
import { notify } from '@kyvg/vue3-notification'
import type { ApiError } from '@/types/api'

// API parameter types
type ApiParams = Record<string, unknown>
type CreateData = Record<string, unknown>
type UpdateData = Record<string, unknown>
type CampaignData = Record<string, unknown>
type SettingsData = Record<string, unknown>

interface ApiState<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
}

export function useApi<T>() {
  const state: ApiState<T> = {
    data: ref(null),
    loading: ref(false),
    error: ref(null),
  }

  const execute = async <P extends unknown[]>(
    apiCall: (...args: P) => Promise<{ data: T }>,
    ...args: P
  ): Promise<T | null> => {
    state.loading.value = true
    state.error.value = null

    try {
      const response = await apiCall(...args)
      state.data.value = response.data
      return response.data
    } catch (error: unknown) {
      const apiError = error as ApiError
      state.error.value = apiError.message || 'An error occurred'

      // Show notification for user-visible errors
      notify({
        title: 'Error',
        text: state.error.value,
        type: 'error',
      })

      throw error
    } finally {
      state.loading.value = false
    }
  }

  const reset = () => {
    state.data.value = null
    state.loading.value = false
    state.error.value = null
  }

  return {
    ...state,
    execute,
    reset,
  }
}

// Content management composables
export function useArticles<T = unknown>() {
  const api = useApi<T>()

  const fetchArticles = (params?: ApiParams, accountSlug?: string) => {
    // Articles are fetched from the root API endpoint, not account-scoped
    const url = '/'
    return api.execute(apiClient.get, url, { params })
  }

  const fetchArticle = (slug: string, accountSlug?: string) => {
    const url = accountSlug ? `/${accountSlug}/detail/${slug}/` : `/detail/${slug}/`
    return api.execute(apiClient.get, url)
  }

  const createArticle = (data: CreateData) =>
    api.execute(apiClient.post, '/', data)

  const updateArticle = (slug: string, data: UpdateData) =>
    api.execute(apiClient.put, `/detail/${slug}/`, data)

  const deleteArticle = (slug: string) =>
    api.execute(apiClient.delete, `/detail/${slug}/`)

  const publishArticle = (slug: string) =>
    api.execute(apiClient.post, `/detail/${slug}/publish/`)

  return {
    ...api,
    fetchArticles,
    fetchArticle,
    createArticle,
    updateArticle,
    deleteArticle,
    publishArticle,
  }
}

export function useTopics<T = unknown>() {
  const api = useApi<T>()

  const fetchTopics = (params?: ApiParams, accountSlug?: string) => {
    const url = accountSlug ? `/${accountSlug}/topics/` : '/topics/'
    return api.execute(apiClient.get, url, { params })
  }

  const fetchArticlesByTopic = (slug: string, params?: ApiParams, accountSlug?: string) => {
    const url = accountSlug ? `/${accountSlug}/topics/${slug}/articles/` : `/topics/${slug}/articles/`
    return api.execute(apiClient.get, url, { params })
  }

  const createTopic = (data: CreateData) =>
    api.execute(apiClient.post, '/topics/', data)

  const updateTopic = (slug: string, data: UpdateData) =>
    api.execute(apiClient.put, `/topics/${slug}/`, data)

  const deleteTopic = (slug: string) =>
    api.execute(apiClient.delete, `/topics/${slug}/`)

  return {
    ...api,
    fetchTopics,
    fetchArticlesByTopic,
    createTopic,
    updateTopic,
    deleteTopic,
  }
}

export function usePages<T = unknown>() {
  const api = useApi<T>()

  const fetchPages = (params?: ApiParams) =>
    api.execute(apiClient.get, '/pages/', { params })

  const fetchPage = (slug: string) =>
    api.execute(apiClient.get, `/pages/${slug}/`)

  const createPage = (data: CreateData) =>
    api.execute(apiClient.post, '/pages/', data)

  const updatePage = (slug: string, data: UpdateData) =>
    api.execute(apiClient.put, `/pages/${slug}/`, data)

  const deletePage = (slug: string) =>
    api.execute(apiClient.delete, `/pages/${slug}/`)

  return {
    ...api,
    fetchPages,
    fetchPage,
    createPage,
    updatePage,
    deletePage,
  }
}

export function useMedia<T = unknown>() {
  const api = useApi<T>()

  const fetchMedia = (params?: ApiParams) =>
    api.execute(apiClient.get, '/media/', { params })

  const uploadMedia = (formData: FormData) =>
    api.execute(apiClient.post, '/media/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

  const deleteMedia = (id: string) =>
    api.execute(apiClient.delete, `/media/${id}/`)

  const getMediaStats = () =>
    api.execute(apiClient.get, '/media/stats/')

  return {
    ...api,
    fetchMedia,
    uploadMedia,
    deleteMedia,
    getMediaStats,
  }
}

export function useNewsletter<T = unknown>() {
  const api = useApi<T>()

  const subscribe = (data: { email: string; first_name?: string; last_name?: string }) =>
    api.execute(apiClient.post, '/newsletter/subscribers/subscribe/', data)

  const unsubscribe = (data: { email: string }) =>
    api.execute(apiClient.post, '/newsletter/subscribers/unsubscribe/', data)

  const getSubscribers = (params?: ApiParams) =>
    api.execute(apiClient.get, '/newsletter/subscribers/', { params })

  const getSubscriberStats = () =>
    api.execute(apiClient.get, '/newsletter/subscribers/stats/')

  const importSubscribers = (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.execute(apiClient.post, '/newsletter/subscribers/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  }

  const exportSubscribers = (params?: ApiParams) =>
    api.execute(apiClient.get, '/newsletter/subscribers/export/', { params })

  const updateSubscriber = (id: string, data: Partial<{ is_active: boolean; first_name: string; last_name: string }>) =>
    api.execute(apiClient.patch, `/newsletter/subscribers/${id}/`, data)

  const deleteSubscriber = (id: string) =>
    api.execute(apiClient.delete, `/newsletter/subscribers/${id}/`)

  return {
    ...api,
    subscribe,
    unsubscribe,
    getSubscribers,
    getSubscriberStats,
    importSubscribers,
    exportSubscribers,
    updateSubscriber,
    deleteSubscriber,
  }
}

export function useNewsletterCampaigns<T = unknown>() {
  const api = useApi<T>()

  const getCampaigns = (params?: ApiParams) =>
    api.execute(apiClient.get, '/newsletter/campaigns/', { params })

  const getCampaign = (id: string) =>
    api.execute(apiClient.get, `/newsletter/campaigns/${id}/`)

  const createCampaign = (data: CampaignData) =>
    api.execute(apiClient.post, '/newsletter/campaigns/', data)

  const updateCampaign = (id: string, data: CampaignData) =>
    api.execute(apiClient.put, `/newsletter/campaigns/${id}/`, data)

  const deleteCampaign = (id: string) =>
    api.execute(apiClient.delete, `/newsletter/campaigns/${id}/`)

  const sendCampaign = (id: string, data?: CampaignData) =>
    api.execute(apiClient.post, `/newsletter/campaigns/${id}/send/`, data)

  const getCampaignStats = (id: string) =>
    api.execute(apiClient.get, `/newsletter/campaigns/${id}/stats/`)

  const scheduleCampaign = (id: string, scheduledAt: string) =>
    api.execute(apiClient.post, `/newsletter/campaigns/${id}/schedule/`, { scheduled_at: scheduledAt })

  return {
    ...api,
    getCampaigns,
    getCampaign,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    sendCampaign,
    getCampaignStats,
    scheduleCampaign,
  }
}

export function useSeo<T = unknown>() {
  const api = useApi<T>()

  const getSeoAudit = () =>
    api.execute(apiClient.get, '/seo/audit/')

  const optimizeArticle = (articleId: string) =>
    api.execute(apiClient.post, `/articles/${articleId}/seo-optimize/`)

  const getGlobalSettings = () =>
    api.execute(apiClient.get, '/seo/settings/')

  const updateGlobalSettings = (data: SettingsData) =>
    api.execute(apiClient.put, '/seo/settings/', data)

  const generateSitemap = () =>
    api.execute(apiClient.post, '/seo/sitemap/generate/')

  const updateRobotsTxt = (content: string) =>
    api.execute(apiClient.post, '/seo/robots/', { content })

  return {
    ...api,
    getSeoAudit,
    optimizeArticle,
    getGlobalSettings,
    updateGlobalSettings,
    generateSitemap,
    updateRobotsTxt,
  }
}

export function useAnalytics<T = unknown>() {
  const api = useApi<T>()

  const getArticleAnalytics = (articleId?: string, params?: ApiParams) =>
    api.execute(apiClient.get, articleId ? `/analytics/articles/${articleId}/` : '/analytics/articles/', { params })

  const getPageViewAnalytics = (params?: ApiParams) =>
    api.execute(apiClient.get, '/analytics/pageviews/', { params })

  const getTrafficSources = (params?: ApiParams) =>
    api.execute(apiClient.get, '/analytics/traffic-sources/', { params })

  const getUserEngagement = (params?: ApiParams) =>
    api.execute(apiClient.get, '/analytics/engagement/', { params })

  const exportAnalytics = (format: 'csv' | 'pdf', params?: ApiParams) =>
    api.execute(apiClient.get, `/analytics/export/?format=${format}`, { params, responseType: 'blob' })

  return {
    ...api,
    getArticleAnalytics,
    getPageViewAnalytics,
    getTrafficSources,
    getUserEngagement,
    exportAnalytics,
  }
}

// Account and billing management composables
export function useBilling<T = unknown>() {
  const api = useApi<T>()

  const getSubscriptionPlans = () =>
    api.execute(apiClient.get, '/subscription-plans/')

  const getAccountSubscription = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/subscription_status/`)

  const getAccountBillingInfo = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/billing_info/`)

  const upgradeSubscriptionPlan = (accountId: string, planId: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/upgrade_plan/`, { plan_id: planId })

  const cancelSubscription = (accountId: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/cancel_subscription/`)

  return {
    ...api,
    getSubscriptionPlans,
    getAccountSubscription,
    getAccountBillingInfo,
    upgradeSubscriptionPlan,
    cancelSubscription,
  }
}
