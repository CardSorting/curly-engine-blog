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
          <div class="flex items-center space-x-6">
            <!-- Topic Filter -->
            <div class="relative">
              <select
                v-model="selectedTopic"
                @change="onTopicChange"
                class="appearance-none bg-white border border-gray-300 rounded-md px-3 py-1 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Topics</option>
                <option v-for="topic in topics" :key="topic.id" :value="topic.slug">
                  {{ topic.name }}
                </option>
              </select>
              <ChevronDownIcon class="absolute right-2 top-2 h-4 w-4 text-gray-400 pointer-events-none" />
            </div>

            <router-link to="/search" class="text-gray-600 hover:text-gray-900 text-sm">
              Search
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div class="text-center">
          <h1 class="text-4xl md:text-6xl font-bold mb-6">
            Welcome to Chronicle
          </h1>
          <p class="text-xl md:text-2xl mb-12 max-w-3xl mx-auto opacity-90">
            A modern multi-tenant blog platform built with Vue 3 and Django
          </p>
          <Button variant="secondary" size="lg" class="inline-block">
            Get Started
          </Button>
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

      <div v-else-if="articles?.length" class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
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

      <div v-else class="text-center py-12">
        <p class="text-gray-600 mb-4">No articles published yet.</p>
        <router-link to="/login" class="text-blue-600 hover:text-blue-700">
          Sign in to create content
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import { useArticles, useTopics } from '@/composables/useApi'
import { type Article, type Topic } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const { data: articles, loading, error, fetchArticles } = useArticles()
const { data: topics, fetchTopics } = useTopics()

const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')
const selectedTopic = ref('')

onMounted(async () => {
  await Promise.all([
    loadTopics(),
    loadArticles()
  ])
})

const loadArticles = async (params?: Record<string, any>) => {
  await fetchArticles(params)
}

const loadTopics = async () => {
  await fetchTopics()
}

const onTopicChange = () => {
  const params: any = {}
  if (selectedTopic.value) {
    // For topic filtering, we'll redirect to topic page
    router.push(`/topics/${selectedTopic.value}`)
  } else {
    // Load all articles
    loadArticles()
  }
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
