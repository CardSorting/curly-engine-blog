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
            <ThemeToggle />
          </div>
          <div class="flex items-center space-x-4">
            <router-link to="/search" class="text-gray-600 hover:text-gray-900">
              Search
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Topic Header -->
    <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div v-if="topic" class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">
            {{ topic.name }}
          </h1>
          <p class="text-xl opacity-90 max-w-3xl mx-auto">
            {{ topic.description || `Articles about ${topic.name}` }}
          </p>
        </div>
        <div v-else class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-4">Topic</h1>
          <p class="text-xl opacity-90">Loading topic...</p>
        </div>
      </div>
    </div>

    <!-- Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading articles...</p>
      </div>

      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600">{{ error }}</p>
        <Button @click="loadArticles" class="mt-4">
          Try Again
        </Button>
      </div>

      <div v-else-if="articles?.length" class="mb-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900">
            Articles in {{ topic?.name }}
          </h2>
          <p class="text-gray-600">
            {{ articles.length }} article{{ articles.length !== 1 ? 's' : '' }}
          </p>
        </div>

        <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          <Card
            v-for="article in articles"
            :key="article.id"
            :title="article.title"
            :subtitle="`By ${article.author.email} • ${formatDate(article.published_at)}`"
            :content="article.excerpt"
            clickable
            class="h-full"
            @click="navigateToArticle(article)"
          >
            <template #footer>
              <div class="pt-4 border-t border-gray-100">
                <SocialShare 
                  :title="article.title"
                  :description="article.excerpt"
                  :url="getArticleUrl(article)"
                  class="scale-90 origin-left"
                />
              </div>
            </template>
          </Card>
        </div>
      </div>

      <div v-else class="text-center py-12">
        <p class="text-gray-600 mb-4">No articles published in this topic yet.</p>
        <router-link to="/" class="text-blue-600 hover:text-blue-700">
          ← Back to all articles
        </router-link>
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
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTopics } from '@/composables/useApi'
import { type Article, type Topic, type PaginatedResponse } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import SocialShare from '@/components/SocialShare.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const { fetchTopics, fetchArticlesByTopic } = useTopics()

const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')
const topic = ref<Topic | null>(null)
const articles = ref<Article[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const topicSlug = computed(() => route.params.topicSlug as string)
const accountSlug = computed(() => route.params.accountSlug as string)

// Get origin for URLs
const origin = computed(() => window.location.origin)

// Generate article URL
const getArticleUrl = (article: Article) => {
  return `${origin.value}/blog/${accountSlug.value}/articles/${article.slug}`
}

onMounted(async () => {
  await loadTopicAndArticles()
})

const loadTopicAndArticles = async () => {
  if (!topicSlug.value) return

  loading.value = true
  error.value = null

  try {
    // Load topic info
    const topicsResponse = await fetchTopics()
    if (topicsResponse && topicsResponse.results) {
      topic.value = topicsResponse.results.find((t: Topic) => t.slug === topicSlug.value) || null
    }

    // Load articles for this topic
    const articlesResponse = await fetchArticlesByTopic(topicSlug.value) as PaginatedResponse<Article>
    if (articlesResponse && articlesResponse.results) {
      articles.value = articlesResponse.results
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load topic articles'
  } finally {
    loading.value = false
  }
}

const loadArticles = async () => {
  await loadTopicAndArticles()
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
