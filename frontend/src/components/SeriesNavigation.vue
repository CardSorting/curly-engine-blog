<template>
  <div v-if="navigation.previous || navigation.next" class="series-navigation bg-gray-50 border-t border-b py-4 mt-8">
    <div class="max-w-4xl mx-auto px-4">
      <div class="flex items-center justify-between">
        <!-- Previous Article -->
        <div v-if="navigation.previous" class="flex-1">
          <router-link
            :to="{ name: 'ArticleDetail', params: { slug: navigation.previous.slug } }"
            class="flex items-center p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow group"
          >
            <div class="mr-3 text-gray-400 group-hover:text-blue-500">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
            <div class="flex-1 text-left">
              <div class="text-xs text-gray-500 uppercase tracking-wide">Previous</div>
              <div class="text-sm font-medium text-gray-900 truncate">{{ navigation.previous.title }}</div>
              <div class="text-xs text-gray-500 truncate">{{ navigation.previous.excerpt }}</div>
            </div>
          </router-link>
        </div>

        <!-- Series Info -->
        <div class="px-6 text-center">
          <div v-if="seriesInfo" class="text-sm">
            <div class="text-gray-600">Part {{ currentPosition + 1 }} of {{ totalArticles }}</div>
            <div class="font-medium text-gray-900">{{ seriesInfo.title }}</div>
          </div>
        </div>

        <!-- Next Article -->
        <div v-if="navigation.next" class="flex-1">
          <router-link
            :to="{ name: 'ArticleDetail', params: { slug: navigation.next.slug } }"
            class="flex items-center p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow group"
          >
            <div class="flex-1 text-right">
              <div class="text-xs text-gray-500 uppercase tracking-wide">Next</div>
              <div class="text-sm font-medium text-gray-900 truncate">{{ navigation.next.title }}</div>
              <div class="text-xs text-gray-500 truncate">{{ navigation.next.excerpt }}</div>
            </div>
            <div class="ml-3 text-gray-400 group-hover:text-blue-500">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
              </svg>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Series Overview -->
      <div v-if="showSeriesOverview && seriesArticles.length > 0" class="mt-6">
        <div class="flex items-center justify-between mb-3">
          <h4 class="font-medium text-gray-900">{{ seriesInfo?.title }}</h4>
          <button
            @click="toggleSeriesOverview"
            class="text-sm text-blue-600 hover:text-blue-800"
          >
            {{ showArticlesList ? 'Hide Articles' : 'Show Articles' }}
          </button>
        </div>

        <div v-if="showArticlesList" class="bg-white rounded-lg border overflow-hidden">
          <div class="max-h-64 overflow-y-auto">
            <div
              v-for="(article, index) in seriesArticles"
              :key="article.id"
              class="border-b last:border-b-0"
              :class="{ 'bg-blue-50': index === currentPosition }"
            >
              <router-link
                :to="{ name: 'ArticleDetail', params: { slug: article.slug } }"
                class="flex items-center p-3 hover:bg-gray-50 transition-colors"
              >
                <div class="flex-shrink-0 w-8 text-center">
                  <span
                    class="inline-flex items-center justify-center w-6 h-6 text-xs font-medium rounded-full"
                    :class="index === currentPosition ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'"
                  >
                    {{ index + 1 }}
                  </span>
                </div>
                <div class="flex-1 ml-3 min-w-0">
                  <div class="text-sm font-medium text-gray-900 truncate">
                    {{ article.title }}
                  </div>
                  <div class="text-xs text-gray-500 truncate">
                    {{ article.reading_time }} min read
                  </div>
                </div>
                <div v-if="article.status === 'published'" class="ml-2">
                  <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useSeries, type SeriesArticle } from '@/composables/useSeries'

interface Props {
  articleId: string
  seriesId?: string
  seriesSlug?: string
}

interface NavigationInfo {
  previous: SeriesArticle | null | undefined
  next: SeriesArticle | null | undefined
  currentIndex: number
}

const props = defineProps<Props>()

const {
  currentSeries,
  seriesArticles,
  fetchSeriesDetails,
  getSeriesNavigation
} = useSeries()

// State
const navigation = ref<NavigationInfo>({
  previous: null,
  next: null,
  currentIndex: -1
})

const showSeriesOverview = ref(false)
const showArticlesList = ref(false)

// Computed
const seriesInfo = computed(() => currentSeries.value)

const currentPosition = computed(() => navigation.value.currentIndex)

const totalArticles = computed(() => seriesArticles.value.length)

// Watch for series changes
watch(() => props.seriesId, async (newSeriesId) => {
  if (newSeriesId) {
    await loadSeriesData(newSeriesId)
  } else {
    navigation.value = { previous: null, next: null, currentIndex: -1 }
  }
}, { immediate: true })

// Methods
const loadSeriesData = async (seriesId: string) => {
  await fetchSeriesDetails(seriesId)
  updateNavigation()
}

const updateNavigation = () => {
  if (props.articleId && currentSeries.value) {
    navigation.value = getSeriesNavigation(props.articleId)
  }
}

const toggleSeriesOverview = () => {
  showArticlesList.value = !showArticlesList.value
}

// Initialize
if (props.seriesId) {
  loadSeriesData(props.seriesId)
}
</script>

<style scoped>
.router-link-active {
  @apply bg-blue-50;
}
</style>
