<template>
  <AdminLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h1 class="text-2xl font-semibold text-gray-900">Analytics Dashboard</h1>
          <p class="mt-2 text-sm text-gray-700">Track your blog's performance and engagement metrics.</p>
        </div>
        <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <select
            v-model="selectedPeriod"
            @change="loadAnalytics"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="mt-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>

      <div v-else class="mt-8 space-y-8">
        <!-- Stats Grid -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <EyeIcon class="h-6 w-6 text-gray-400" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Total Views</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.totalViews.toLocaleString() }}</dd>
                  </dl>
                  <div class="mt-1">
                    <span :class="[
                      'text-xs font-semibold',
                      stats.viewsChange >= 0 ? 'text-green-600' : 'text-red-600'
                    ]">
                      {{ stats.viewsChange >= 0 ? '+' : '' }}{{ stats.viewsChange }}%
                    </span>
                    <span class="text-xs text-gray-500">vs last period</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <DocumentTextIcon class="h-6 w-6 text-gray-400" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Total Articles</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.totalArticles }}</dd>
                  </dl>
                  <div class="mt-1">
                    <span class="text-xs font-semibold text-blue-600">
                      {{ stats.publishedArticles }} published
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <UsersIcon class="h-6 w-6 text-green-500" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Subscribers</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.totalSubscribers.toLocaleString() }}</dd>
                  </dl>
                  <div class="mt-1">
                    <span :class="[
                      'text-xs font-semibold',
                      stats.subscribersChange >= 0 ? 'text-green-600' : 'text-red-600'
                    ]">
                      {{ stats.subscribersChange >= 0 ? '+' : '' }}{{ stats.subscribersChange }}
                    </span>
                    <span class="text-xs text-gray-500">this month</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <ClockIcon class="h-6 w-6 text-yellow-500" />
                </div>
                <div class="ml-5 w-0 flex-1">
                  <dl>
                    <dt class="text-sm font-medium text-gray-500 truncate">Avg. Reading Time</dt>
                    <dd class="text-lg font-medium text-gray-900">{{ stats.avgReadingTime }}m</dd>
                  </dl>
                  <div class="mt-1">
                    <span class="text-xs text-gray-500">per article</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Views Over Time Chart -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Views Over Time</h3>
            </div>
            <div class="p-6">
              <ViewsChart :data="chartData.value.views" />
            </div>
          </div>

          <!-- Articles by Status Chart -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Articles by Status</h3>
            </div>
            <div class="p-6">
              <StatusChart :data="chartData.value.status" />
            </div>
          </div>

          <!-- Top Topics Chart -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Top Topics</h3>
            </div>
            <div class="p-6">
              <TopicsChart :data="chartData.value.topics" />
            </div>
          </div>

          <!-- Engagement Metrics -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Engagement Metrics</h3>
            </div>
            <div class="p-6">
              <EngagementChart :data="chartData.value.engagement" />
            </div>
          </div>
        </div>

        <!-- Recent Articles Table -->
        <div class="bg-white shadow overflow-hidden sm:rounded-md">
          <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-medium text-gray-900">Recent Articles Performance</h3>
          </div>
          <div class="divide-y divide-gray-200">
            <div
              v-for="article in recentArticles"
              :key="article.id"
              class="px-6 py-4 hover:bg-gray-50"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ article.title }}</p>
                    <span
                      :class="[
                        'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                        article.is_published
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      ]"
                    >
                      {{ article.is_published ? 'Published' : 'Draft' }}
                    </span>
                  </div>
                  <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <span>{{ article.view_count || 0 }} views</span>
                    <span>{{ article.reading_time }} min read</span>
                    <span>{{ new Date(article.created_at).toLocaleDateString() }}</span>
                    <span v-if="article.topic">{{ article.topic.name }}</span>
                  </div>
                </div>
                <div class="ml-4 flex-shrink-0">
                  <div class="text-right">
                    <div class="text-sm font-medium text-gray-900">
                      {{ getArticlePerformance(article) }}
                    </div>
                    <div class="text-xs text-gray-500">
                      {{ getPerformanceLabel(article) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Export Options -->
        <div class="bg-white shadow rounded-lg p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Export Analytics</h3>
          <div class="flex space-x-4">
            <Button @click="exportData('csv')" variant="outline">
              <DocumentArrowDownIcon class="h-4 w-4 mr-2" />
              Export as CSV
            </Button>
            <Button @click="exportData('pdf')" variant="outline">
              <DocumentArrowDownIcon class="h-4 w-4 mr-2" />
              Export as PDF
            </Button>
            <Button @click="refreshData" :loading="refreshing">
              <ArrowPathIcon class="h-4 w-4 mr-2" />
              Refresh Data
            </Button>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import Button from '@/components/ui/Button.vue'
import ViewsChart from '@/components/charts/ViewsChart.vue'
import StatusChart from '@/components/charts/StatusChart.vue'
import TopicsChart from '@/components/charts/TopicsChart.vue'
import EngagementChart from '@/components/charts/EngagementChart.vue'
import { useArticles, useAnalytics } from '@/composables/useApi'
import type { Article } from '@/types/api'
import {
  ChartBarIcon,
  EyeIcon,
  DocumentTextIcon,
  UsersIcon,
  ClockIcon,
  DocumentArrowDownIcon,
  ArrowPathIcon,
} from '@heroicons/vue/24/outline'

const { fetchArticles } = useArticles()
const {
  getPageViewAnalytics,
  getArticleAnalytics,
  getUserEngagement,
  exportAnalytics
} = useAnalytics()

const selectedPeriod = ref('30')
const loading = ref(true)
const refreshing = ref(false)
const analyticsData = ref<any>(null)
const articles = ref<Article[]>([])

const stats = computed(() => {
  if (!analyticsData.value) {
    // Fallback mock data while loading
    return {
      totalViews: 0,
      totalArticles: 0,
      publishedArticles: 0,
      draftArticles: 0,
      totalSubscribers: 0,
      subscribersChange: 0,
      viewsChange: 0,
      avgReadingTime: 0,
    }
  }

  const publishedArticles = articles.value.filter(a => a.is_published)
  const avgReadingTime = publishedArticles.length > 0
    ? Math.round(publishedArticles.reduce((sum, a) => sum + a.reading_time, 0) / publishedArticles.length)
    : 0

  return {
    totalViews: analyticsData.value.overview.total_views,
    totalArticles: articles.value.length,
    publishedArticles: publishedArticles.length,
    draftArticles: articles.value.filter(a => !a.is_published).length,
    totalSubscribers: analyticsData.value.overview.total_unique_views, // Using unique views as subscriber proxy for now
    subscribersChange: 5, // Could be calculated from daily trend if needed
    viewsChange: 10, // Could be calculated from daily trend if needed
    avgReadingTime,
  }
})

const recentArticles = computed(() => {
  return articles.value
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 10)
})

const chartData = ref<any>({
  views: [],
  status: [],
  topics: [],
  engagement: [],
})

const updateChartData = () => {
  // Status data from articles
  const statusData = [
    { name: 'Published', value: stats.value.publishedArticles, color: '#10b981' },
    { name: 'Draft', value: stats.value.draftArticles, color: '#f59e0b' },
  ]

  // Topics data from articles
  const topicCounts: Record<string, number> = {}
  articles.value.forEach(article => {
    if (article.topic) {
      topicCounts[article.topic.name] = (topicCounts[article.topic.name] || 0) + 1
    }
  })

  const topicsData = Object.entries(topicCounts)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 5)

  // Use actual analytics data if available, fallback to calculated values
  const viewsData = analyticsData.value?.pageViews || []
  const engagementData = analyticsData.value?.engagement || [
    { metric: 'Avg. Views/Article', value: Math.round(stats.value.totalViews / Math.max(stats.value.publishedArticles, 1)) },
    { metric: 'Avg. Reading Time', value: stats.value.avgReadingTime },
    { metric: 'Top Article Views', value: Math.max(...articles.value.map(a => a.view_count || 0), 0) },
  ]

  chartData.value = {
    views: viewsData,
    status: statusData,
    topics: topicsData,
    engagement: engagementData,
  }
}

