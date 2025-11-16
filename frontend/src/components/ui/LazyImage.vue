<template>
  <div class="lazy-image-container" :style="{ height: imageHeight + 'px', width: imageWidth + 'px' }">
    <!-- Loading placeholder -->
    <div
      v-if="isLoading || showPlaceholder"
      class="lazy-image-placeholder"
      :style="{ backgroundColor: placeholderColor }"
    >
      <slot v-if="showPlaceholder" name="placeholder">
        <div class="flex items-center justify-center h-full">
          <div class="animate-pulse text-gray-400">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </slot>
    </div>

    <!-- Actual image -->
    <img
      v-show="!isLoading && !hasError"
      ref="imgRef"
      :src="currentSrc"
      :alt="alt"
      :class="imgClass"
      :style="imgStyle"
      @load="handleLoad"
      @error="handleError"
      :loading="loading"
      :fetchpriority="fetchpriority"
      :decoding="decoding"
    />

    <!-- Error state -->
    <div
      v-if="hasError"
      class="lazy-image-error"
      :style="{ height: imageHeight + 'px', width: imageWidth + 'px' }"
    >
      <slot name="error">
        <div class="flex items-center justify-center h-full text-red-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

interface Props {
  src: string
  alt?: string
  width?: number | string
  height?: number | string
  aspectRatio?: string // e.g., "16/9", "4/3"
  placeholderColor?: string
  imgClass?: string
  imgStyle?: Record<string, any>
  loading?: 'lazy' | 'eager'
  fetchpriority?: 'high' | 'low' | 'auto'
  decoding?: 'sync' | 'async' | 'auto'
  rootMargin?: string
  threshold?: number | number[]
  enablePlaceholder?: boolean
  srcSet?: string
  sizes?: string
  progressive?: boolean
  blurDataUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  alt: '',
  placeholderColor: '#f3f4f6',
  imgClass: '',
  loading: 'lazy',
  fetchpriority: 'auto',
  decoding: 'async',
  rootMargin: '50px',
  threshold: 0.1,
  enablePlaceholder: true,
  progressive: false
})

const emit = defineEmits<{
  load: [event: Event]
  error: [event: Event]
  intersect: [entry: IntersectionObserverEntry]
}>()

// Refs
const imgRef = ref<HTMLImageElement>()
const observer = ref<IntersectionObserver | null>(null)

// State
const isLoading = ref(true)
const hasError = ref(false)
const isInView = ref(false)
const showPlaceholder = ref(props.enablePlaceholder)

// Computed properties
const imageWidth = computed(() => {
  if (typeof props.width === 'number') return props.width
  if (typeof props.width === 'string') return parseInt(props.width, 10) || 300
  return 300
})

const imageHeight = computed(() => {
  if (typeof props.height === 'number') return props.height
  if (props.aspectRatio) {
    const [width, height] = props.aspectRatio.split('/').map(Number)
    if (width && height) {
      return (imageWidth.value * height) / width
    }
  }
  return 200
})

const currentSrc = computed(() => {
  if (!isInView.value && props.loading === 'lazy') return ''
  return props.src
})

// Methods
const createObserver = () => {
  if (!props.enablePlaceholder && props.loading !== 'lazy') return

  const options: IntersectionObserverInit = {
    rootMargin: props.rootMargin,
    threshold: props.threshold
  }

  observer.value = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        isInView.value = true
        emit('intersect', entry)
        observer.value?.unobserve(entry.target)
      }
    })
  }, options)
}

const observeElement = () => {
  if (observer.value && imgRef.value) {
    observer.value.observe(imgRef.value)
  }
}

const handleLoad = (event: Event) => {
  isLoading.value = false
  showPlaceholder.value = false
  emit('load', event)
}

const handleError = (event: Event) => {
  isLoading.value = false
  hasError.value = true
  emit('error', event)
}

// Lifecycle
const setupProgressiveLoading = async () => {
  if (!props.progressive || !props.blurDataUrl) return

  // For progressive loading, we show the blur placeholder first
  showPlaceholder.value = true

  // Create a tiny blur image first
  const blurImg = new Image()
  blurImg.src = props.blurDataUrl

  // When blur image loads, transition to actual image
  blurImg.onload = () => {
    nextTick(() => {
      // Gradually transition from blur to actual image
      setTimeout(() => {
        showPlaceholder.value = false
      }, 100) // Small delay for smooth transition
    })
  }
}

onMounted(async () => {
  createObserver()
  observeElement()

  // Setup progressive loading if enabled
  if (props.progressive) {
    await setupProgressiveLoading()
  } else if (!props.enablePlaceholder) {
    isInView.value = true
  }
})

onUnmounted(() => {
  if (observer.value) {
    observer.value.disconnect()
  }
})

// Expose methods for parent components
defineExpose({
  reload: () => {
    hasError.value = false
    isLoading.value = true
    const img = imgRef.value
    if (img) {
      img.src = props.src
    }
  },
  observer,
  imgRef
})
</script>

<style scoped>
.lazy-image-container {
  position: relative;
  overflow: hidden;
}

.lazy-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lazy-image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgb(243 244 246);
}

.lazy-image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: opacity 0.3s ease-in-out;
}
</style>
