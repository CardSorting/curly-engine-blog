import { ref, computed } from 'vue'
import { useApi } from './useApi'
import { apiClient } from '@/services/api/config'
import { useNotification } from '@kyvg/vue3-notification'

export interface Series {
  id: string
  title: string
  slug: string
  description: string
  cover_image?: {
    id: string
    file: string
    file_name: string
  }
  account?: string
  article_count: number
  created_at: string
  updated_at: string
}

export interface SeriesArticle {
  id: string
  title: string
  slug: string
  excerpt: string
  series_order: number
  published_at?: string
  status: 'draft' | 'published'
  word_count: number
  reading_time: number
  author: {
    id: string
    username: string
    first_name: string
    last_name: string
  }
}

export const useSeries = () => {
  const api = useApi()
  const { notify } = useNotification()

  // Reactive state
  const series = ref<Series[]>([])
  const currentSeries = ref<Series | null>(null)
  const seriesArticles = ref<SeriesArticle[]>([])
  const isLoading = ref(false)
  const isCreatingSeries = ref(false)

  // Computed properties
  const publishedSeries = computed(() =>
    series.value.filter(s => s.article_count > 0)
  )

  const draftSeries = computed(() =>
    series.value.filter(s => s.article_count === 0)
  )

  // Methods
  const fetchSeries = async (params?: any) => {
    isLoading.value = true
    try {
      const response = await api.execute(apiClient.get, '/api/', { params: { ...params, include_series: true } }) as any
      series.value = response.series || []
      return series.value
    } catch (error: any) {
      notify({
        title: 'Failed to load series',
        text: error.response?.data?.detail || 'Unable to fetch series',
        type: 'error'
      })
      return []
    } finally {
      isLoading.value = false
    }
  }

  const fetchSeriesDetails = async (seriesId: string) => {
    isLoading.value = true
    try {
      const response = await api.execute(apiClient.get, `/api/series/${seriesId}/`) as any
      currentSeries.value = response.series
      seriesArticles.value = response.articles || []
      return currentSeries.value
    } catch (error: any) {
      notify({
        title: 'Failed to load series',
        text: error.response?.data?.detail || 'Unable to fetch series details',
        type: 'error'
      })
      return null
    } finally {
      isLoading.value = false
    }
  }

  const createSeries = async (data: {
    title: string
    description?: string
    cover_image?: string
  }) => {
    isCreatingSeries.value = true
    try {
      const response = await api.execute(apiClient.post, '/api/series/', data) as any
      const newSeries = response as Series
      series.value.unshift(newSeries)

      notify({
        title: 'Series created',
        text: `"${newSeries.title}" has been created successfully`,
        type: 'success'
      })

      return newSeries
    } catch (error: any) {
      notify({
        title: 'Failed to create series',
        text: error.response?.data?.detail || 'Unable to create series',
        type: 'error'
      })
      return null
    } finally {
      isCreatingSeries.value = false
    }
  }

  const updateSeries = async (seriesId: string, data: Partial<{
    title: string
    description: string
    cover_image: string
  }>) => {
    try {
      const response = await api.execute(apiClient.patch, `/api/series/${seriesId}/`, data) as any
      const updatedSeries = response as Series

      // Update in local series list
      const index = series.value.findIndex(s => s.id === seriesId)
      if (index !== -1) {
        series.value[index] = updatedSeries
      }

      if (currentSeries.value?.id === seriesId) {
        currentSeries.value = updatedSeries
      }

      notify({
        title: 'Series updated',
        text: `"${updatedSeries.title}" has been updated`,
        type: 'success'
      })

      return updatedSeries
    } catch (error: any) {
      notify({
        title: 'Failed to update series',
        text: error.response?.data?.detail || 'Unable to update series',
        type: 'error'
      })
      return null
    }
  }

  const deleteSeries = async (seriesId: string) => {
    try {
      await api.execute(apiClient.delete, `/api/series/${seriesId}/`)

      // Remove from local series list
      series.value = series.value.filter(s => s.id !== seriesId)

      if (currentSeries.value?.id === seriesId) {
        currentSeries.value = null
        seriesArticles.value = []
      }

      notify({
        title: 'Series deleted',
        text: 'Series has been deleted successfully',
        type: 'success'
      })

      return true
    } catch (error: any) {
      notify({
        title: 'Failed to delete series',
        text: error.response?.data?.detail || 'Unable to delete series',
        type: 'error'
      })
      return false
    }
  }

  const assignArticleToSeries = async (articleId: string, seriesId: string, order?: number) => {
    try {
      const data: any = { series: seriesId }
      if (order !== undefined) {
        data.series_order = order
      }

      const response = await api.execute(apiClient.patch, `/api/detail/${articleId}/`, data) as any

      notify({
        title: 'Article assigned',
        text: 'Article has been added to the series',
        type: 'success'
      })

      // Refresh series details if current series
      if (currentSeries.value?.id === seriesId) {
        fetchSeriesDetails(seriesId)
      }

      return response
    } catch (error: any) {
      notify({
        title: 'Failed to assign article',
        text: error.response?.data?.detail || 'Unable to assign article to series',
        type: 'error'
      })
      return null
    }
  }

  const removeArticleFromSeries = async (articleId: string) => {
    try {
      const response = await api.execute(apiClient.patch, `/api/detail/${articleId}/`, {
        series: null,
        series_order: 0
      }) as any

      notify({
        title: 'Article removed',
        text: 'Article has been removed from the series',
        type: 'success'
      })

      // Refresh current series if applicable
      if (currentSeries.value) {
        fetchSeriesDetails(currentSeries.value.id)
      }

      return response
    } catch (error: any) {
      notify({
        title: 'Failed to remove article',
        text: error.response?.data?.detail || 'Unable to remove article from series',
        type: 'error'
      })
      return null
    }
  }

  const reorderSeriesArticles = async (seriesId: string, articleOrder: { id: string; order: number }[]) => {
    try {
      const updates = articleOrder.map(({ id, order }) =>
        api.execute(apiClient.patch, `/api/detail/${id}/`, { series_order: order })
      )

      await Promise.all(updates)

      notify({
        title: 'Order updated',
        text: 'Series article order has been updated',
        type: 'success'
      })

      // Refresh series details
      fetchSeriesDetails(seriesId)

      return true
    } catch (error: any) {
      notify({
        title: 'Failed to reorder',
        text: error.response?.data?.detail || 'Unable to reorder series articles',
        type: 'error'
      })
      return false
    }
  }

  const getSeriesNavigation = (currentArticleId: string) => {
    if (!currentSeries.value || !seriesArticles.value.length) {
      return { previous: null, next: null, currentIndex: -1 }
    }

    const currentIndex = seriesArticles.value.findIndex(article => article.id === currentArticleId)

    return {
      previous: currentIndex > 0 ? seriesArticles.value[currentIndex - 1] : null,
      next: currentIndex < seriesArticles.value.length - 1 ? seriesArticles.value[currentIndex + 1] : null,
      currentIndex
    }
  }

  const clearCurrentSeries = () => {
    currentSeries.value = null
    seriesArticles.value = []
  }

  return {
    // State
    series,
    currentSeries,
    seriesArticles,
    isLoading,
    isCreatingSeries,

    // Computed
    publishedSeries,
    draftSeries,

    // Methods
    fetchSeries,
    fetchSeriesDetails,
    createSeries,
    updateSeries,
    deleteSeries,
    assignArticleToSeries,
    removeArticleFromSeries,
    reorderSeriesArticles,
    getSeriesNavigation,
    clearCurrentSeries
  }
}
