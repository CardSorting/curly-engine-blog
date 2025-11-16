// Service Worker for Chronicle Frontend
// Handles caching, offline support, and performance optimizations

const CACHE_NAME = 'chronicle-v1.0.0'
const STATIC_CACHE = 'chronicle-static-v1.0.0'
const API_CACHE = 'chronicle-api-v1.0.0'

// Assets to cache on installation
const STATIC_ASSETS = [
  '/',
  '/favicon.ico',
  '/manifest.json'
]

// API endpoints to cache
const API_ENDPOINTS = [
  '/articles/',
  '/topics/',
  '/pages/',
  '/analytics/',
  '/seo/'
]

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker')
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll(STATIC_ASSETS)
    }).then(() => {
      self.skipWaiting()
    })
  )
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker')
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName)
            return caches.delete(cacheName)
          }
        })
      )
    }).then(() => {
      self.clients.claim()
    })
  )
})

// Fetch event - serve from cache when available, cache new responses
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // Handle API requests
  if (url.hostname.includes('localhost') && API_ENDPOINTS.some(endpoint => url.pathname.includes(endpoint))) {
    event.respondWith(handleApiRequest(event.request))
    return
  }

  // Handle static assets
  if (event.request.destination === 'script' ||
      event.request.destination === 'style' ||
      event.request.destination === 'image' ||
      event.request.destination === 'font') {
    event.respondWith(handleStaticRequest(event.request))
    return
  }

  // Handle navigation requests
  if (event.request.mode === 'navigate') {
    event.respondWith(handleNavigationRequest(event.request))
    return
  }

  // Default - cache-first strategy
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request)
    })
  )
})

// Handle API requests with cache-first strategy
async function handleApiRequest(request) {
  try {
    // Try cache first
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      // Return cached response and update cache in background
      updateCache(request)
      return cachedResponse
    }

    // Fetch and cache
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(API_CACHE)
      cache.put(request, response.clone())
    }
    return response
  } catch (error) {
    console.error('[SW] API request failed:', error)
    // Return cached response if available, otherwise offline fallback
    const cachedResponse = await caches.match(request)
    if (cachedResponse) {
      return cachedResponse
    }

    // Return offline response for critical endpoints
    if (request.url.includes('/articles/')) {
      return new Response(
        JSON.stringify({
          error: 'Offline',
          message: 'Content not available offline. Please check your internet connection.'
        }),
        {
          status: 503,
          statusText: 'Service Unavailable',
          headers: { 'Content-Type': 'application/json' }
        }
      )
    }

    throw error
  }
}

// Handle static assets with cache-first strategy
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request)
  if (cachedResponse) {
    return cachedResponse
  }

  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(STATIC_CACHE)
      cache.put(request, response.clone())
    }
    return response
  } catch (error) {
    console.error('[SW] Static asset fetch failed:', error)
    throw error
  }
}

// Handle navigation requests
async function handleNavigationRequest(request) {
  try {
    const response = await fetch(request)
    return response
  } catch (error) {
    void error
    // Serve offline fallback for navigation requests
    const cache = await caches.open(STATIC_CACHE)
    const fallbackResponse = await cache.match('/')

    if (fallbackResponse) {
      return fallbackResponse
    }

    // Return basic offline page if no fallback available
    return new Response(
      `
      <!DOCTYPE html>
      <html>
        <head>
          <title>Offline - Chronicle</title>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
          <div style="text-align: center; padding: 50px; font-family: Arial, sans-serif;">
            <h1>You're Offline</h1>
            <p>Some content may not be available without an internet connection.</p>
            <p>Please check your connection and try again.</p>
          </div>
        </body>
      </html>
      `,
      {
        headers: { 'Content-Type': 'text/html' }
      }
    )
  }
}

// Update cache in background
async function updateCache(request) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(API_CACHE)
      cache.put(request, response)
    }
  } catch (error) {
    console.log('[SW] Background cache update failed:', error)
  }
}

// Message handler for cache management
self.addEventListener('message', (event) => {
  if (event.data && event.data.type) {
    switch (event.data.type) {
      case 'SKIP_WAITING':
        self.skipWaiting()
        break
      case 'CLEAR_CACHE':
        clearAllCaches()
        break
      case 'GET_CACHE_SIZE':
        getCacheSize().then((size) => {
          event.ports[0].postMessage({ cacheSize: size })
        })
        break
    }
  }
})

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys()
  await Promise.all(
    cacheNames.map((cacheName) => caches.delete(cacheName))
  )
}

// Get approximate cache size
async function getCacheSize() {
  let totalSize = 0
  const cacheNames = await caches.keys()

  for (const cacheName of cacheNames) {
    const cache = await caches.open(cacheName)
    const keys = await cache.keys()

    for (const request of keys) {
      try {
        const response = await cache.match(request)
        if (response) {
          const blob = await response.blob()
          totalSize += blob.size
        }
      } catch (error) {
        console.warn('[SW] Error calculating cache size:', error)
      }
    }
  }

  return totalSize
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag)

  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync())
  }
})

// Perform background synchronization
async function doBackgroundSync() {
  const cache = await caches.open(API_CACHE)
  const keys = await cache.keys()

  // Process any queued offline actions
  const offlineActions = []

  for (const request of keys) {
    if (request.url.includes('/pending/')) {
      offlineActions.push(request)
    }
  }

  return Promise.all(
    offlineActions.map(async (request) => {
      try {
        const response = await fetch(request)
        if (response.ok) {
          await cache.delete(request)
        }
      } catch (error) {
        void error
        console.log('[SW] Background sync failed for:', request.url)
      }
    })
  )
}

// Periodic cache cleanup
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'cache-cleanup') {
    event.waitUntil(cleanupExpiredCache())
  }
})

// Clean up expired cache entries
async function cleanupExpiredCache() {
  const cache = await caches.open(API_CACHE)
  const keys = await cache.keys()
  const now = Date.now()
  const maxAge = 24 * 60 * 60 * 1000 // 24 hours

  return Promise.all(
    keys.map(async (request) => {
      try {
        const response = await cache.match(request)
        if (response) {
          const date = response.headers.get('date')
          if (date && (now - new Date(date).getTime()) > maxAge) {
            await cache.delete(request)
          }
        }
      } catch (error) {
        console.warn('[SW] Error during cache cleanup:', error)
      }
    })
  )
}
