<template>
  <Card class="mx-auto max-w-md">
    <template #header>
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900">Choose Your Blog</h2>
        <p class="mt-2 text-sm text-gray-600">
          Select which blog you'd like to manage
        </p>
      </div>
    </template>

    <div v-if="loading" class="text-center py-8">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-sm text-gray-600">Loading your blogs...</p>
    </div>

    <div v-else-if="accounts.length > 0" class="space-y-4">
      <div v-for="account in accounts" :key="account.id" class="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors" @click="selectAccount(account)">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <h3 class="text-lg font-medium text-gray-900">{{ account.name }}</h3>
            <p class="text-sm text-gray-600 mt-1">{{ account.description || 'No description' }}</p>
            <p class="text-xs text-gray-500 mt-2">
              Slug: {{ account.slug }} • {{ formatPlan(account.subscription_plan) }}
            </p>
          </div>
          <div class="flex flex-col items-end space-y-2">
            <span :class="[
              'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
              getStatusBadge(account)
            ]">
              {{ getStatusText(account) }}
            </span>
            <Button variant="outline" size="sm" @click.stop="goToAdmin(account)">
              Manage
            </Button>
          </div>
        </div>
      </div>

      <div class="pt-4 border-t">
        <Button variant="secondary" full-width @click="createNewAccount">
          <PlusIcon class="w-4 h-4 mr-2" />
          Create New Blog
        </Button>
      </div>
    </div>

    <div v-else class="text-center py-8">
      <p class="text-gray-600 mb-4">You don't have any blogs yet.</p>
      <Button variant="primary" @click="createNewAccount">
        <PlusIcon class="w-4 h-4 mr-2" />
        Create Your First Blog
      </Button>
    </div>

    <template #footer>
      <div class="text-center">
        <router-link
          to="/login"
          class="text-sm text-blue-600 hover:text-blue-500"
        >
          Not you? Sign in with a different account
        </router-link>
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTenantStore } from '@/stores/tenant'
import { type Account } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Card from '@/components/ui/Card.vue'
import { Plus as PlusIcon } from 'lucide-vue-next'

const router = useRouter()
const tenantStore = useTenantStore()

const loading = ref(true)

onMounted(async () => {
  try {
    await tenantStore.fetchUserAccounts()
  } catch (error) {
    console.error('Failed to fetch accounts:', error)
  } finally {
    loading.value = false
  }
})

const selectAccount = (account: Account) => {
  tenantStore.setCurrentAccount(account)
  // Redirect to where they were going or to the dashboard
  const redirectTo = router.currentRoute.value.query.redirect as string
  router.push(redirectTo || `/${account.slug}/admin`)
}

const goToAdmin = (account: Account) => {
  tenantStore.setCurrentAccount(account)
  router.push(`/${account.slug}/admin`)
}

const createNewAccount = () => {
  router.push('/account-create')
}

const formatPlan = (plan: any) => {
  if (!plan) return 'Free Plan'
  return plan.name || 'Plan'
}

const getStatusBadge = (account: Account) => {
  switch (account.subscription_status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'trialing':
      return 'bg-blue-100 text-blue-800'
    case 'past_due':
      return 'bg-yellow-100 text-yellow-800'
    case 'canceled':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const getStatusText = (account: Account) => {
  switch (account.subscription_status) {
    case 'active':
      return 'Active'
    case 'trialing':
      return 'Trial'
    case 'past_due':
      return 'Past Due'
    case 'canceled':
      return 'Canceled'
    default:
      return 'Unknown'
  }
}

const accounts = computed(() => tenantStore.userAccounts)
</script>
