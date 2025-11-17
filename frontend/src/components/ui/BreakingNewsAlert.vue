<template>
  <div
    v-if="showAlert"
    class="relative bg-gradient-to-r from-red-600 via-orange-600 to-red-700 text-white overflow-hidden shadow-lg"
    :class="{ 'animate-pulse-subtle': urgent }"
  >
    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 20px 20px;"></div>
    </div>

    <!-- Content -->
    <div class="relative px-4 py-3 md:px-6 md:py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <div class="flex items-center space-x-3 md:space-x-4 flex-1 min-w-0">
          <!-- Breaking News Badge -->
          <div class="flex-shrink-0 flex items-center space-x-2">
            <div class="relative">
              <BoltIcon class="w-6 h-6 animate-pulse" />
              <div class="absolute -top-1 -right-1 w-2 h-2 bg-yellow-400 rounded-full animate-ping"></div>
            </div>
            <span class="font-bold text-sm md:text-base tracking-wide uppercase">
              {{ urgent ? 'BREAKING' : 'NEWS ALERT' }}
            </span>
          </div>

          <!-- Separator -->
          <div class="hidden md:block w-px h-6 bg-white/30"></div>

          <!-- News Content -->
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-sm md:text-base leading-tight line-clamp-1">
              {{ headline }}
            </h3>
            <p v-if="subheadline" class="text-xs md:text-sm text-orange-100 mt-1 line-clamp-1">
              {{ subheadline }}
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex items-center space-x-2 ml-4">
          <Button
            variant="secondary"
            size="sm"
            class="bg-white/10 hover:bg-white/20 border-white/30 text-white text-xs font-medium px-3 py-1"
            @click="readNow"
          >
            Read Now
            <ArrowRightIcon class="w-3 h-3 ml-1" />
          </Button>

          <Button
            variant="ghost"
            size="sm"
            class="text-white/70 hover:text-white hover:bg-white/10 p-1"
            @click="dismissAlert"
            :aria-label="'Dismiss ' + headline"
          >
            <XMarkIcon class="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>

    <!-- Progress Bar (only for timed alerts) -->
    <div v-if="autoDismiss && timeLeft > 0" class="h-0.5 bg-white/20">
      <div
        class="h-full bg-white transition-all ease-linear"
        :style="{ width: `${(timeLeft / 10000) * 100}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { BoltIcon, ArrowRightIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import Button from './Button.vue'
import { useRouter } from 'vue-router'
import { useTenantStore } from '@/stores/tenant'

interface Props {
  headline: string
  subheadline?: string
  articleSlug?: string
  urgent?: boolean
  autoDismiss?: boolean
  dismissDelay?: number
}

const props = withDefaults(defineProps<Props>(), {
  urgent: false,
  autoDismiss: true,
  dismissDelay: 10000, // 10 seconds
})

const emit = defineEmits<{
  dismissed: []
  clicked: [articleSlug?: string]
}>()

const router = useRouter()
const tenantStore = useTenantStore()
const showAlert = ref(true)
const timeLeft = ref(props.dismissDelay)
const dismissInterval = ref<number | null>(null)

onMounted(() => {
  if (props.autoDismiss) {
    dismissInterval.value = setInterval(() => {
      timeLeft.value -= 100
      if (timeLeft.value <= 0) {
        dismissAlert()
      }
    }, 100)
  }
})

onUnmounted(() => {
  if (dismissInterval.value) {
    clearInterval(dismissInterval.value)
  }
})

const dismissAlert = () => {
  showAlert.value = false
  if (dismissInterval.value) {
    clearInterval(dismissInterval.value)
  }
  emit('dismissed')
}

const readNow = () => {
  dismissAlert()
  if (props.articleSlug) {
    const accountSlug = tenantStore.accountSlug
    if (accountSlug && props.articleSlug) {
      router.push(`/${accountSlug}/${props.articleSlug}`)
    }
  }
  emit('clicked', props.articleSlug)
}
</script>
