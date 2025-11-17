<template>
  <div class="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer group hover:shadow-xl transition-all duration-300" @click="handleClick">
    <!-- Image -->
    <div class="h-48 overflow-hidden relative">
      <LazyImage
        v-if="articleImage"
        :src="articleImage"
        :alt="title"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
      />
      <div v-else class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <div class="text-gray-400 text-3xl">{{ icon || '📰' }}</div>
      </div>

      <!-- Category Badge -->
      <div v-if="category" class="absolute top-3 left-3">
        <span class="inline-block px-2 py-1 bg-white/90 text-gray-800 text-xs font-medium rounded-md">
          {{ category }}
        </span>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6">
      <!-- Title -->
      <h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-2 leading-tight group-hover:text-blue-600 transition-colors line-clamp-2">
        {{ title }}
      </h3>

      <!-- Excerpt -->
      <p class="text-gray-600 text-sm md:text-base mb-4 line-clamp-3">
        {{ excerpt }}
      </p>

      <!-- Meta Information -->
      <div class="flex items-center justify-between text-xs md:text-sm text-gray-500">
        <div class="flex items-center space-x-3">
          <div class="flex items-center space-x-1">
            <UserIcon class="w-3 h-3 md:w-4 md:h-4" />
            <span>{{ author }}</span>
          </div>
          <div class="flex items-center space-x-1">
            <ClockIcon class="w-3 h-3 md:w-4 md:h-4" />
            <span>{{ formattedDate }}</span>
          </div>
        </div>

        <div class="flex items-center space-x-1">
          <EyeIcon class="w-3 h-3 md:w-4 md:h-4" />
          <span>{{ readTime }} min</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { UserIcon, ClockIcon, EyeIcon } from '@heroicons/vue/24/outline'
import LazyImage from './LazyImage.vue'
import type { Article } from '@/types/api'

interface Props {
  article: Article
  articleImage?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: '📰',
})

const emit = defineEmits<{
  click: [article: Article]
}>()

const title = computed(() => props.article.title)
const excerpt = computed(() => props.article.excerpt)
const author = computed(() => props.article.author?.username || 'Anonymous')
const category = computed(() => props.article.topic?.name || null)
const formattedDate = computed(() => {
  if (!props.article.published_at) return ''
  return new Date(props.article.published_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
})
const readTime = computed(() => {
  // Estimate read time based on content length (rough estimate)
  const words = props.article.content?.split(' ').length || 0
  return Math.max(1, Math.ceil(words / 200))
})

const handleClick = () => {
  emit('click', props.article)
}
</script>
