import { ref, type Ref } from 'vue'
import { apiClient } from '@/services/api/config'
import { notify } from '@kyvg/vue3-notification'
import type {
  ApiError,
  MediaUploadResponse,
  PageViewAnalytics,
  TopicResponse,
  ArticleResponse,
  PageViewResponse,
  Article,
  Page,
  Media,
  PaginatedResponse
} from '@/types/api'

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

// Fix: Remove type parameters from useArticles - it always returns PaginatedResponse
export function useArticles() {
  const fetchArticlesApi = useApi<PaginatedResponse<Article>>()
  const fetchArticleApi = useApi<ArticleResponse>()

  const fetchArticles = (params?: ApiParams, _accountSlug?: string) => {
    // Articles are fetched from the root API endpoint, not account-scoped
    const url = '/'
    return fetchArticlesApi.execute(apiClient.get, url, { params })
  }

  const fetchArticle = (slug: string, accountSlug?: string) => {
    const url = accountSlug ? `/${accountSlug}/detail/${slug}/` : `/detail/${slug}/`
    return fetchArticleApi.execute(apiClient.get, url)
  }

  const createArticle = (data: CreateData) =>
    useApi().execute(apiClient.post, '/', data)

  const updateArticle = (slug: string, data: UpdateData) =>
    useApi().execute(apiClient.put, `/detail/${slug}/`, data)

  const deleteArticle = (slug: string) =>
    useApi().execute(apiClient.delete, `/detail/${slug}/`)

  const publishArticle = (slug: string) =>
    useApi().execute(apiClient.post, `/detail/${slug}/publish/`)

  return {
    // Separate loading states
    loadingArticles: fetchArticlesApi.loading,
    loadingArticle: fetchArticleApi.loading,
    loading: fetchArticlesApi.loading || fetchArticleApi.loading,

    // Separate error states
    errorArticles: fetchArticlesApi.error,
    errorArticle: fetchArticleApi.error,
    error: fetchArticlesApi.error || fetchArticleApi.error,

    // Separate data properties
    articlesData: fetchArticlesApi.data,
    articleData: fetchArticleApi.data,
    data: fetchArticlesApi.data || fetchArticleApi.data, // Keep for backward compatibility

    fetchArticles,
    fetchArticle,
    createArticle,
    updateArticle,
    deleteArticle,
    publishArticle,
  }
}

