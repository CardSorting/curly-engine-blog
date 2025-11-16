<template>
  <slot v-if="!hasError" />

  <!-- Error fallback UI -->
  <div
    v-else
    class="min-h-[400px] flex items-center justify-center p-8 bg-red-50 border border-red-200 rounded-lg"
  >
    <div class="max-w-md w-full text-center space-y-4">
      <div class="mx-auto w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
        <ExclamationTriangleIcon class="w-6 h-6 text-red-600" />
      </div>

      <div>
        <h3 class="text-lg font-medium text-red-900">
          {{ title || 'Something went wrong' }}
        </h3>
        <p class="mt-2 text-sm text-red-700">
          {{ message || 'An unexpected error occurred. Please try refreshing the page.' }}
        </p>
      </div>

      <!-- Error details (only in development) -->
      <details v-if="isDevelopment" class="mt-4 text-left">
        <summary class="cursor-pointer text-sm font-medium text-red-800 hover:text-red-900">
          Error Details
        </summary>
        <div class="mt-2 p-3 bg-red-100 rounded border text-xs font-mono whitespace-pre-wrap text-red-900 max-h-64 overflow-y-auto">
          <div class="mb-2">
            <strong>Error:</strong>
            <pre class="mt-1">{{ errorMessage }}</pre>
          </div>
          <div v-if="errorStack" class="mb-2">
            <strong>Stack:</strong>
            <pre class="mt-1">{{ errorStack }}</pre>
          </div>
          <div v-if="componentStack">
            <strong>Component Stack:</strong>
            <pre class="mt-1">{{ componentStack }}</pre>
          </div>
        </div>
      </details>

      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <Button
          @click="retry"
          variant="primary"
          :disabled="retrying"
        >
          {{ retrying ? 'Retrying...' : retryText || 'Try Again' }}
        </Button>

        <Button
          v-if="showRefresh"
          @click="refreshPage"
          variant="outline"
        >
          {{ refreshText || 'Refresh Page' }}
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onErrorCaptured } from 'vue'
import Button from './Button.vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

// Props
interface Props {
  title?: string
  message?: string
  retryText?: string
  refreshText?: string
  showRefresh?: boolean
  maxRetries?: number
  onError?: (error: Error, instance: any, info: string) => void
  onRetry?: () => void
}

const props = withDefaults(defineProps<Props>(), {
  showRefresh: true,
  maxRetries: 3,
})

// State
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref<string>('')
const retryCount = ref(0)
const retrying = ref(false)

// Computed
const isDevelopment = computed(() => import.meta.env.DEV)

const errorMessage = computed(() => {
  if (!error.value) return ''
  return error.value.message || 'Unknown error'
})

const errorStack = computed(() => {
  if (!error.value) return ''
  return error.value.stack || ''
})

const componentStack = computed(() => {
  return errorInfo.value || ''
})

// Methods
const handleError = (err: Error, instance: any, info: string) => {
  console.error('[ErrorBoundary] Error captured:', err)
  console.error('[ErrorBoundary] Component instance:', instance)
  console.error('[ErrorBoundary] Error info:', info)

  hasError.value = true
  error.value = err
  errorInfo.value = info

  // Call custom error handler if provided
  if (props.onError) {
    props.onError(err, instance, info)
  }

  // Log to analytics/error reporting service in production
  if (!isDevelopment.value) {
    // Example: send to error reporting service
    // reportError(err, { componentStack: info, ...additionalContext })
  }
}

const retry = async () => {
  if (retryCount.value >= props.maxRetries) {
    return
  }

  retrying.value = true
  retryCount.value++

  try {
    // Reset error state
    hasError.value = false
    error.value = null
    errorInfo.value = ''

    // Call custom retry handler
    if (props.onRetry) {
      await props.onRetry()
    }

    // Wait a bit for re-rendering
    await new Promise(resolve => setTimeout(resolve, 100))
  } catch (err) {
    console.error('[ErrorBoundary] Retry failed:', err)
    handleError(err as Error, null, 'Retry failed')
  } finally {
    retrying.value = false
  }
}

const refreshPage = () => {
  window.location.reload()
}

// Error capturing hook (Vue 3 composition API)
onErrorCaptured((err, instance, info) => {
  handleError(err, instance, info)
  return false // Prevent error from propagating further
})
</script>

<style scoped>
/* Additional error boundary styles can go here */
</style>
