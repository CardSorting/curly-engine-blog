<template>
  <div
    v-if="currentAccount"
    :class="[
      'min-h-screen bg-gray-50',
      `theme-${currentAccount.slug}` // For future theming support
    ]"
  >
    <!-- Account-specific Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <!-- Account branding -->
            <router-link
              to="blog-home"
              class="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full">
                <span class="text-white font-bold text-sm">{{ getAccountInitials }}</span>
              </div>
              <div>
                <h1 class="text-lg font-semibold text-gray-900">{{ currentAccount.name }}</h1>
                <p class="text-xs text-gray-500">{{ currentAccount.description }}</p>
              </div>
            </router-link>
          </div>

          <div class="flex items-center space-x-6">
            <!-- Main navigation -->
            <div class="hidden md:flex items-center space-x-4">
              <router-link
                to="blog-home"
                class="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors"
                :class="{ 'text-blue-600': $route.name === 'account-home' }"
              >
                Home
              </router-link>
              <a
                href="#about"
                class="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors"
              >
                About
              </a>
              <router-link
                :to="{ name: 'search' }"
                class="text-gray-600 hover:text-gray-900 text-sm font-medium transition-colors"
              >
                Search
              </router-link>
            </div>

            <!-- Authentication actions -->
            <div v-if="!isAuthenticated">
              <router-link
                to="/login"
                class="text-gray-600 hover:text-gray-900 text-sm font-medium"
              >
                Sign In
              </router-link>
            </div>
            <div v-else class="flex items-center space-x-2">
              <router-link
                :to="{ name: 'admin-dashboard', params: { accountSlug: currentAccount.slug } }"
                class="bg-blue-600 text-white px-3 py-1.5 rounded-md text-sm font-medium hover:bg-blue-700 transition-colors"
              >
                Manage
              </router-link>
            </div>

            <!-- Theme Toggle -->
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>

    <!-- Account-specific Hero Section -->
    <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div class="text-center">
          <h1 class="text-4xl md:text-5xl font-bold mb-6">
            {{ currentAccount.name }}
          </h1>
          <p class="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
            {{ currentAccount.description || 'A curated editorial space for thoughtful content' }}
          </p>
          <div class="flex flex-col sm:flex-row justify-center gap-4">
            <router-link
              to="blog-home"
              class="inline-block bg-white text-blue-600 px-8 py-3 rounded-md font-semibold hover:bg-gray-50 transition-colors"
            >
              Explore Content
            </router-link>
            <button
              v-if="!isAuthenticated"
              @click="$router.push('/login')"
              class="inline-block border-2 border-white text-white px-8 py-3 rounded-md font-semibold hover:bg-white hover:text-blue-600 transition-colors"
            >
              Start Your Own
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div v-if="loadingArticles" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading latest articles...</p>
      </div>

      <div v-else-if="articles?.length">
        <div class="mb-8">
          <h2 class="text-3xl font-bold text-gray-900 mb-2">Latest Articles</h2>
          <p class="text-gray-600">Discover the most recent content from {{ currentAccount.name }}</p>
        </div>

        <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3 mb-12">
          <Card
            v-for="article in articles.slice(0, 6)"
            :key="article.id"
            :title="article.title"
            :subtitle="`By ${article.author_name || 'Author'} • ${formatDate(article.published_at)}`"
            :content="article.excerpt"
            clickable
            class="h-full"
            @click="() => navigateToArticle(article)"
          />
        </div>

        <div class="text-center" v-if="articles.length >= 6">
          <router-link
            to="blog-home"
            class="inline-block bg-gray-900 text-white px-8 py-3 rounded-md font-semibold hover:bg-gray-800 transition-colors"
          >
            View All Articles
          </router-link>
        </div>
      </div>

      <!-- Account Stats Section -->
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-12">
        <h3 class="text-2xl font-bold text-gray-900 mb-6 text-center">About {{ currentAccount.name }}</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div class="text-3xl font-bold text-blue-600 mb-2">{{ currentAccount.current_article_count }}</div>
            <div class="text-gray-600">Articles Published</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-green-600 mb-2">
              {{ currentAccount.subscription_status === 'active' ? 'Active' : 'Free Trial' }}
            </div>
            <div class="text-gray-600">Status</div>
          </div>
          <div>
            <div class="text-3xl font-bold text-purple-600 mb-2">{{ formatSubscriptionDate(currentAccount.created_at) }}</div>
            <div class="text-gray-600">Since</div>
          </div>
        </div>
      </div>

      <!-- Call to Action for Unauthenticated Users -->
      <div v-if="!isAuthenticated" class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8 text-center mb-12">
        <h3 class="text-2xl font-bold text-gray-900 mb-4">Ready to Start Your Own Editorial?</h3>
        <p class="text-gray-600 mb-6 max-w-2xl mx-auto">
          Join the community of writers and creators sharing their stories on Chronicle.
          Create your own branded editorial space today.
        </p>
        <router-link
          to="/login"
          class="inline-block bg-green-600 text-white px-8 py-3 rounded-md font-semibold hover:bg-green-700 transition-colors"
        >
          Get Started Free
        </router-link>
      </div>
    </main>

    <!-- Account Footer -->
    <footer class="bg-gray-50 border-t">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="flex items-center space-x-3 mb-4 md:mb-0">
            <div class="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full">
              <span class="text-white font-bold text-sm">{{ getAccountInitials }}</span>
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">{{ currentAccount.name }}</h4>
              <p class="text-sm text-gray-500">{{ currentAccount.slug }}</p>
            </div>
          </div>

          <div class="flex items-center space-x-6 text-sm text-gray-600">
            <div>© {{ new Date().getFullYear() }} {{ currentAccount.name }}</div>
            <div>•</div>
            <div>Powered by Chronicle</div>
          </div>
        </div>
      </div>
    </footer>
  </div>

  <!-- Loading state for account -->
  <div v-else-if="loadingAccount" class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading editorial...</p>
    </div>
  </div>

  <!-- Error state -->
  <div v-else class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <div class="text-6xl mb-4">📝</div>
      <h1 class="text-2xl font-bold text-gray-900 mb-2">
        {{ accountError ? 'Editorial Error' : 'Editorial Not Found' }}
      </h1>
      <p class="text-gray-600 mb-6">
        {{ accountError || 'The editorial you\'re looking for doesn\'t exist or has been removed.' }}
      </p>
      <div class="space-x-4">
        <Button @click="retryLoad" variant="primary">
          Try Again
        </Button>
        <router-link
          to="/"
          class="inline-block bg-gray-600 text-white px-6 py-3 rounded-md font-semibold hover:bg-gray-700 transition-colors"
        >
          Browse Editorials
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import { useArticles } from '@/composables/useApi'
import { apiClient } from '@/services/api/config'
import type { Account, Article } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tenantStore = useTenantStore()

