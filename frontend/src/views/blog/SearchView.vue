<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-900">
              {{ appName }}
            </router-link>
          </div>
          <div class="flex items-center">
            <!-- Minimal nav - search is the focus -->
          </div>
        </div>
      </div>
    </nav>

    <!-- Search Section -->
    <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-8">
            Search Articles
          </h1>

          <!-- Search Form -->
          <form @submit.prevent="performSearch" class="max-w-2xl mx-auto">
            <div class="flex gap-4">
              <div class="flex-1 relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search for articles, topics, or keywords..."
                  class="w-full px-4 py-3 text-lg text-gray-900 rounded-lg focus:outline-none focus:ring-2 focus:ring-white focus:border-transparent"
                  :disabled="loading"
                />
                <MagnifyingGlassIcon class="absolute right-3 top-3 h-6 w-6 text-gray-400" />
              </div>
              <Button
                type="submit"
                :disabled="loading || !searchQuery.trim()"
                class="px-6 py-3 text-lg font-medium"
              >
                <MagnifyingGlassIcon v-if="!loading" class="h-5 w-5 mr-2" />
                <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Search
              </Button>
            </div>
          </form>

          <!-- Search Tips -->
          <div class="mt-8 text-sm opacity-75 max-w-xl mx-auto">
            <p>💡 Tip: Search for article titles, content, or author names</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Results -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <!-- Search Info -->
      <div v-if="searchPerformed" class="mb-8">
        <div v-if="searchQuery" class="flex items-center justify-between">
          <h2 class="text-2xl font-bold text-gray-900">
            Search Results for "{{ searchQuery }}"
          </h2>
          <p class="text-gray-600">
            {{ articles.length }} result{{ articles.length !== 1 ? 's' : '' }} found
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && searchPerformed" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Searching articles...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600 mb-4">{{ error }}</p>
        <Button @click="performSearch" variant="outline">
          Try Again
        </Button>
      </div>

      <!-- Results -->
      <div v-else-if="articles.length > 0" class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        <Card
          v-for="article in articles"
          :key="article.id"
          :title="article.title"
          :subtitle="`By ${article.author.email} • ${formatDate(article.published_at)}`"
          :content="article.excerpt"
          clickable
          class="h-full"
          @click="navigateToArticle(article)"
        />
      </div>

      <!-- No Results -->
      <div v-else-if="searchPerformed && !loading" class="text-center py-12">
        <MagnifyingGlassIcon class="mx-auto h-16 w-16 text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
        <p class="text-gray-600 mb-6">
          We couldn't find any articles matching "{{ searchQuery }}".
        </p>
        <div class="space-x-4">
          <Button @click="clearSearch" variant="outline">
            Clear Search
          </Button>
          <router-link to="/">
            <Button variant="outline">
              Browse All Articles
            </Button>
          </router-link>
        </div>
      </div>

      <!-- Initial State -->
      <div v-else class="text-center py-12">
        <MagnifyingGlassIcon class="mx-auto h-16 w-16 text-gray-300 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">Start your search</h3>
        <p class="text-gray-600">
          Enter keywords above to find articles
        </p>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-50 border-t">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-gray-600">
          <p>&copy; 2025 Chronicle. Multi-tenant blog platform.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import { useArticles } from '@/composables/useApi'
import { type Article, type PaginatedResponse } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const route = useRoute()
const { fetchArticles } = useArticles()

const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')
const searchQuery = ref('')
const articles = ref<Article[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const searchPerformed = ref(false)

// Initialize search from query param
onMounted(() => {
  const query = route.query.q as string
  if (query) {
    searchQuery.value = query
    performSearch()
  }
})

const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  loading.value = true
  error.value = null
  searchPerformed.value = true

  try {
    // Update URL with search query
    router.replace({ query: { q: searchQuery.value } })

    // Search articles with query parameter
    const params = {
      search: searchQuery.value,
      page_size: 50 // Increase limit for search results
    }

    const response = await fetchArticles(params) as PaginatedResponse<Article>

    if (response && response.results) {
      articles.value = response.results
    } else {
      articles.value = []
    }
  } catch (err: any) {
    error.value = err.message || 'Search failed'
    articles.value = []
  } finally {
    loading.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  articles.value = []
  error.value = null
  searchPerformed.value = false
  router.replace({ query: {} })
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const navigateToArticle = (article: Article) => {
  // For multi-tenant routing, we'd need account context here
  // For now, redirect to login to set up account context
  router.push('/login')
}
</script>