// Fix: Remove type parameters from useTopics - it returns TopicResponse with results array
export function useTopics() {
  const fetchTopicsApi = useApi<TopicResponse>()
  const api = useApi()

  const fetchTopics = (params?: ApiParams, accountSlug?: string) => {
    const url = accountSlug ? `/${accountSlug}/topics/` : '/topics/'
    return fetchTopicsApi.execute(apiClient.get, url, { params })
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

export function usePages() {
  const fetchPagesApi = useApi<PaginatedResponse<Page>>()
  const fetchPageApi = useApi<PageViewResponse>()

  const fetchPages = (params?: ApiParams) =>
    fetchPagesApi.execute(apiClient.get, '/pages/', { params })

  const fetchPage = (slug: string) =>
    fetchPageApi.execute(apiClient.get, `/pages/${slug}/`)

  const createPage = (data: CreateData) =>
    useApi().execute(apiClient.post, '/pages/', data)

  const updatePage = (slug: string, data: UpdateData) =>
    useApi().execute(apiClient.put, `/pages/${slug}/`, data)

  const deletePage = (slug: string) =>
    useApi().execute(apiClient.delete, `/pages/${slug}/`)

  return {
    loading: fetchPagesApi.loading || fetchPageApi.loading,
    error: fetchPagesApi.error || fetchPageApi.error,
    fetchPages,
    fetchPage,
    createPage,
    updatePage,
    deletePage,
  }
}

export function useMedia() {
  const fetchMediaApi = useApi<PaginatedResponse<Media>>()
  const uploadMediaApi = useApi<MediaUploadResponse>()

  const fetchMedia = (params?: ApiParams) =>
    fetchMediaApi.execute(apiClient.get, '/media/', { params })

  const uploadMedia = (formData: FormData) =>
    uploadMediaApi.execute(apiClient.post, '/media/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

  const deleteMedia = (id: string) =>
    useApi().execute(apiClient.delete, `/media/${id}/`)

  const getMediaStats = () =>
    useApi().execute(apiClient.get, '/media/stats/')

  return {
    loading: fetchMediaApi.loading || uploadMediaApi.loading,
    error: fetchMediaApi.error || uploadMediaApi.error,
    data: fetchMediaApi.data || uploadMediaApi.data,
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

export function useAnalytics() {
  const getPageViewAnalyticsApi = useApi<PageViewAnalytics>()
  const getArticleAnalyticsApi = useApi<unknown>()

  const getArticleAnalytics = (articleId?: string, params?: ApiParams) =>
    getArticleAnalyticsApi.execute(apiClient.get, articleId ? `/analytics/articles/${articleId}/` : '/analytics/articles/', { params })

  const getPageViewAnalytics = (params?: ApiParams) =>
    getPageViewAnalyticsApi.execute(apiClient.get, '/analytics/pageviews/', { params })

  const getTrafficSources = (params?: ApiParams) =>
    useApi().execute(apiClient.get, '/analytics/traffic-sources/', { params })

  const getUserEngagement = (params?: ApiParams) =>
    useApi().execute(apiClient.get, '/analytics/engagement/', { params })

  const exportAnalytics = (format: 'csv' | 'pdf', params?: ApiParams) =>
    useApi().execute(apiClient.get, `/analytics/export/?format=${format}`, { params, responseType: 'blob' })

  return {
    loading: getPageViewAnalyticsApi.loading,
    error: getPageViewAnalyticsApi.error,
    getArticleAnalytics,
    getPageViewAnalytics,
    getTrafficSources,
    getUserEngagement,
    exportAnalytics,
  }
}

// Account and billing management composables - Industry Standard Features
export function useBilling<T = unknown>() {
  const api = useApi<T>()

  // Core Subscription Management
  const getSubscriptionPlans = () =>
    api.execute(apiClient.get, '/subscription-plans/')

  const getAccountSubscription = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/subscription_status/`)

  const getAccountBillingInfo = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/billing_info/`)

  const upgradeSubscriptionPlan = (accountId: string, planId: string, billingType: 'monthly' | 'yearly' = 'monthly') =>
    api.execute(apiClient.post, `/accounts/${accountId}/upgrade_plan/`, {
      plan_id: planId,
      billing_type: billingType
    })

  // Subscription Lifecycle Management
  const cancelSubscription = (accountId: string, cancelImmediately: boolean = false) =>
    api.execute(apiClient.post, `/accounts/${accountId}/cancel_subscription/`, {
      cancel_immediately: cancelImmediately
    })

  const reactivateSubscription = (accountId: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/reactivate_subscription/`)

  const pauseSubscription = (accountId: string, reason?: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/pause_subscription/`, { reason })

  const resumeSubscription = (accountId: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/resume_subscription/`)

  // Invoice Management
  const getInvoices = (accountId: string, limit: number = 20) =>
    api.execute(apiClient.get, `/accounts/${accountId}/invoices/`, { params: { limit } })

  // Billing Analytics & Intelligence
  const getBillingAnalytics = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/billing_analytics/`)

  const getBillingAlerts = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/billing_alerts/`)

  // Payment Method Management
  const getPaymentMethods = (accountId: string) =>
    api.execute(apiClient.get, `/accounts/${accountId}/payment_methods/`)

  // Plan Change Intelligence
  const calculateProration = (accountId: string, planId: string, billingType: 'monthly' | 'yearly' = 'monthly') =>
    api.execute(apiClient.post, `/accounts/${accountId}/calculate_proration/`, {
      plan_id: planId,
      billing_type: billingType
    })

  // Promotional Features
  const applyCoupon = (accountId: string, couponCode: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/apply_coupon/`, {
      coupon_code: couponCode.trim().toUpperCase()
    })

  // Administrative Features
  const extendTrial = (accountId: string, days: number, reason?: string) =>
    api.execute(apiClient.post, `/accounts/${accountId}/extend_trial/`, {
      days,
      reason
    })

  return {
    ...api,
    // Core subscription management
    getSubscriptionPlans,
    getAccountSubscription,
    getAccountBillingInfo,
    upgradeSubscriptionPlan,

    // Subscription lifecycle
    cancelSubscription,
    reactivateSubscription,
    pauseSubscription,
    resumeSubscription,

    // Invoice management
    getInvoices,

    // Analytics & intelligence
    getBillingAnalytics,
    getBillingAlerts,

    // Payment methods
    getPaymentMethods,

    // Plan changes
    calculateProration,

    // Promotions
    applyCoupon,

    // Administrative
    extendTrial,
  }
}
