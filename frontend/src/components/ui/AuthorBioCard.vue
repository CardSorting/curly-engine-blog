<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300">
    <!-- Author Header -->
    <div class="flex items-start space-x-4 mb-4">
      <!-- Author Avatar -->
      <div class="flex-shrink-0">
        <div class="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold overflow-hidden">
          <LazyImage
            v-if="avatar"
            :src="avatar"
            :alt="name"
            class="w-full h-full object-cover rounded-full"
            loading="eager"
          />
          <span v-else>{{ name.charAt(0).toUpperCase() }}</span>
        </div>
      </div>

      <!-- Author Info -->
      <div class="flex-1 min-w-0">
        <div class="flex items-center justify-between mb-1">
          <h4 class="text-lg font-semibold text-gray-900 truncate">{{ name }}</h4>
          <!-- Social Proof (Article Count) -->
          <span v-if="articleCount" class="text-sm text-gray-500 bg-gray-50 px-2 py-1 rounded-full">
            {{ articleCount }} articles
          </span>
        </div>

        <p class="text-gray-600 text-sm mb-2">{{ role }}</p>

        <!-- Social Media Icons -->
        <div v-if="socialLinks" class="flex space-x-3">
          <a
            v-for="social in socialLinks"
            :key="social.platform"
            :href="social.url"
            target="_blank"
            rel="noopener noreferrer"
            class="text-gray-400 hover:text-gray-700 transition-colors"
            :aria-label="`${social.platform} profile`"
          >
            <component :is="getIcon(social.platform)" class="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>

    <!-- Bio -->
    <div v-if="bio" class="mb-4">
      <p class="text-gray-700 text-sm leading-relaxed line-clamp-3">{{ bio }}</p>
    </div>

    <!-- Expertise Tags -->
    <div v-if="expertise && expertise.length > 0" class="mb-4">
      <div class="flex flex-wrap gap-1">
        <span
          v-for="tag in expertise"
          :key="tag"
          class="inline-block px-2 py-1 bg-editorial-light text-editorial-primary text-xs rounded-full"
        >
          {{ tag }}
        </span>
      </div>
    </div>

    <!-- Author Stats -->
    <div v-if="showStats" class="flex items-center justify-between text-xs text-gray-500">
      <div class="flex items-center space-x-4">
        <div class="flex items-center space-x-1">
          <EyeIcon class="w-3 h-3" />
          <span>{{ totalViews?.toLocaleString() || 0 }} views</span>
        </div>
        <div class="flex items-center space-x-1">
          <HeartIcon class="w-3 h-3" />
          <span>{{ totalLikes || 0 }} likes</span>
        </div>
      </div>
      <span v-if="memberSince" class="text-gray-400">
        Member since {{ memberSince }}
      </span>
    </div>

    <!-- CTA Button -->
    <div v-if="showCta" class="mt-4 pt-4 border-t border-gray-100">
      <Button
        variant="outline"
        size="sm"
        class="w-full text-center"
        @click="viewAuthorProfile"
      >
        View Profile & Articles
      </Button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { EyeIcon, HeartIcon } from '@heroicons/vue/24/outline'
import LazyImage from './LazyImage.vue'
import Button from './Button.vue'

interface SocialLink {
  platform: 'twitter' | 'linkedin' | 'facebook' | 'instagram' | 'website'
  url: string
}

interface Props {
  name: string
  role?: string
  bio?: string
  avatar?: string
  socialLinks?: SocialLink[]
  expertise?: string[]
  articleCount?: number
  totalViews?: number
  totalLikes?: number
  memberSince?: string
  showStats?: boolean
  showCta?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  role: 'Writer',
  showStats: false,
  showCta: true,
})

const emit = defineEmits<{
  viewProfile: [authorName: string]
}>()

const getIcon = (platform: string) => {
  // In a real app, you'd import specific icons
  // For now, using placeholder icons
  switch (platform) {
    case 'twitter': return '🐦'
    case 'linkedin': return '💼'
    case 'facebook': return '📘'
    case 'instagram': return '📷'
    case 'website': return '🌐'
    default: return '🔗'
  }
}

const viewAuthorProfile = () => {
  emit('viewProfile', props.name)
}
</script>
