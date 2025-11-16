<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { usePages } from '@/composables/useApi'
import { type Page } from '@/types/api'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const { fetchPage } = usePages()
const appName = ref(import.meta.env.VITE_APP_NAME || 'Chronicle')

const page = ref<Page | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  const slug = route.params.slug as string
  try {
    const response = await fetchPage(slug)
    page.value = response
  } catch (err) {
    error.value = 'Page not found'
    console.error('Failed to load page:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b">
      <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <router-link to="/" class="text-xl font-bold text-gray-900">
              {{ appName }}
            </router-link>
          </div>
          <div class="flex items-center">
            <ThemeToggle />
          </div>
        </div>
      </div>
    </nav>
    
    <div v-if="loading" class="flex justify-center items-center min-h-[400px]">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
    
    <div v-else-if="error" class="max-w-4xl mx-auto px-4 py-16 text-center">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">Page Not Found</h1>
      <p class="text-gray-600 mb-8">{{ error }}</p>
      <router-link 
        to="/blog" 
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
      >
        Back to Blog
      </router-link>
    </div>
    
    <article v-else-if="page" class="max-w-4xl mx-auto px-4 py-12">
      <header class="mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ page.title }}</h1>
        <p v-if="page.meta_description" class="text-lg text-gray-600">{{ page.meta_description }}</p>
      </header>
      
      <div class="prose prose-lg max-w-none">
        <div v-html="page.content"></div>
      </div>
    </article>
  </div>
</template>