<template>
  <div class="relative w-full h-96 md:h-[500px] bg-gray-900 rounded-xl overflow-hidden cursor-pointer group" @click="handleClick">
    <!-- Background Image -->
    <div class="absolute inset-0">
      <LazyImage
        v-if="heroImage"
        :src="heroImage"
        :alt="title"
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="eager"
      />
      <div v-else class="w-full h-full bg-gradient-to-br from-blue-900 to-purple-900 flex items-center justify-center">
        <div class="text-white text-6xl md:text-8xl opacity-20">{{ icon || '📝' }}</div>
      </div>
    </div>

    <!-- Overlay -->
    <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent"></div>

    <!-- Content -->
    <div class="absolute bottom-0 left-0 right-0 p-6 md:p-8">
      <div class="max-w-4xl">
        <!-- Category Badge -->
        <div v-if="category" class="mb-3">
          <span class="inline-block px-3 py-1 bg-white/20 text-white text-sm font-medium rounded-full backdrop-blur-sm">
            {{ category }}
          </span>
        </div>

        <!-- Title -->
        <h1 class="text-2xl md:text-4xl font-bold text-white mb-3 leading-tight">
          {{ title }}
        </h1>

        <!-- Excerpt -->
        <p v-if="excerpt" class="text-sm md:text-lg text-gray-200 mb-4 line-clamp-3 leading-relaxed">
          {{ excerpt }}
        </p>

        <!-- Meta Information -->
        <div class="flex items-center space-x-4 text-sm text-gray-300">
          <div class="flex items-center space-x-2">
            <UserIcon class="w-4 h-4" />
            <span>{{ author }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <ClockIcon class="w-4 h-4" />
            <span>{{ formattedDate }}</span>
          </div>
          <div class="flex items-center space-x-2">
            <EyeIcon class="w-4 h-4" />
            <span>{{ readTime }} min read</span>
          </div>
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
  heroImage?: string
  icon?: string
}

const props = withDefaults(defineProps<Props>(), {
  icon: '📝',
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
