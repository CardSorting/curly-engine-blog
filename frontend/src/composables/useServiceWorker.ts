import { ref, computed } from 'vue'

interface ServiceWorkerState {
  isSupported: boolean
  isRegistered: boolean
  isUpdating: boolean
  updateAvailable: boolean
  isOffline: boolean
  registration: ServiceWorkerRegistration | null
}

let serviceWorkerRegistration: ServiceWorkerRegistration | null = null

export function useServiceWorker() {
  const state = ref<ServiceWorkerState>({
    isSupported: 'serviceWorker' in navigator,
    isRegistered: false,
    isUpdating: false,
    updateAvailable: false,
    isOffline: !navigator.onLine,
    registration: null
  })

  // Computed properties
  const isSupported = computed(() => state.value.isSupported)
  const isRegistered = computed(() => state.value.isRegistered)
  const isUpdating = computed(() => state.value.isUpdating)
  const updateAvailable = computed(() => state.value.updateAvailable)
  const isOffline = computed(() => state.value.isOffline)

  // Register service worker
  const register = async (): Promise<void> => {
    if (!state.value.isSupported) {
      console.warn('[SW] Service workers are not supported in this browser')
      return
    }

    try {
      console.log('[SW] Registering service worker...')
      serviceWorkerRegistration = await navigator.serviceWorker.register('/sw.js', {
        scope: '/'
      })

      state.value.registration = serviceWorkerRegistration
      state.value.isRegistered = true

      console.log('[SW] Service worker registered successfully')

      // Listen for updates
      serviceWorkerRegistration.addEventListener('updatefound', handleUpdateFound)

      // Check for updates
      checkForUpdates()

    } catch (error) {
      console.error('[SW] Failed to register service worker:', error)
      state.value.isRegistered = false
    }
  }

  // Handle service worker update found
  const handleUpdateFound = () => {
    if (!serviceWorkerRegistration) return

    const newWorker = serviceWorkerRegistration.installing
    if (!newWorker) return

    newWorker.addEventListener('statechange', () => {
      if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
        state.value.updateAvailable = true
        console.log('[SW] New content is available and will be used when all tabs for this page are closed.')
      }
    })
  }

  // Update service worker
  const update = async (): Promise<void> => {
    if (!serviceWorkerRegistration) return

    try {
      state.value.isUpdating = true

      // Send message to service worker to skip waiting
      serviceWorkerRegistration.waiting?.postMessage({ type: 'SKIP_WAITING' })

      // Reload page after update
      setTimeout(() => {
        window.location.reload()
      }, 100)

    } catch (error) {
      console.error('[SW] Failed to update service worker:', error)
      state.value.isUpdating = false
    }
  }

  // Skip waiting and activate update immediately
  const skipWaiting = (): void => {
    if (serviceWorkerRegistration?.waiting) {
      serviceWorkerRegistration.waiting.postMessage({ type: 'SKIP_WAITING' })
      state.value.updateAvailable = false
    }
  }

  // Check for updates
  const checkForUpdates = async (): Promise<void> => {
    if (!serviceWorkerRegistration) return

    try {
      await serviceWorkerRegistration.update()
    } catch (error) {
      console.log('[SW] Update check failed:', error)
    }
  }

  // Clear all caches
  const clearCache = async (): Promise<void> => {
    if (!serviceWorkerRegistration) return

    try {
      serviceWorkerRegistration.active?.postMessage({ type: 'CLEAR_CACHE' })
    } catch (error) {
      console.error('[SW] Failed to clear cache:', error)
    }
  }

  // Get cache size
  const getCacheSize = async (): Promise<number> => {
    return new Promise((resolve, reject) => {
      if (!serviceWorkerRegistration?.active) {
        resolve(0)
        return
      }

      const messageChannel = new MessageChannel()
      messageChannel.port1.onmessage = (event) => {
        resolve(event.data.cacheSize || 0)
      }

      serviceWorkerRegistration.active.postMessage(
        { type: 'GET_CACHE_SIZE' },
        [messageChannel.port2]
      )

      // Timeout after 5 seconds
      setTimeout(() => reject(new Error('Cache size request timeout')), 5000)
    })
  }

  // Handle online/offline events
  const handleOnline = () => {
    state.value.isOffline = false
    console.log('[SW] Connection restored')
  }

  const handleOffline = () => {
    state.value.isOffline = true
    console.log('[SW] Connection lost')
  }

  // Listen for messages from service worker
  const handleMessage = (event: MessageEvent) => {
    if (event.data && event.data.type) {
      switch (event.data.type) {
        case 'UPDATE_AVAILABLE':
          state.value.updateAvailable = true
          break
        case 'CACHE_CLEARED':
          console.log('[SW] Cache cleared')
          break
        default:
          break
      }
    }
  }

  // Initialize service worker
  const init = (): void => {
    // Register message listener
    navigator.serviceWorker.addEventListener('message', handleMessage)

    // Listen for online/offline events
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Set initial online status
    state.value.isOffline = !navigator.onLine
  }

  // Cleanup
  const destroy = (): void => {
    navigator.serviceWorker.removeEventListener('message', handleMessage)
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  }

  // Initialize
  init()

  return {
    // State
    isSupported,
    isRegistered,
    isUpdating,
    updateAvailable,
    isOffline,
    serviceWorkerRegistration,

    // Methods
    register,
    update,
    skipWaiting,
    checkForUpdates,
    clearCache,
    getCacheSize,
    destroy
  }
}

// Global service worker instance (for use throughout the app)
let globalServiceWorker: ReturnType<typeof useServiceWorker> | null = null

export function getGlobalServiceWorker() {
  if (!globalServiceWorker) {
    globalServiceWorker = useServiceWorker()
  }
  return globalServiceWorker
}

// Auto-register service worker (call this in main.ts)
export async function registerServiceWorker() {
  const sw = getGlobalServiceWorker()
  await sw.register()
}

// Service worker update prompt component helper
export function useUpdatePrompt() {
  const sw = getGlobalServiceWorker()

  const showUpdatePrompt = computed(() =>
    sw.updateAvailable.value && !sw.isUpdating.value
  )

  const acceptUpdate = () => {
    sw.update()
  }

  const dismissUpdate = () => {
    sw.skipWaiting()
  }

  return {
    showUpdatePrompt,
    acceptUpdate,
    dismissUpdate,
    isUpdating: sw.isUpdating
  }
}
