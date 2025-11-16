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

  return {
    ...api,
    fetchTopics,
    fetchArticlesByTopic,
  }
}

export function usePages<T = any>() {
  const api = useApi<T>()

  const fetchPages = (params?: Record<string, any>) =>
    api.execute(apiClient.get, '/pages/', { params })

  const fetchPage = (slug: string) =>
    api.execute(apiClient.get, `/pages/${slug}/`)

  return {
    ...api,
    fetchPages,
    fetchPage,
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

  return {
    ...api,
    subscribe,
    unsubscribe,
  }
}