// Reactive state
const loadingAccount = ref(true)
const loadingArticles = ref(true)
const accountId = ref<string | null>(null)
const accountError = ref<string | null>(null)

// Computed properties
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentAccount = computed(() => tenantStore.currentAccount)

const accountSlug = computed(() => route.params.accountSlug as string)

const getAccountInitials = computed(() => {
  if (!currentAccount.value?.name) return 'A'
  return currentAccount.value.name
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)
})

interface ArticleSummary {
  id: string
  title: string
  slug: string
  excerpt: string
  published_at: string | null
  author_name: string
}

// API compositions
const { data: articles, loading, error, fetchArticles } = useArticles<ArticleSummary[]>()

// Methods
const loadAccount = async (slug: string) => {
  try {
    loadingAccount.value = true

    // Fetch account details from the API using proper endpoint format
    const response = await apiClient.get(`/accounts/public_detail/?slug=${encodeURIComponent(slug)}`)

    // Validate that we received a proper account object
    if (response.data && response.data.slug === slug) {
      tenantStore.setCurrentAccount(response.data)
    } else {
      throw new Error('Invalid account data received')
    }
  } catch (err: any) {
    console.error('Failed to load account:', err)

    // Clear any existing account data
    tenantStore.setCurrentAccount(null)

    throw err // Re-throw the error to be handled by the caller
  } finally {
    loadingAccount.value = false
  }
}

const loadArticles = async () => {
  loadingArticles.value = true
  try {
    await fetchArticles({}, typeof accountSlug.value === 'string' ? accountSlug.value : undefined)
  } catch (err) {
    console.error('Failed to load articles:', err)
  } finally {
    loadingArticles.value = false
  }
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return 'Recently'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatSubscriptionDate = (dateString: string): string => {
  return new Date(dateString).getFullYear().toString()
}

const navigateToArticle = (article: ArticleSummary) => {
  if (article.slug && currentAccount.value) {
    router.push(`/${currentAccount.value.slug}/${article.slug}`)
  }
}

const retryLoad = async () => {
  accountError.value = null
  await loadAccount(accountSlug.value)
}

// Initialize on mount
onMounted(async () => {
  const slug = route.params.accountSlug as string
  if (slug) {
    try {
      await loadAccount(slug)
      await loadArticles()
    } catch (err: any) {
      accountError.value = err.message || 'Failed to load editorial'
    }
  }
})

// Watch for route changes (account switching via URL)
import { watch } from 'vue'
watch(
  () => route.params.accountSlug,
  async (newSlug, oldSlug) => {
    if (newSlug && newSlug !== oldSlug) {
      const slugString = Array.isArray(newSlug) ? newSlug[0] : newSlug
      if (slugString) {
        accountError.value = null
        try {
          await loadAccount(slugString)
          await loadArticles()
        } catch (err: any) {
          accountError.value = err.message || 'Failed to load editorial'
        }
      }
    }
  }
)
</script>
