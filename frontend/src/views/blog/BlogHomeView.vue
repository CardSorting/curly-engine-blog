<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Breaking News Alert -->
    <BreakingNewsAlert
      headline="Major Tech Breakthrough Announced"
      subheadline="Revolutionary AI development changes everything"
      article-slug="ai-breakthrough-2025"
      :urgent="true"
      :dismiss-delay="15000"
      @dismissed="onAlertDismissed"
      @clicked="onAlertClicked"
    />

    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-100 sticky top-0 z-40">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-20">
          <div class="flex items-center">
            <router-link to="/" class="text-3xl font-bold text-gray-900 tracking-tight">
              {{ appName }}
            </router-link>
          </div>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <a href="#latest" class="text-gray-700 hover:text-gray-900 font-medium transition-colors">
              Latest
            </a>
            <a href="#featured" class="text-gray-700 hover:text-gray-900 font-medium transition-colors">
              Featured
            </a>

            <!-- Topics Dropdown -->
            <div class="relative group">
              <button class="flex items-center space-x-1 text-gray-700 hover:text-gray-900 font-medium transition-colors">
                <span>Topics</span>
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <div class="absolute top-full mt-2 w-48 bg-white shadow-lg rounded-lg py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                <router-link
                  v-if="accountSlug"
                  :to="`/${accountSlug}/topics/${topic.slug}`"
                  v-for="topic in (topics?.results || [])"
                  :key="topic.id"
                  class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                >
                  {{ topic.name }}
                </router-link>
              </div>
            </div>

            <ThemeToggle />
            <Button variant="ghost" size="sm" @click="goToSearch">
              <MagnifyingGlassIcon class="w-5 h-5" />
            </Button>
          </div>

          <!-- Mobile Menu Button -->
          <div class="md:hidden flex items-center space-x-4">
            <ThemeToggle />
            <Button variant="ghost" size="sm" @click="mobileMenuOpen = !mobileMenuOpen">
              <Bars3Icon v-if="!mobileMenuOpen" class="w-6 h-6" />
              <XMarkIcon v-else class="w-6 h-6" />
            </Button>
          </div>
        </div>

        <!-- Mobile Navigation -->
        <div v-if="mobileMenuOpen" class="md:hidden border-t border-gray-100 py-4">
          <div class="space-y-4">
            <a href="#latest" class="block text-gray-700 font-medium">Latest</a>
            <a href="#featured" class="block text-gray-700 font-medium">Featured</a>
            <div class="space-y-2">
              <p class="text-sm font-semibold text-gray-900">Topics</p>
              <router-link
                v-if="accountSlug"
                :to="`/${accountSlug}/topics/${topic.slug}`"
                v-for="topic in (topics?.results || [])"
                :key="topic.id"
                class="block px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md"
              >
                {{ topic.name }}
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Reading Progress -->
    <ReadingProgress
      show-progress
      show-stats
      show-bookmarks
      @bookmark="handleBookmark"
      @progress-update="handleProgressUpdate"
    />

    <!-- Hero Article -->
    <section v-if="heroArticle" class="bg-gray-900 font-serif">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <HeroCard
          :article="heroArticle"
          @click="navigateToArticle"
        />
      </div>
    </section>

    <!-- Breaking/Featured Section -->
    <section v-if="featuredArticles.length > 0" class="bg-white py-16 border-b border-gray-100" id="featured">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Featured Stories</h2>
            <p class="text-lg text-gray-600">Curated pieces that deserve your attention</p>
          </div>
          <div class="hidden md:flex items-center space-x-4">
            <Button variant="outline" @click="showAllArticles">
              View All
              <ArrowRightIcon class="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>

        <div class="grid gap-8 lg:grid-cols-2">
          <FeaturedCard
            v-for="article in featuredArticles"
            :key="article.id"
            :article="article"
            @click="navigateToArticle"
          />
        </div>
      </div>
    </section>

    <!-- Latest Articles Section with Sidebar -->
    <section class="bg-gray-50 py-16" id="latest">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between mb-12">
          <div>
            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">Latest Articles</h2>
            <p class="text-lg text-gray-600">Fresh perspectives and compelling narratives</p>
          </div>
        </div>

        <!-- Main Content + Sidebar Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Main Content Area -->
          <div class="lg:col-span-2">
            <!-- Loading State -->
            <div v-if="loading" class="flex justify-center py-16">
              <div class="space-y-4">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                <p class="text-gray-600 text-center">Loading exceptional content...</p>
              </div>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="text-center py-16">
              <div class="space-y-4">
                <ExclamationTriangleIcon class="w-16 h-16 text-red-500 mx-auto" />
                <h3 class="text-xl font-semibold text-gray-900">Something went wrong</h3>
                <p class="text-gray-600">{{ error }}</p>
                <Button @click="() => loadArticles()">
                  Try Again
                </Button>
              </div>
            </div>

            <!-- Articles Grid -->
            <div v-else-if="regularArticles.length > 0" class="grid gap-8 md:grid-cols-2">
              <ArticleCard
                v-for="article in regularArticles"
                :key="article.id"
                :article="article"
                @click="navigateToArticle"
              />
            </div>

            <!-- Empty State -->
            <div v-else class="text-center py-16">
              <div class="space-y-4">
                <DocumentTextIcon class="w-16 h-16 text-gray-400 mx-auto" />
                <h3 class="text-xl font-semibold text-gray-900">No articles published yet</h3>
                <p class="text-gray-600 max-w-md mx-auto">
                  We're working on creating amazing content. Check back soon for compelling stories and insights.
                </p>
                <router-link to="/login">
                  <Button>
                    Sign in to contribute
                  </Button>
                </router-link>
              </div>
            </div>

            <!-- Load More Button -->
            <div v-if="hasMoreArticles" class="text-center mt-12">
              <Button variant="outline" size="lg" @click="loadMoreArticles" :disabled="loading">
                Load More Stories
              </Button>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="space-y-8">
            <!-- Trending Articles -->
            <TrendingArticles
              :articles="trendingArticles"
              @navigate-to-article="navigateToArticle"
              @view-all-trending="viewAllTrending"
            />

            <!-- Featured Author -->
            <div v-if="featuredAuthor">
              <div class="mb-4">
                <h3 class="text-lg font-semibold text-gray-900">Featured Author</h3>
              </div>
              <AuthorBioCard
                :name="featuredAuthor.name"
                :role="featuredAuthor.role"
                :bio="featuredAuthor.bio"
                :social-links="featuredAuthor.socialLinks"
                :expertise="featuredAuthor.expertise"
                :article-count="featuredAuthor.articleCount"
                :show-stats="true"
                @view-profile="viewAuthorProfile"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Newsletter Signup -->
    <section class="bg-white py-16 border-t border-gray-100">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="max-w-2xl mx-auto">
          <NewsletterSignup />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white py-12 border-t border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid gap-8 md:grid-cols-4">
          <div class="md:col-span-2">
            <h3 class="text-2xl font-bold mb-4">{{ appName }}</h3>
            <p class="text-gray-400 mb-6 max-w-md">
              A modern multi-tenant blog platform dedicated to fostering thoughtful dialogue and sharing compelling stories.
            </p>
            <div class="flex space-x-4">
              <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white">
                <NewspaperIcon class="w-5 h-5" />
              </Button>
              <Button variant="ghost" size="sm" class="text-gray-400 hover:text-white">
                <EnvelopeIcon class="w-5 h-5" />
              </Button>
            </div>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Navigation</h4>
            <ul class="space-y-2 text-gray-400">
              <li><a href="#latest" class="hover:text-white transition-colors">Latest Articles</a></li>
              <li><a href="#featured" class="hover:text-white transition-colors">Featured Stories</a></li>
              <li><router-link v-if="accountSlug" :to="`/${accountSlug}`" class="hover:text-white transition-colors">All Topics</router-link></li>
            </ul>
          </div>

          <div>
            <h4 class="font-semibold mb-4">Topics</h4>
            <ul class="space-y-2 text-gray-400">
              <li v-for="topic in topics?.results?.slice(0, 5)" :key="topic.id">
                <router-link
                  v-if="accountSlug"
                  :to="`/${accountSlug}/topics/${topic.slug}`"
                  class="hover:text-white transition-colors"
                >
                  {{ topic.name }}
                </router-link>
              </li>
            </ul>
          </div>
        </div>

        <div class="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 {{ appName }}. Crafted for the curious mind.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  ChevronDownIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  XMarkIcon,
  ArrowRightIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  NewspaperIcon,
  EnvelopeIcon
} from '@heroicons/vue/24/outline'
import { useArticles, useTopics } from '@/composables/useApi'
import { useTenantStore } from '@/stores/tenant'
import type { Topic, PaginatedResponse, TopicResponse, Article } from '@/types/api'

