<template>
  <div class="flex flex-col md:flex-row bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer group hover:shadow-xl transition-all duration-300" @click="handleClick">
    <!-- Image Section -->
    <div class="md:w-1/2 h-48 md:h-auto relative">
      <LazyImage
        v-if="featuredImage"
        :src="featuredImage"
        :alt="title"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
      />
      <div v-else class="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <div class="text-gray-400 text-3xl">{{ icon || '📄' }}</div>
      </div>

      <!-- Category Badge -->
      <div v-if="category" class="absolute top-4 left-4">
        <span class="inline-block px-3 py-1 bg-black/70 text-white text-xs font-medium rounded-full backdrop-blur-sm">
          {{ category }}
        </span>
      </div>
    </div>

    <!-- Content Section -->
    <div class="md:w-1/2 p-6 md:p-8 flex flex-col">
      <!-- Title -->
      <h3 class="text-xl md:text-2xl font-bold text-gray-900 mb-3 leading-tight group-hover:text-blue-600 transition-colors">
        {{ title }}
      </h3>

      <!-- Excerpt -->
      <p class="text-gray-600 mb-4 line-clamp-3 flex-grow">
        {{ excerpt }}
      </p>

      <!-- Meta Information -->
      <div class="flex items-center justify-between text-sm text-gray-500">
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <UserIcon class="w-4 h-4" />
            <span>{{ author }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <ClockIcon class="w-4 h-4" />
            <span>{{ formattedDate }}</span>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <EyeIcon class="w-4 h-4" />
          <span>{{ readTime }} min read</span>
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
  featuredImage?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: '📄',
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
    year: 'numeric',
    month: 'long',
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
