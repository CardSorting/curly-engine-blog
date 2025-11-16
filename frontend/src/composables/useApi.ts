import { ref, type Ref } from 'vue'
import { apiClient } from '@/services/api/config'
import { notify } from '@kyvg/vue3-notification'
import type { ApiError } from '@/types/api'

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

  const execute = async <P extends any[]>(
    apiCall: (...args: P) => Promise<{ data: T }>,
    ...args: P
  ): Promise<T | null> => {
    state.loading.value = true
    state.error.value = null

    try {
      const response = await apiCall(...args)
      state.data.value = response.data
      return response.data
    } catch (error: any) {
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
export function useArticles<T = any>() {
  const api = useApi<T>()

  const fetchArticles = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/', { params })

  const fetchArticle = (slug: string) =>
    api.execute(apiClient.get, `/detail/${slug}/`)

  const createArticle = (data: any) =>
    api.execute(apiClient.post, '/', data)

  const updateArticle = (slug: string, data: any) =>
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

export function useTopics<T = any>() {
  const api = useApi<T>()

  const fetchTopics = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/topics/', { params })

  const fetchArticlesByTopic = (slug: string, params?: Record<string, any>) =>
    api.execute(apiClient.get, `/topics/${slug}/articles/`, { params })

  const createTopic = (data: any) =>
    api.execute(apiClient.post, '/topics/', data)

  const updateTopic = (slug: string, data: any) =>
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

export function usePages<T = any>() {
  const api = useApi<T>()

  const fetchPages = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/pages/', { params })

  const fetchPage = (slug: string) =>
    api.execute(apiClient.get, `/pages/${slug}/`)

  const createPage = (data: any) =>
    api.execute(apiClient.post, '/pages/', data)

  const updatePage = (slug: string, data: any) =>
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

export function useMedia<T = any>() {
  const api = useApi<T>()

  const fetchMedia = (params?: Record<string, any>) =>
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

export function useNewsletter<T = any>() {
  const api = useApi<T>()

  const subscribe = (data: { email: string; first_name?: string; last_name?: string }) =>
    api.execute(apiClient.post, '/newsletter/subscribers/subscribe/', data)

  const unsubscribe = (data: { email: string }) =>
    api.execute(apiClient.post, '/newsletter/subscribers/unsubscribe/', data)

  const getSubscribers = (params?: Record<string, any>) =>
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

  const exportSubscribers = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/newsletter/subscribers/export/', { params })

  return {
    ...api,
    subscribe,
    unsubscribe,
    getSubscribers,
    getSubscriberStats,
    importSubscribers,
    exportSubscribers,
  }
}

export function useNewsletterCampaigns<T = any>() {
  const api = useApi<T>()

  const getCampaigns = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/newsletter/campaigns/', { params })

  const getCampaign = (id: string) =>
    api.execute(apiClient.get, `/newsletter/campaigns/${id}/`)

  const createCampaign = (data: any) =>
    api.execute(apiClient.post, '/newsletter/campaigns/', data)

  const updateCampaign = (id: string, data: any) =>
    api.execute(apiClient.put, `/newsletter/campaigns/${id}/`, data)

  const deleteCampaign = (id: string) =>
    api.execute(apiClient.delete, `/newsletter/campaigns/${id}/`)

  const sendCampaign = (id: string, data?: any) =>
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

export function useSeo<T = any>() {
  const api = useApi<T>()

  const getSeoAudit = () =>
    api.execute(apiClient.get, '/seo/audit/')

  const optimizeArticle = (articleId: string) =>
    api.execute(apiClient.post, `/articles/${articleId}/seo-optimize/`)

  const getGlobalSettings = () =>
    api.execute(apiClient.get, '/seo/settings/')

  const updateGlobalSettings = (data: any) =>
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

export function useAnalytics<T = any>() {
  const api = useApi<T>()

  const getArticleAnalytics = (articleId?: string, params?: Record<string, any>) =>
    api.execute(apiClient.get, articleId ? `/analytics/articles/${articleId}/` : '/analytics/articles/', { params })

  const getPageViewAnalytics = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/analytics/pageviews/', { params })

  const getTrafficSources = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/analytics/traffic-sources/', { params })

  const getUserEngagement = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/analytics/engagement/', { params })

  const exportAnalytics = (format: 'csv' | 'pdf', params?: Record<string, any>) =>
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