import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'
import HeroCard from '@/components/ui/HeroCard.vue'
import FeaturedCard from '@/components/ui/FeaturedCard.vue'
import ArticleCard from '@/components/ui/ArticleCard.vue'
import NewsletterSignup from '@/components/ui/NewsletterSignup.vue'
import ReadingProgress from '@/components/ui/ReadingProgress.vue'
import TrendingArticles from '@/components/ui/TrendingArticles.vue'
import AuthorBioCard from '@/components/ui/AuthorBioCard.vue'
import BreakingNewsAlert from '@/components/ui/BreakingNewsAlert.vue'

const router = useRouter()
const tenantStore = useTenantStore()
const { data: articles, loading, error, fetchArticles } = useArticles()
const { data: topics, fetchTopics } = useTopics() as any

const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')
const selectedTopic = ref('')
const mobileMenuOpen = ref(false)
const accountSlug = computed(() => tenantStore.accountSlug)

// Mock data logic - in real app, you'd have different article categories
const heroArticle = computed(() => articles.value?.results?.[0] || null)

const featuredArticles = computed(() => {
  const allArticles = articles.value?.results || []
  return allArticles.slice(1, 3) // Take the next 2 articles as featured
})

const regularArticles = computed(() => {
  const allArticles = articles.value?.results || []
  return allArticles.slice(3) // Remaining articles
})

