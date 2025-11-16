<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-900">
              {{ appName }}
            </router-link>
          </div>
          <div class="flex items-center">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Loading state -->
    <div v-if="loading" class="flex justify-center items-center min-h-[50vh]">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="max-w-4xl mx-auto px-4 py-8">
      <div class="text-center">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Article Not Found</h1>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <router-link to="/" class="text-blue-600 hover:text-blue-800">
          ← Back to Home
        </router-link>
      </div>
    </div>

    <!-- Article content -->
    <article v-else-if="article" class="max-w-4xl mx-auto px-4 py-8">
      <!-- Article header -->
      <header class="mb-8">
        <!-- Topic badge -->
        <div v-if="article.topic" class="mb-4">
          <span
            class="inline-block px-3 py-1 text-sm font-medium rounded-full text-white"
            :style="{ backgroundColor: article.topic.color }"
          >
            {{ article.topic.name }}
          </span>
        </div>

        <!-- Title -->
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4 leading-tight">
          {{ article.title }}
        </h1>

        <!-- Meta information -->
        <div class="flex flex-wrap items-center gap-4 text-gray-600 mb-6">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-sm font-medium text-blue-600">
                {{ article.author.username.charAt(0).toUpperCase() }}
              </span>
            </div>
            <span class="font-medium">{{ article.author.username }}</span>
          </div>

          <span class="text-gray-400">•</span>

          <time v-if="article.published_at" :datetime="article.published_at">
            {{ formatDate(article.published_at) }}
          </time>

          <span class="text-gray-400">•</span>

          <span>{{ article.reading_time }} min read</span>

          <span class="text-gray-400">•</span>

          <span>{{ article.view_count }} views</span>
        </div>

        <!-- Hero image -->
        <div v-if="article.hero_image" class="mb-8">
          <img
            :src="article.hero_image.file"
            :alt="article.hero_image.alt_text || article.title"
            class="w-full h-64 md:h-96 object-cover rounded-lg shadow-lg"
          />
        </div>
      </header>

      <!-- Article content -->
      <div class="prose prose-lg prose-blue max-w-none">
        <VueMarkdownRender :source="article.content" />
      </div>

      <!-- Social sharing -->
      <div class="mt-8">
        <SocialShare 
          :title="article.title"
          :description="article.excerpt"
        />
      </div>

      <!-- Article footer -->
      <footer class="mt-12 pt-8 border-t border-gray-200">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-2 text-gray-600">
            <span>Published on</span>
            <time v-if="article.published_at" :datetime="article.published_at" class="font-medium">
              {{ formatDate(article.published_at) }}
            </time>
          </div>

          <router-link to="/" class="text-blue-600 hover:text-blue-800 font-medium">
            ← Back to Home
          </router-link>
        </div>
      </footer>
    </article>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import VueMarkdownRender from 'vue-markdown-render'
import { useArticles } from '@/composables/useApi'
import type { Article } from '@/types/api'
import SocialShare from '@/components/SocialShare.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')
const articleSlug = computed(() => route.params.articleSlug as string)
const accountSlug = computed(() => route.params.accountSlug as string)

const { data: article, loading, error, fetchArticle } = useArticles<Article>()

// Format date for display
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

// Load article on mount
onMounted(async () => {
  try {
    await fetchArticle(articleSlug.value)
    // TODO: Add meta tag setup with vue-meta
  } catch (err) {
    console.error('Failed to load article:', err)
  }
})
</script>
