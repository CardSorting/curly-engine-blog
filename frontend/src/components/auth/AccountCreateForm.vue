<template>
  <Card class="mx-auto max-w-md">
    <template #header>
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900">Create Your Blog</h2>
        <p class="mt-2 text-sm text-gray-600">
          Set up your first blog account to get started
        </p>
      </div>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div>
        <label for="accountName" class="block text-sm font-medium text-gray-700">
          Blog Name
        </label>
        <Input
          id="accountName"
          v-model="form.name"
          type="text"
          placeholder="My Amazing Blog"
          :error-message="errors.name"
          full-width
          class="mt-1"
          @blur="validateField('name')"
        />
        <div v-if="!errors.name" class="mt-1 text-xs text-gray-500">
          Your blog's display name
        </div>
      </div>

      <div>
        <label for="accountSlug" class="block text-sm font-medium text-gray-700">
          Blog URL Slug
        </label>
        <div class="mt-1 relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span class="text-gray-500 text-sm">chronicle.com/</span>
          </div>
          <Input
            id="accountSlug"
            v-model="form.slug"
            type="text"
            placeholder="my-amazing-blog"
            :error-message="errors.slug"
            full-width
            class="pl-32"
            @blur="validateField('slug')"
            @input="slugify"
          />
        </div>
        <div v-if="!errors.slug" class="mt-1 text-xs text-gray-500">
          Lowercase letters, numbers, and hyphens only
        </div>
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-gray-700">
          Description
        </label>
        <Input
          id="description"
          v-model="form.description"
          type="text"
          placeholder="A blog about..."
          :error-message="errors.description"
          multiline
          :rows="3"
          full-width
          class="mt-1"
        />
        <div v-if="!errors.description" class="mt-1 text-xs text-gray-500">
          Brief description of your blog (optional)
        </div>
      </div>

      <!-- Subscription Plan Selection (if available) -->
      <div v-if="subscriptionPlans.length > 0" class="space-y-3">
        <label class="block text-sm font-medium text-gray-700">
          Choose Your Plan
        </label>
        <div class="space-y-2">
          <div
            v-for="plan in subscriptionPlans"
            :key="plan.id"
            :class="[
              'border rounded-lg p-3 cursor-pointer transition-colors',
              selectedPlan === plan.id
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-200 hover:border-gray-300'
            ]"
            @click="selectedPlan = plan.id"
          >
            <div class="flex items-center justify-between">
              <div>
                <h4 class="font-medium text-gray-900">{{ plan.name }}</h4>
                <p class="text-sm text-gray-600">{{ plan.description }}</p>
                <p class="text-lg font-semibold text-blue-600 mt-1">
                  ${{ plan.monthly_price }}/month
                </p>
              </div>
              <div class="flex items-center">
                <input
                  :checked="selectedPlan === plan.id"
                  type="radio"
                  :value="plan.id"
                  class="text-blue-600 focus:ring-blue-500"
                  @change="selectedPlan = plan.id"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        :loading="tenantStore.isLoading"
        full-width
        size="lg"
        class="justify-center"
      >
        Create Blog
      </Button>

      <div class="text-center">
        <p class="text-sm text-gray-600">
          Have an existing blog?
          <router-link
            to="/account-select"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Switch accounts
          </router-link>
        </p>
      </div>
    </form>
  </Card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTenantStore } from '@/stores/tenant'
import { apiClient } from '@/services/api/config'
import { type SubscriptionPlan } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const tenantStore = useTenantStore()

const subscriptionPlans = ref<SubscriptionPlan[]>([])
const selectedPlan = ref<string>('')

const form = reactive({
  name: '',
  slug: '',
  description: '',
})

const errors = reactive({
  name: '',
  slug: '',
  description: '',
})

onMounted(async () => {
  try {
    // Load subscription plans from the backend
    const response = await apiClient.get('/accounts/subscription-plans/')
    subscriptionPlans.value = response.data || []

    // Select the first (free) plan by default
    if (subscriptionPlans.value.length > 0) {
      selectedPlan.value = subscriptionPlans.value[0]?.id || ''
    }
  } catch (error) {
    console.error('Failed to load subscription plans:', error)
    // Fallback to basic plans if API fails (during development)
    subscriptionPlans.value = [
      {
        id: 'free',
        name: 'Free',
        slug: 'free',
        description: 'Perfect for getting started',
        monthly_price: 0,
        yearly_price: 0,
        max_users: 1,
        max_articles: 10,
        max_storage_mb: 100,
        features: {},
        stripe_price_id_monthly: '',
        stripe_price_id_yearly: '',
        is_active: true,
      },
      {
        id: 'pro',
        name: 'Pro',
        slug: 'pro',
        description: 'For growing blogs',
        monthly_price: 9.99,
        yearly_price: 99.99,
        max_users: 5,
        max_articles: 1000,
        max_storage_mb: 1000,
        features: {},
        stripe_price_id_monthly: 'price_pro_monthly',
        stripe_price_id_yearly: 'price_pro_yearly',
        is_active: true,
      },
    ]
    selectedPlan.value = 'free'
  }
})

const validateSlug = (slug: string): boolean => {
  const slugRegex = /^[a-z0-9-]+(?:-[a-z0-9-]+)*$/
  return slugRegex.test(slug)
}

const slugify = () => {
  if (!form.name.trim()) return

  let slug = form.name.toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
    .replace(/^-+|-+$/g, '') // Remove leading/trailing hyphens

  form.slug = slug
}

const validateField = (field: keyof typeof errors) => {
  switch (field) {
    case 'name':
      if (!form.name.trim()) {
        errors.name = 'Blog name is required'
      } else if (form.name.trim().length < 3) {
        errors.name = 'Blog name must be at least 3 characters'
      } else {
        errors.name = ''
      }
      break
    case 'slug':
      if (!form.slug) {
        errors.slug = 'URL slug is required'
      } else if (!validateSlug(form.slug)) {
        errors.slug = 'Invalid slug format. Use lowercase letters, numbers, and hyphens only'
      } else {
        errors.slug = ''
      }
      break
    case 'description':
      // Optional field, no validation needed
      errors.description = ''
      break
  }
}

const validateForm = (): boolean => {
  const fields: (keyof typeof errors)[] = ['name', 'slug', 'description']
  fields.forEach(field => validateField(field))

  return !Object.values(errors).some(error => error)
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    const account = await tenantStore.createAccount({
      name: form.name.trim(),
      slug: form.slug,
      description: form.description.trim(),
    })

    // Account created successfully - redirect to admin dashboard
    router.push(`/${account.slug}/admin`)
  } catch (error: any) {
    // Handle specific account creation errors
    if (error.response?.data?.slug) {
      errors.slug = error.response.data.slug[0] || 'This slug is already taken'
    } else if (error.response?.data?.name) {
      errors.name = error.response.data.name[0]
    }
  }
}
</script>
