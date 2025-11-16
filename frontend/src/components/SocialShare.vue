<template>
  <div class="social-share">
    <h3 class="text-sm font-medium text-gray-700 mb-3">Share this article</h3>
    <div class="flex flex-wrap gap-2">
      <!-- Twitter/X -->
      <a
        :href="twitterUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center px-3 py-2 bg-black text-white rounded-md hover:bg-gray-800 transition-colors"
        title="Share on X (Twitter)"
      >
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
        <span class="text-sm">X</span>
      </a>

      <!-- Facebook -->
      <a
        :href="facebookUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        title="Share on Facebook"
      >
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
        <span class="text-sm">Facebook</span>
      </a>

      <!-- LinkedIn -->
      <a
        :href="linkedinUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="inline-flex items-center px-3 py-2 bg-blue-700 text-white rounded-md hover:bg-blue-800 transition-colors"
        title="Share on LinkedIn"
      >
        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
        </svg>
        <span class="text-sm">LinkedIn</span>
      </a>

      <!-- Email -->
      <a
        :href="emailUrl"
        class="inline-flex items-center px-3 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
        title="Share via Email"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
        <span class="text-sm">Email</span>
      </a>

      <!-- Copy Link -->
      <button
        @click="copyLink"
        class="inline-flex items-center px-3 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors"
        title="Copy link"
      >
        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
        </svg>
        <span class="text-sm">{{ copied ? 'Copied!' : 'Copy' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'

interface Props {
  title?: string
  description?: string
  url?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  description: '',
  url: ''
})

const route = useRoute()
const copied = ref(false)

// Get the full URL for sharing
const fullUrl = computed(() => {
  if (props.url) return props.url
  const baseUrl = window.location.origin
  return `${baseUrl}${route.fullPath}`
})

// Twitter/X share URL
const twitterUrl = computed(() => {
  const text = props.title || 'Check out this article'
  const url = fullUrl.value
  return `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`
})

// Facebook share URL
const facebookUrl = computed(() => {
  const url = fullUrl.value
  return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`
})

// LinkedIn share URL
const linkedinUrl = computed(() => {
  const url = fullUrl.value
  const title = props.title || 'Interesting article'
  const summary = props.description || ''
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}&summary=${encodeURIComponent(summary)}`
})

// Email share URL
const emailUrl = computed(() => {
  const subject = props.title || 'Check out this article'
  const body = props.description ? `${props.description}\n\n${fullUrl.value}` : fullUrl.value
  return `mailto:?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
})

// Copy link to clipboard
const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(fullUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy link:', err)
  }
}
</script>

<style scoped>
.social-share {
  @apply bg-gray-50 rounded-lg p-4;
}
</style>
