<template>
  <div
    v-if="showProgress && progress > 0"
    class="fixed top-20 left-0 right-0 z-50 pointer-events-none"
  >
    <!-- Progress Bar -->
    <div class="h-1 bg-gray-200 mx-4 md:mx-6 lg:mx-8">
      <div
        class="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 transition-all duration-300 ease-out"
        :style="{ width: `${Math.min(progress, 100)}%` }"
      ></div>
    </div>

    <!-- Reading Stats (Optional) -->
    <div v-if="showStats" class="bg-white border-b border-gray-100 px-4 md:px-6 lg:px-8 py-2">
      <div class="max-w-7xl mx-auto flex items-center justify-between text-sm">
        <div class="flex items-center space-x-4 text-gray-600">
          <span>{{ Math.round(progress) }}% complete</span>
          <span class="text-gray-300">•</span>
          <span>{{ estimatedTimeRemaining }} left</span>
          <span v-if="wordsPerMinute" class="text-gray-300">•</span>
          <span v-if="wordsPerMinute">{{ wordsPerMinute }} WPM</span>
        </div>

        <div v-if="showBookmarks" class="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            class="pointer-events-auto text-gray-600 hover:text-gray-900"
            @click="bookmarkCurrentPosition"
            :disabled="isBookmarked"
          >
            <BookmarkIcon
              :class="isBookmarked ? 'fill-current' : ''"
              class="w-4 h-4"
            />
            <span class="ml-1">{{ isBookmarked ? 'Bookmarked' : 'Bookmark' }}</span>
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watchEffect } from 'vue'
import { BookmarkIcon } from '@heroicons/vue/24/outline'
import Button from './Button.vue'

interface Props {
  content?: string
  showProgress?: boolean
  showStats?: boolean
  showBookmarks?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showProgress: true,
  showStats: false,
  showBookmarks: true,
})

const emit = defineEmits<{
  bookmark: [position: number]
  progressUpdate: [progress: number]
}>()

const progress = ref(0)
const scrollY = ref(0)
const documentHeight = ref(0)
const isBookmarked = ref(false)

const estimatedTimeRemaining = computed(() => {
  if (!props.content) return '0 min'

  const words = props.content.split(/\s+/).length
  const wordsRemaining = words - (words * progress.value) / 100
  const timeRemaining = Math.ceil(wordsRemaining / 200) // Assuming 200 words per minute

  if (timeRemaining <= 1) return '< 1 min'
  return `${timeRemaining} min`
})

const wordsPerMinute = computed(() => {
  if (!props.content || progress.value === 0) return null
  const words = props.content.split(/\s+/).length
  const wordsRead = (words * progress.value) / 100
  // Estimated based on current progress and assuming 1 minute read time
  return Math.round(wordsRead)
})

const updateProgress = () => {
  scrollY.value = window.scrollY
  documentHeight.value = document.documentElement.scrollHeight - window.innerHeight
  progress.value = Math.min((scrollY.value / documentHeight.value) * 100, 100)

  emit('progressUpdate', progress.value)
}

onMounted(() => {
  window.addEventListener('scroll', updateProgress, { passive: true })
  window.addEventListener('resize', updateProgress)

  // Initial calculation
  updateProgress()

  // Check if current position is bookmarked
  checkBookmarkStatus()
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateProgress)
  window.removeEventListener('resize', updateProgress)
})

const bookmarkCurrentPosition = () => {
  if (isBookmarked.value) return

  isBookmarked.value = true
  emit('bookmark', progress.value)

  // Reset bookmark after 3 seconds for demo
  setTimeout(() => {
    isBookmarked.value = false
  }, 3000)
}

const checkBookmarkStatus = () => {
  // In a real app, check stored bookmarks for current article
  // For now, just reset
  isBookmarked.value = false
}

// Watch for content changes
watchEffect(() => {
  if (props.content) {
    // Recalculate on content change
    updateProgress()
  }
})
</script>
