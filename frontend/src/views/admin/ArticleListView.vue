<template>
  <AdminLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex flex-wrap gap-4 items-center">
            <!-- Status Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                v-model="statusFilter"
                @change="onStatusFilterChange"
                class="block w-full pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
              >
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="published">Published</option>
              </select>
            </div>

            <!-- Topic Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Topic</label>
              <select
                v-model="topicFilter"
                @change="onTopicFilterChange"
                class="block w-full pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
              >
                <option value="">All Topics</option>
                <option v-for="topic in topics" :key="topic.id" :value="topic.id">
                  {{ topic.name }}
                </option>
              </select>
            </div>

            <!-- Search -->
            <div class="flex-1 min-w-64">
              <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                type="text"
                placeholder="Search articles..."
                class="block w-full px-3 py-2 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div class="flex items-end">
              <Button @click="clearFilters" variant="outline" size="sm">
                Clear Filters
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading articles...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600">{{ error }}</p>
        <Button @click="loadArticles()" class="mt-4">
          Try Again
        </Button>
      </div>

      <!-- Articles Table -->
      <div v-else-if="articles.length" class="bg-white shadow overflow-hidden sm:rounded-md">
        <ul class="divide-y divide-gray-200">
          <li v-for="article in articles" :key="article.id">
            <div class="px-4 py-4 sm:px-6">
              <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center">
                    <p class="text-lg font-medium text-blue-600 truncate">
                      {{ article.title }}
                    </p>
                    <span
                      :class="article.status === 'published' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'"
                      class="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    >
                      {{ article.status }}
                    </span>
                  </div>
                  <div class="mt-2 flex items-center text-sm text-gray-500">
                    <p class="truncate">
                      By {{ article.author.email }} •
                      {{ formatDate(article.updated_at) }} •
                      {{ article.word_count }} words •
                      {{ article.reading_time }} min read
                    </p>
                  </div>
                  <p v-if="article.excerpt" class="mt-2 text-sm text-gray-600 line-clamp-2">
                    {{ article.excerpt }}
                  </p>
                </div>
                <div class="flex items-center space-x-4">
                  <router-link
                    :to="{ name: 'admin-article-edit', params: { articleSlug: article.slug } }"
                    class="text-blue-600 hover:text-blue-900 text-sm font-medium"
                  >
                    Edit
                  </router-link>
                  <Button
                    @click="togglePublishStatus(article)"
                    :variant="article.status === 'published' ? 'outline' : 'primary'"
                    size="sm"
                  >
                    {{ article.status === 'published' ? 'Unpublish' : 'Publish' }}
                  </Button>
                </div>
              </div>
            </div>
          </li>
        </ul>

        <!-- Pagination -->
        <div v-if="pagination.next || pagination.previous" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              Showing {{ startIndex + 1 }} to {{ endIndex }} of {{ pagination.count }} articles
            </div>
            <div class="flex space-x-2">
              <Button
                @click="loadPage(pagination.previous)"
                :disabled="!pagination.previous"
                variant="outline"
                size="sm"
              >
                Previous
              </Button>
              <Button
                @click="loadPage(pagination.next)"
                :disabled="!pagination.next"
                variant="outline"
                size="sm"
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <DocumentTextIcon class="mx-auto h-16 w-16 text-gray-300" />
        <h3 class="mt-2 text-lg font-medium text-gray-900">No articles found</h3>
        <p class="mt-1 text-gray-600">
          {{ searchQuery || statusFilter || topicFilter ? 'Try adjusting your filters.' : 'Get started by creating your first article.' }}
        </p>
        <div class="mt-6">
          <router-link
            :to="{ name: 'admin-article-create' }"
            class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <PlusIcon class="w-5 h-5 mr-2" />
            Create Article
          </router-link>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AdminLayout from '@/layouts/AdminLayout.vue'
import { DocumentTextIcon, PlusIcon } from '@heroicons/vue/24/outline'
import { useArticles, useTopics } from '@/composables/useApi'
import { type Article, type Topic, type PaginatedResponse } from '@/types/api'
import Button from '@/components/ui/Button.vue'

const route = useRoute()
const { fetchArticles, publishArticle } = useArticles()
const { fetchTopics } = useTopics()

const articles = ref<Article[]>([])
const topics = ref<Topic[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const pagination = ref({
  count: 0,
  next: null as string | null,
  previous: null as string | null,
  currentPage: 1
})

const statusFilter = ref('')
const topicFilter = ref('')
const searchQuery = ref('')
let searchTimeout: number | null = null

const startIndex = computed(() => (pagination.value.currentPage - 1) * 20)
const endIndex = computed(() => Math.min(pagination.value.currentPage * 20, pagination.value.count))

onMounted(async () => {
  await Promise.all([
    loadTopics(),
    loadArticles()
  ])
})

const loadArticles = async (url?: string) => {
  loading.value = true
  error.value = null

  try {
    const params: any = {}

    if (statusFilter.value) params.status = statusFilter.value
    if (topicFilter.value) params.topic = topicFilter.value
    if (searchQuery.value) params.search = searchQuery.value

    const response = await fetchArticles(params) as PaginatedResponse<Article>

    if (response) {
      articles.value = response.results || []
      pagination.value = {
        count: response.count || 0,
        next: response.next,
        previous: response.previous,
        currentPage: pagination.value.currentPage
      }
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load articles'
  } finally {
    loading.value = false
  }
}

const loadTopics = async () => {
  try {
    const response = await fetchTopics()
    if (response && response.results) {
      topics.value = response.results
    }
  } catch (err) {
    console.error('Failed to load topics:', err)
  }
}

const loadPage = async (url: string | null) => {
  if (!url) return

  // Extract page number from URL for tracking
  const urlObj = new URL(url)
  const page = parseInt(urlObj.searchParams.get('page') || '1')
  pagination.value.currentPage = page

  // For now, reload with current filters
  // In a real implementation, you'd parse the URL and maintain filters
  await loadArticles()
}

const togglePublishStatus = async (article: Article) => {
  try {
    const newStatus = article.status === 'published' ? 'draft' : 'published'
    await publishArticle(article.slug)
    // Optimistically update the UI
    article.status = newStatus
  } catch (err: any) {
    console.error('Failed to toggle publish status:', err)
    // Could show a toast notification here
  }
}

const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadArticles()
  }, 300)
}

const clearFilters = () => {
  statusFilter.value = ''
  topicFilter.value = ''
  searchQuery.value = ''
  loadArticles()
}

const onStatusFilterChange = () => {
  loadArticles()
}

const onTopicFilterChange = () => {
  loadArticles()
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>
