<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <!-- Header -->
    <div class="bg-gradient-to-r from-orange-500 to-red-500 text-white p-4">
      <div class="flex items-center space-x-2">
        <FireIcon class="w-5 h-5" />
        <h3 class="text-lg font-semibold">Trending Now</h3>
      </div>
      <p class="text-orange-100 text-sm mt-1">Most read articles this week</p>
    </div>

    <!-- Articles List -->
    <div class="divide-y divide-gray-100">
      <div
        v-for="(article, index) in trendingArticles.slice(0, 5)"
        :key="article.id"
        class="p-4 hover:bg-gray-50 transition-colors cursor-pointer group"
        @click="navigateToArticle(article)"
      >
        <div class="flex space-x-4">
          <!-- Rank Number -->
          <div class="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white"
               :class="getRankColor(index)">
            {{ index + 1 }}
          </div>

          <!-- Article Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between mb-2">
              <h4 class="font-medium text-gray-900 line-clamp-2 group-hover:text-blue-600 transition-colors text-sm leading-snug">
                {{ article.title }}
              </h4>
            </div>

            <div class="flex items-center space-x-4 text-xs text-gray-500 mb-2">
              <span>{{ formatTimeAgo(article.published_at) }}</span>
              <span class="text-gray-300">•</span>
              <span>{{ calculateReadTime(article) }} min read</span>
            </div>

            <!-- Author & Metrics -->
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <div class="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-xs">
                  {{ article.author?.username?.charAt(0).toUpperCase() || 'A' }}
                </div>
                <span class="text-xs text-gray-600">{{ article.author?.username || 'Anonymous' }}</span>
              </div>

              <!-- Engagement Metrics -->
              <div class="flex items-center space-x-3 text-xs text-gray-500">
                <div class="flex items-center space-x-1">
                  <EyeIcon class="w-3 h-3" />
                  <span>{{ formatNumber(article.view_count || index * 234 + 123) }}</span>
                </div>

                <!-- Trending indicator -->
                <div v-if="index < 3" class="flex items-center text-orange-500">
                  <ArrowTrendingUpIcon class="w-3 h-3" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer CTA -->
    <div class="bg-gray-50 p-4 border-t border-gray-100">
      <Button
        variant="ghost"
        size="sm"
        class="w-full text-center text-gray-600 hover:text-gray-900"
        @click="viewAllTrending"
      >
        View All Trending
        <ArrowRightIcon class="w-4 h-4 ml-2" />
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  FireIcon,
  EyeIcon,
  ArrowTrendingUpIcon,
  ArrowRightIcon
} from '@heroicons/vue/24/outline'
import Button from './Button.vue'
import type { Article } from '@/types/api'

interface Props {
  articles: Article[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  navigateToArticle: [article: Article]
  viewAllTrending: []
}>()

// Sort articles by engagement (simulated - in real app, use actual metrics)
const trendingArticles = computed(() => {
  return [...props.articles].sort((a, b) => {
    // Simulate trending based on index, published date, and random factor
    const aScore = (props.articles.indexOf(a) * -0.1) +
                   (new Date(a.published_at || Date.now()).getTime()) +
                   Math.random()
    const bScore = (props.articles.indexOf(b) * -0.1) +
                   (new Date(b.published_at || Date.now()).getTime()) +
                   Math.random()
    return bScore - aScore
  })
})

const getRankColor = (index: number) => {
  const colors = [
    'bg-yellow-500', // #1
    'bg-gray-400',   // #2
    'bg-orange-600', // #3
    'bg-blue-500',   // #4
    'bg-purple-500'  // #5
  ]
  return colors[index] || 'bg-gray-500'
}

const formatTimeAgo = (dateString: string | null) => {
  if (!dateString) return 'Now'

  const date = new Date(dateString)
  const now = new Date()
  const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

  if (diffInHours < 1) return 'Just now'
  if (diffInHours < 24) return `${diffInHours}h ago`

  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`

  const diffInWeeks = Math.floor(diffInDays / 7)
  return `${diffInWeeks}w ago`
}

const calculateReadTime = (article: Article) => {
  const words = article.content?.split(' ').length || 0
  return Math.max(1, Math.ceil(words / 200))
}

const formatNumber = (num: number) => {
  if (num < 1000) return num.toString()
  if (num < 1000000) return `${(num / 1000).toFixed(1)}k`
  return `${(num / 1000000).toFixed(1)}M`
}

const navigateToArticle = (article: Article) => {
  emit('navigateToArticle', article)
}

const viewAllTrending = () => {
  emit('viewAllTrending')
}
</script>
