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
          <div class="flex items-center space-x-4">
            <router-link to="/search" class="text-gray-600 hover:text-gray-900">
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
import { useArticles, useTopics } from '@/composables/useApi'
import { type Article, type Topic } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const { data: articles, loading, error, execute: fetchArticles } = useArticles()
const { data: topics } = useTopics()

const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')

onMounted(async () => {
  await loadArticles()
})

const loadArticles = async () => {
  await fetchArticles()
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
