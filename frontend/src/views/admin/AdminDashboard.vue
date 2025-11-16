<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
              <p class="mt-1 text-sm text-gray-500">Manage your blog content and settings</p>
            </div>
            <div class="flex items-center space-x-3">
              <router-link
                :to="{ name: 'admin-article-create' }"
                class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <PlusIcon class="w-5 h-5 mr-2" />
                New Article
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <EyeIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Published</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.publishedArticles }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <PencilIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Drafts</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.draftArticles }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-5">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <EyeIcon class="h-6 w-6 text-gray-400" />
              </div>
              <div class="ml-5 w-0 flex-1">
                <dl>
                  <dt class="text-sm font-medium text-gray-500 truncate">Total Views</dt>
                  <dd class="text-lg font-medium text-gray-900">{{ stats.totalViews }}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions & Recent Content -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Quick Actions -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link
                :to="{ name: 'admin-article-create' }"
                class="flex items-center p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <PlusIcon class="h-5 w-5 text-blue-600 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-900">Create New Article</p>
                  <p class="text-xs text-gray-500">Start writing a new blog post</p>
                </div>
              </router-link>

              <router-link
                :to="{ name: 'admin-articles' }"
                class="flex items-center p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <DocumentTextIcon class="h-5 w-5 text-green-600 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-900">Manage Articles</p>
                  <p class="text-xs text-gray-500">View and edit existing content</p>
                </div>
              </router-link>

              <router-link
                :to="{ name: 'admin-media' }"
                class="flex items-center p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <PhotoIcon class="h-5 w-5 text-purple-600 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-900">Media Library</p>
                  <p class="text-xs text-gray-500">Upload and manage images</p>
                </div>
              </router-link>

              <router-link
                :to="{ name: 'admin-settings' }"
                class="flex items-center p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <CogIcon class="h-5 w-5 text-gray-600 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-900">Settings</p>
                  <p class="text-xs text-gray-500">Configure your blog</p>
                </div>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Recent Articles -->
        <div class="bg-white shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center justify-between mb-4">
              <h3 class="text-lg leading-6 font-medium text-gray-900">Recent Articles</h3>
              <router-link
                :to="{ name: 'admin-articles' }"
                class="text-sm font-medium text-blue-600 hover:text-blue-500"
              >
                View all
              </router-link>
            </div>

            <div v-if="loading" class="space-y-3">
              <div v-for="i in 3" :key="i" class="animate-pulse">
                <div class="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>

            <div v-else-if="recentArticles.length === 0" class="text-center py-6">
              <DocumentTextIcon class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">No articles</h3>
              <p class="mt-1 text-sm text-gray-500">Get started by creating your first article.</p>
            </div>

            <div v-else class="space-y-3">
              <router-link
                v-for="article in recentArticles"
                :key="article.id"
                :to="{ name: 'admin-article-edit', params: { articleId: article.id } }"
                class="block p-3 rounded-md hover:bg-gray-50 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium text-gray-900 truncate">{{ article.title }}</p>
                    <p class="text-xs text-gray-500">
                      {{ formatDate(article.updated_at) }} •
                      <span :class="article.status === 'published' ? 'text-green-600' : 'text-yellow-600'">
                        {{ article.status }}
                      </span>
                    </p>
                  </div>
                  <ChevronRightIcon class="h-5 w-5 text-gray-400" />
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  DocumentTextIcon,
  EyeIcon,
  PencilIcon,
  PlusIcon,
  PhotoIcon,
  CogIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import { useArticles } from '@/composables/useApi'
import type { Article, PaginatedResponse } from '@/types/api'

const route = useRoute()
const recentArticles = ref<Article[]>([])
const loading = ref(true)

// Stats computed from recent articles (would normally come from a separate API)
const stats = ref({
  totalArticles: 0,
  publishedArticles: 0,
  draftArticles: 0,
  totalViews: 0
})

// Format date for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const { fetchArticles } = useArticles()

// Load recent articles on mount
onMounted(async () => {
  try {
    const params = {
      ordering: '-updated_at',
      page_size: 5
    }
    const response = await fetchArticles(params) as PaginatedResponse<Article>

    if (response && response.results) {
      recentArticles.value = response.results
      stats.value.totalArticles = response.count || response.results.length

      // Calculate stats from the loaded data
      stats.value.publishedArticles = response.results.filter((a: Article) => a.status === 'published').length
      stats.value.draftArticles = response.results.filter((a: Article) => a.status === 'draft').length
      stats.value.totalViews = response.results.reduce((total: number, a: Article) => total + a.view_count, 0)
    }
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  } finally {
    loading.value = false
  }
})
</script>
