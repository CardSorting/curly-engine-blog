<template>
  <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 20px 20px;"></div>
    </div>

    <div class="relative max-w-md mx-auto text-center">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-white/20 rounded-full mb-6">
        <EnvelopeIcon class="w-8 h-8 text-white" />
      </div>

      <h3 class="text-2xl md:text-3xl font-bold text-white mb-4">
        Stay in the Loop
      </h3>

      <p class="text-blue-100 mb-8 leading-relaxed">
        Get the latest stories, insights, and editorial picks delivered straight to your inbox.
        Join our community of curious minds.
      </p>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-3">
          <Input
            v-model="email"
            type="email"
            placeholder="Enter your email address"
            class="flex-1 bg-white/10 border-white/30 text-white placeholder-white/70 focus:bg-white/20"
            :disabled="submitting"
            required
          />
          <Button
            type="submit"
            variant="secondary"
            size="lg"
            :disabled="submitting"
            class="whitespace-nowrap"
          >
            <span v-if="submitting">Subscribing...</span>
            <span v-else>Subscribe</span>
          </Button>
        </div>

        <div v-if="message" class="text-sm text-center">
          <span v-if="error" class="text-red-200">{{ message }}</span>
          <span v-else class="text-green-200">{{ message }}</span>
        </div>
      </form>

      <p class="text-xs text-blue-200 mt-4">
        No spam, unsubscribe at any time. Your privacy is respected.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { EnvelopeIcon } from '@heroicons/vue/24/outline'
import Input from './Input.vue'
import Button from './Button.vue'

const email = ref('')
const submitting = ref(false)
const message = ref('')
const error = ref(false)

// Mock newsletter subscription - in real app, this would call API
const handleSubmit = async () => {
  if (!email.value) return

  submitting.value = true
  message.value = ''
  error.value = false

  try {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // For now, just show success message
    // In real implementation, you'd call the newsletter API
    message.value = 'Thanks for subscribing! Check your email to confirm.'
  } catch (err) {
    error.value = true
    message.value = 'Something went wrong. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>
