<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <h1 class="text-2xl font-bold text-gray-900">Discover Editorials</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/login"
              class="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
            >
              Sign In
            </router-link>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Hero Section -->
      <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-8 mb-8 text-white">
        <div class="text-center">
          <h2 class="text-3xl font-bold mb-4">Find Your Voice</h2>
          <p class="text-xl opacity-90 mb-6">
            Discover amazing editorials created by writers, journalists, and creators from around the world.
          </p>
          <p class="text-lg opacity-80">
            Start your own editorial today and share your stories with the world.
          </p>
        </div>
      </div>

      <!-- Search and Filter -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search editorials..."
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
          </div>
          <select
            v-model="selectedCategory"
            class="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading editorials...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600 mb-4">{{ error }}</p>
        <Button @click="fetchAccounts" variant="primary">
          Try Again
        </Button>
      </div>

      <!-- Editorial Grid -->
      <div v-else-if="filteredAccounts.length > 0" class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="account in filteredAccounts"
          :key="account.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
          @click="visitAccount(account.slug)"
        >
          <!-- Account Header/Branding -->
          <div class="h-32 bg-gradient-to-r from-blue-500 to-purple-600 relative overflow-hidden">
            <div class="absolute inset-0 bg-black bg-opacity-20"></div>
            <div class="absolute inset-0 flex items-center justify-center">
              <h3 class="text-white text-xl font-bold text-center px-4">{{ account.name }}</h3>
            </div>
          </div>

          <!-- Account Info -->
          <div class="p-6">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-gray-500">{{ account.slug }}</span>
              <span class="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                {{ account.current_article_count }} articles
              </span>
            </div>
            <p class="text-gray-600 text-sm mb-4 line-clamp-3">
              {{ account.description || 'A curated editorial space' }}
            </p>
            <div class="flex justify-between items-center">
              <span class="text-xs text-gray-400">Recently active</span>
              <Button variant="secondary" size="sm">
                Visit Editorial
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <NewspaperIcon class="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No editorials found</h3>
        <p class="text-gray-600 mb-4">
          {{ searchQuery ? 'Try adjusting your search terms' : 'Be the first to create an editorial!' }}
        </p>
        <router-link to="/login">
          <Button variant="primary">
            Start Your Editorial
          </Button>
        </router-link>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-16">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center text-gray-600">
          <p>&copy; 2025 Chronicle. Multi-tenant editorial platform.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { NewspaperIcon } from '@heroicons/vue/24/outline'
import { apiClient } from '@/services/api/config'
import Button from '@/components/ui/Button.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const router = useRouter()

// Define public account interface for the browse view
interface PublicAccount {
  id: string
  name: string
  slug: string
  description: string
  owner_name: string
  current_article_count: number
  since: number
}

// Reactive state
const searchQuery = ref('')
const selectedCategory = ref('')
const loading = ref(true)
const error = ref<string | null>(null)
const accounts = ref<PublicAccount[]>([])

// Categories for future use
const categories = ref(['Technology', 'Lifestyle', 'Business', 'Politics', 'Health', 'Entertainment'])

// Filtered accounts based on search and filters
const filteredAccounts = computed(() => {
  let accountsList = accounts.value

  if (searchQuery.value) {
    accountsList = accountsList.filter((account: PublicAccount) =>
      account.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      account.description?.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  // Category filtering would be added here once we have topic/category data
  if (selectedCategory.value) {
    // Filter by category - placeholder for future implementation
  }

  return accountsList
})

// Methods
const visitAccount = (slug: string) => {
  router.push(`/${slug}`)
}

const fetchAccounts = async () => {
  loading.value = true
  error.value = null

  try {
    // Fetch public accounts from the API - uses search params if provided
    const params = new URLSearchParams()
    if (searchQuery.value.trim()) {
      params.append('search', searchQuery.value.trim())
    }

    const response = await apiClient.get(`/accounts/public_browse/?${params.toString()}`)
    accounts.value = response.data || []
  } catch (err: any) {
    error.value = err?.response?.data?.error || err.response?.data?.message || err.message || 'Failed to load editorials'
    console.error('Error fetching accounts:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchAccounts()
})

// Watch for search query changes and debounce the API call
let searchTimeout: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    fetchAccounts()
  }, 300) // 300ms debounce
})
</script>
