<template>
  <AdminLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h1 class="text-2xl font-semibold text-gray-900">Analytics</h1>
          <p class="mt-2 text-sm text-gray-700">Track your blog's performance and engagement metrics.</p>
        </div>
      </div>

      <div v-if="loading" class="mt-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>

      <div v-else class="mt-8">
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
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white overflow-hidden shadow rounded-lg">
            <div class="p-5">
              <div class="flex items-center">
                <div class="flex-shrink-0">
                  <ChartBarIcon class="h-6 w-6 text-green-500" />
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
                  <DocumentTextIcon class="h-6 w-6 text-yellow-500" />
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
        </div>

        <!-- Recent Articles -->
        <div class="mt-8">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Recent Articles</h3>
          <div class="mt-5 bg-white shadow overflow-hidden sm:rounded-md">
            <ul class="divide-y divide-gray-200">
              <li v-for="article in recentArticles" :key="article.id">
                <div class="px-4 py-4 flex items-center sm:px-6">
                  <div class="min-w-0 flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p class="text-sm font-medium text-gray-900 truncate">{{ article.title }}</p>
                      <p class="mt-1 text-sm text-gray-500">
                        {{ article.view_count || 0 }} views • 
                        {{ new Date(article.created_at).toLocaleDateString() }}
                      </p>
                    </div>
                    <div class="mt-4 flex-shrink-0 sm:mt-0 sm:ml-5">
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
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>

        <!-- Charts Placeholder -->
        <div class="mt-8">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Performance Charts</h3>
          <div class="mt-5 bg-white shadow rounded-lg p-6">
            <div class="text-center py-12">
              <ChartBarIcon class="mx-auto h-12 w-12 text-gray-400" />
              <h3 class="mt-2 text-sm font-medium text-gray-900">Coming Soon</h3>
              <p class="mt-1 text-sm text-gray-500">Detailed charts and analytics will be available soon.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
import { ChartBarIcon, EyeIcon, DocumentTextIcon, UsersIcon } from '@heroicons/vue/24/outline'
import { ref, onMounted } from 'vue'
import { useArticles } from '@/composables/useApi'
import { type Article } from '@/types/api'

const { fetchArticles } = useArticles()

const stats = ref({
  totalViews: 0,
  totalArticles: 0,
  publishedArticles: 0,
  draftArticles: 0
})

const recentArticles = ref<Article[]>([])
const loading = ref(true)

onMounted(async () => {
  await loadAnalytics()
})

const loadAnalytics = async () => {
  try {
    const response = await fetchArticles()
    const articles = response?.results || response || []
    
    stats.value.totalArticles = articles.length
    stats.value.publishedArticles = articles.filter((a: Article) => a.is_published).length
    stats.value.draftArticles = articles.filter((a: Article) => !a.is_published).length
    stats.value.totalViews = articles.reduce((sum: number, a: Article) => sum + (a.view_count || 0), 0)
    
    recentArticles.value = articles
      .sort((a: Article, b: Article) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 5)
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}
</script>
