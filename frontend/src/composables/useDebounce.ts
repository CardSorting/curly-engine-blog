import { ref, type Ref, watch, onUnmounted } from 'vue'

/**
 * Composable for debouncing values and functions
 */
export function useDebounce<T>(value: Ref<T>, delay: number = 300): Ref<T> {
  const debouncedValue = ref(value.value) as Ref<T>
  let timeoutId: number | null = null

  watch(
    value,
    (newValue) => {
      if (timeoutId) {
        clearTimeout(timeoutId)
      }

      timeoutId = window.setTimeout(() => {
        debouncedValue.value = newValue
      }, delay)
    },
    { immediate: true }
  )

  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return debouncedValue
}

/**
 * Composable for debouncing function calls
 */
export function useDebounceFn<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): {
  debouncedFn: T
  cancel: () => void
  flush: () => void
} {
  let timeoutId: number | null = null
  let lastArgs: any[] | null = null

  const cancel = () => {
    if (timeoutId) {
      clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  const flush = () => {
    if (timeoutId) {
      cancel()
      if (lastArgs) {
        fn(...lastArgs)
        lastArgs = null
      }
    }
  }

  const debouncedFn = ((...args: Parameters<T>) => {
    lastArgs = args
    cancel()

    timeoutId = window.setTimeout(() => {
      fn(...args)
      lastArgs = null
      timeoutId = null
    }, delay)
  }) as T

  onUnmounted(() => {
    cancel()
  })

  return {
    debouncedFn,
    cancel,
    flush,
  }
}

/**
 * Composable for API request throttling
 */
export function useThrottle<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  delay: number = 1000
): T {
  let lastCall = 0
  let timeoutId: number | null = null

  const throttledFn = ((...args: Parameters<T>) => {
    const now = Date.now()

    if (now - lastCall >= delay) {
      lastCall = now
      return fn(...args)
    } else {
      if (timeoutId) clearTimeout(timeoutId)

      return new Promise((resolve, reject) => {
        timeoutId = window.setTimeout(async () => {
          lastCall = Date.now()
          try {
            const result = await fn(...args)
            resolve(result)
          } catch (error) {
            reject(error)
          }
        }, delay - (now - lastCall))
      })
    }
  }) as T

  onUnmounted(() => {
    if (timeoutId) {
      clearTimeout(timeoutId)
    }
  })

  return throttledFn
}

/**
 * Composable for rate limiting API calls
 */
export function useRateLimit<T extends (...args: any[]) => any>(
  fn: T,
  maxCalls: number = 10,
  windowMs: number = 1000
): T {
  const calls: number[] = []

  const rateLimitedFn = ((...args: Parameters<T>) => {
    const now = Date.now()

    // Remove calls outside the window
    while (calls.length > 0 && calls[0] !== undefined && calls[0] < now - windowMs) {
      calls.shift()
    }

    // Check if under the limit
    if (calls.length < maxCalls) {
      calls.push(now)
      return fn(...args)
    } else {
      // Calculate wait time until next call is allowed
      const oldestCall = calls[0] !== undefined ? calls[0] : now
      const waitTime = windowMs - (now - oldestCall)

      return new Promise((resolve, reject) => {
        setTimeout(async () => {
          calls.push(Date.now())
          try {
            const result = await fn(...args)
            resolve(result)
          } catch (error) {
            reject(error)
          }
        }, waitTime)
      })
    }
  }) as T

  return rateLimitedFn
}

/**
 * Composable for search input with debounce
 */
export function useSearch(
  initialQuery: string = '',
  delay: number = 300
): {
  query: Ref<string>
  debouncedQuery: Ref<string>
  isSearching: Ref<boolean>
  search: (newQuery: string) => void
  clear: () => void
} {
  const query = ref(initialQuery)
  const debouncedQuery = useDebounce(query, delay)
  const isSearching = ref(false)

  const search = (newQuery: string) => {
    query.value = newQuery
    if (newQuery.trim()) {
      isSearching.value = true
    } else {
      isSearching.value = false
    }
  }

  const clear = () => {
    query.value = ''
    debouncedQuery.value = ''
    isSearching.value = false
  }

  // Auto-clear search state when debounced query changes
  watch(debouncedQuery, (newDebouncedQuery) => {
    if (!newDebouncedQuery.trim()) {
      isSearching.value = false
    }
  })

  return {
    query,
    debouncedQuery,
    isSearching,
    search,
    clear,
  }
}

/**
 * Composable for debounced API calls
 */
export function useDebounceApi<T extends (...args: any[]) => Promise<any>>(
  apiFn: T,
  delay: number = 300
): {
  debouncedApi: T
  cancel: () => void
  isPending: Ref<boolean>
} {
  const { debouncedFn, cancel } = useDebounceFn(apiFn, delay)
  const isPending = ref(false)

  const debouncedApi = (async (...args: Parameters<T>) => {
    isPending.value = true
    try {
      const result = await debouncedFn(...args)
      return result
    } finally {
      isPending.value = false
    }
  }) as T

  return {
    debouncedApi,
    cancel,
    isPending,
  }
}