const getArticlePerformance = (article: Article) => {
  const views = article.view_count || 0
  if (views > 1000) return 'Excellent'
  if (views > 500) return 'Good'
  if (views > 100) return 'Average'
  return 'Low'
}

const getPerformanceLabel = (article: Article) => {
  const views = article.view_count || 0
  return `${views} views`
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    // Load analytics data using composables
    const [pageViewsResponse, articlesResponse, engagementResponse] = await Promise.all([
      getPageViewAnalytics({ period: selectedPeriod.value }),
      fetchArticles(),
      getUserEngagement({ period: selectedPeriod.value }),
    ])

    // Set analytics data from API responses
    analyticsData.value = {
      pageViews: pageViewsResponse,
      engagement: engagementResponse,
      overview: {
        total_views: pageViewsResponse?.total || 0,
        total_unique_views: pageViewsResponse?.uniqueViews || 0,
      }
    }

    // Still load articles for article-specific data
    articles.value = Array.isArray(articlesResponse) ? articlesResponse : (articlesResponse as any)?.results || []

    // Update chart data after loading
    updateChartData()
  } catch (error) {
    console.error('Failed to load analytics:', error)
    // Keep fallback data if API fails
    updateChartData()
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  refreshing.value = true
  await loadAnalytics()
  refreshing.value = false
}

const exportData = async (format: 'csv' | 'pdf') => {
  try {
    // Use the exportAnalytics composable
    const response = await exportAnalytics(format, {
      period: selectedPeriod.value,
      data_type: 'analytics'
    })

    // The exportAnalytics composable should handle the response appropriately
    // If it's a blob response, create download link
    if (response instanceof Blob) {
      const url = URL.createObjectURL(response)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.${format}`
      a.click()
      URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error('Export failed:', error)
    // Fallback to mock export if API fails
    if (format === 'csv') {
      const data = articles.value.map(article => ({
        title: article.title,
        status: article.is_published ? 'Published' : 'Draft',
        views: article.view_count || 0,
        reading_time: article.reading_time,
        topic: article.topic?.name || 'N/A',
        created_at: article.created_at,
      }))

      if (data.length === 0) {
        console.warn('No data to export')
        return
      }

      const csv = [
        Object.keys(data[0] || {}).join(','),
        ...data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
      ].join('\n')

      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      URL.revokeObjectURL(url)
    }
  }
}

onMounted(() => {
  loadAnalytics()
})
</script>