const hasMoreArticles = computed(() => {
  // In a real app, you'd check pagination info
  return false
})

// Computed properties for sidebar content
const trendingArticles = computed(() => {
  const allArticles = articles.value?.results || []
  return allArticles.sort((a, b) => {
    // Simulate trending based on various factors
    const aScore = Math.random() + (allArticles.indexOf(a) * 0.1)
    const bScore = Math.random() + (allArticles.indexOf(b) * 0.1)
    return bScore - aScore
  })
})

const featuredAuthor = computed(() => {
  // Mock featured author data
  const allArticles = articles.value?.results || []
  if (allArticles.length === 0) return null

  // Use the author from the first article as featured
  const author = allArticles[0]?.author
  if (!author) return null

  return {
    name: author.username || 'Anonymous Author',
    role: 'Senior Writer',
    bio: 'Award-winning journalist covering technology, culture, and the intersection of innovation with society. Published in major outlets worldwide.',
    socialLinks: [
      { platform: 'twitter' as const, url: 'https://twitter.com/author' },
      { platform: 'linkedin' as const, url: 'https://linkedin.com/in/author' }
    ],
    expertise: ['Technology', 'Innovation', 'Culture', 'Digital Media'],
    articleCount: Math.floor(Math.random() * 50) + 10,
    totalViews: Math.floor(Math.random() * 50000) + 10000,
    totalLikes: Math.floor(Math.random() * 1000) + 200,
    memberSince: '2020'
  }
})

onMounted(async () => {
  await Promise.all([
    loadTopics(),
    loadArticles()
  ])
})

const loadArticles = async (params?: Record<string, unknown>) => {
  await fetchArticles(params, tenantStore.accountSlug || undefined)
}

const loadTopics = async () => {
  const response = await fetchTopics({}, tenantStore.accountSlug || undefined)
  if (response && response.results) {
    topics.value = response
  }
}

const loadMoreArticles = async () => {
  // In real implementation, load next page
  await loadArticles({ page: 2 })
}

const showAllArticles = () => {
  // Navigate to a "all articles" page
  if (accountSlug.value) {
    router.push(`/${accountSlug.value}`)
  }
}

const goToSearch = () => {
  router.push('/search')
}

const onTopicChange = () => {
  if (selectedTopic.value) {
    // For topic filtering, we'll redirect to topic page with account context
    if (accountSlug.value) {
      router.push(`/${accountSlug.value}/topics/${selectedTopic.value}`)
    } else {
      router.push('/login')
    }
  } else {
    // Load all articles
    loadArticles()
  }
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const navigateToArticle = (article: Article) => {
  // Navigate to article detail page with proper tenant routing
  if (accountSlug.value && article.slug) {
    router.push(`/${accountSlug.value}/${article.slug}`)
  } else {
    // If no account context, try to find first available account or show error
    router.push('/login')
  }
}

const handleBookmark = (position: number) => {
  // In a real app, save bookmark position to user's profile
  console.log('Bookmarked position:', position)
}

const handleProgressUpdate = (progress: number) => {
  // Track reading analytics
  console.log('Reading progress:', progress)
}

const viewAllTrending = () => {
  // Navigate to trending articles page
  console.log('View all trending articles')
}

const viewAuthorProfile = (authorName: string) => {
  // Navigate to author profile page
  console.log('View author profile:', authorName)
}

const onAlertDismissed = () => {
  console.log('Breaking news alert dismissed')
}

const onAlertClicked = (articleSlug?: string) => {
  if (articleSlug) {
    const accountSlug_value = tenantStore.accountSlug
    if (accountSlug_value && articleSlug) {
      router.push(`/${accountSlug_value}/${articleSlug}`)
    }
  }
  console.log('Breaking news alert clicked:', articleSlug)
}
</script>
