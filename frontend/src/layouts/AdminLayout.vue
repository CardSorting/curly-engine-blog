<template>
  <div class="min-h-screen bg-gray-50 flex">
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-gray-900 text-white transition-all duration-300 ease-in-out',
        sidebarOpen ? 'w-64' : 'w-0 lg:w-20',
        'fixed lg:relative inset-y-0 left-0 z-50 overflow-hidden'
      ]"
    >
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between h-16 px-4 bg-gray-800">
        <div v-if="sidebarOpen" class="flex items-center">
          <DocumentTextIcon class="h-8 w-8 text-blue-400" />
          <span class="ml-2 text-xl font-bold">Chronicle</span>
        </div>
        <button
          @click="toggleSidebar"
          class="p-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <Bars3Icon v-if="!sidebarOpen" class="h-6 w-6" />
          <XMarkIcon v-else class="h-6 w-6" />
        </button>
      </div>

      <!-- Navigation -->
      <nav class="mt-8 px-2">
        <div class="space-y-1">
          <template v-for="item in navigationItems" :key="item.name">
            <router-link
              v-if="!item.roles || (currentUserRole && item.roles.includes(currentUserRole))"
              :to="item.to"
              :class="[
                'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                isActiveRoute(item.to)
                  ? 'bg-gray-800 text-white border-l-4 border-blue-500'
                  : 'text-gray-300 hover:bg-gray-700 hover:text-white'
              ]"
            >
              <component
                :is="item.icon"
                :class="[
                  'mr-3 flex-shrink-0 h-6 w-6',
                  isActiveRoute(item.to) ? 'text-blue-400' : 'text-gray-400 group-hover:text-gray-300'
                ]"
              />
              <span v-if="sidebarOpen">{{ item.name }}</span>
              <span v-else class="sr-only">{{ item.name }}</span>
            </router-link>
          </template>
        </div>

        <!-- Account Section -->
        <div v-if="sidebarOpen && currentAccount" class="mt-8 pt-8 border-t border-gray-700">
          <div class="px-3 py-2">
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider">Current Account</p>
            <p class="mt-1 text-sm font-medium text-white truncate">{{ currentAccount.name }}</p>
            <p class="text-xs text-gray-400 capitalize">{{ currentUserRole }}</p>
          </div>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <!-- Mobile menu button -->
            <button
              @click="toggleSidebar"
              class="lg:hidden p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <Bars3Icon class="h-6 w-6 text-gray-600" />
            </button>

            <!-- Page Title -->
            <div class="flex-1">
              <h1 class="text-xl font-semibold text-gray-900">{{ pageTitle }}</h1>
            </div>

            <!-- Right side items -->
            <div class="flex items-center space-x-4">
              <!-- Account Switcher -->
              <div class="relative">
                <button
                  @click="accountDropdownOpen = !accountDropdownOpen"
                  class="flex items-center p-2 text-sm rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <BuildingOfficeIcon class="h-5 w-5 text-gray-600 mr-2" />
                  <span class="hidden sm:block text-gray-700">{{ currentAccount?.name || 'Select Account' }}</span>
                  <ChevronDownIcon class="h-4 w-4 text-gray-500 ml-1" />
                </button>

                <!-- Account Dropdown -->
                <div
                  v-if="accountDropdownOpen"
                  class="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50"
                >
                  <div class="py-1">
                    <template v-if="userAccounts.length > 0">
                      <button
                        v-for="account in userAccounts"
                        :key="account.id"
                        @click="switchAccount(account)"
                        :class="[
                          'w-full text-left px-4 py-2 text-sm hover:bg-gray-100',
                          currentAccount?.id === account.id ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                        ]"
                      >
                        <div class="flex items-center">
                          <BuildingOfficeIcon class="h-4 w-4 mr-2" />
                          <div>
                            <p class="font-medium">{{ account.name }}</p>
                            <p class="text-xs text-gray-500">{{ account.slug }}</p>
                          </div>
                        </div>
                      </button>
                    </template>
                    <router-link
                      v-else
                      :to="{ name: 'account-select' }"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Create or Join Account
                    </router-link>
                  </div>
                </div>
              </div>

              <!-- User Profile Dropdown -->
              <div class="relative">
                <button
                  @click="userDropdownOpen = !userDropdownOpen"
                  class="flex items-center space-x-3 p-2 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <div class="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                    <span class="text-white text-sm font-medium">
                      {{ userInitials }}
                    </span>
                  </div>
                  <ChevronDownIcon class="h-4 w-4 text-gray-500" />
                </button>

                <!-- User Dropdown -->
                <div
                  v-if="userDropdownOpen"
                  class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50"
                >
                  <div class="py-1">
                    <div class="px-4 py-2 border-b border-gray-100">
                      <p class="text-sm font-medium text-gray-900">{{ authStore.user?.username }}</p>
                      <p class="text-xs text-gray-500">{{ authStore.user?.email }}</p>
                    </div>
                    <router-link
                      :to="{ name: 'profile' }"
                      class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Profile Settings
                    </router-link>
                    <button
                      @click="handleLogout"
                      class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-auto">
        <slot />
      </main>
    </div>

    <!-- Mobile sidebar overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-gray-600 bg-opacity-75 z-40 lg:hidden"
      @click="closeSidebar"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bars3Icon,
  XMarkIcon,
  DocumentTextIcon,
  HomeIcon,
  PencilIcon,
  PhotoIcon,
  UserGroupIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  BuildingOfficeIcon,
  ChevronDownIcon,
  TagIcon,
  NewspaperIcon
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import type { Account } from '@/types/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const tenantStore = useTenantStore()

// Reactive state
const sidebarOpen = ref(false)
const accountDropdownOpen = ref(false)
const userDropdownOpen = ref(false)

// Computed properties
const currentAccount = computed(() => tenantStore.currentAccount)
const userAccounts = computed(() => tenantStore.userAccounts)
const currentUserRole = computed(() => tenantStore.currentUserRole)

const userInitials = computed(() => {
  if (!authStore.user?.username) return 'U'
  return authStore.user.username
    .split(' ')
    .map(word => word.charAt(0).toUpperCase())
    .join('')
    .slice(0, 2)
})

const pageTitle = computed(() => {
  const routeMeta = route.meta.title as string
  return routeMeta || 'Dashboard'
})

// Navigation items based on user roles
const navigationItems = computed(() => [
  {
    name: 'Dashboard',
    to: { name: 'admin-dashboard' },
    icon: HomeIcon,
    roles: [] // All roles can access
  },
  {
    name: 'Articles',
    to: { name: 'admin-articles' },
    icon: DocumentTextIcon,
    roles: ['admin', 'editor', 'author']
  },
  {
    name: 'Create Article',
    to: { name: 'admin-article-create' },
    icon: PencilIcon,
    roles: ['admin', 'editor', 'author']
  },
  {
    name: 'Media Library',
    to: { name: 'admin-media' },
    icon: PhotoIcon,
    roles: ['admin', 'editor', 'author']
  },
  {
    name: 'Topics',
    to: { name: 'admin-topics' },
    icon: TagIcon,
    roles: ['admin', 'editor']
  },
  {
    name: 'Pages',
    to: { name: 'admin-pages' },
    icon: NewspaperIcon,
    roles: ['admin', 'editor']
  },
  {
    name: 'Users',
    to: { name: 'admin-users' },
    icon: UserGroupIcon,
    roles: ['admin']
  },
  {
    name: 'Analytics',
    to: { name: 'admin-analytics' },
    icon: ChartBarIcon,
    roles: ['admin', 'editor']
  },
  {
    name: 'Settings',
    to: { name: 'admin-settings' },
    icon: Cog6ToothIcon,
    roles: ['admin']
  }
])

// Methods
const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

const isActiveRoute = (to: any) => {
  if (typeof to === 'string') {
    return route.path.startsWith(to)
  }
  return route.name === to.name
}

const switchAccount = async (account: Account) => {
  try {
    if (account.id) {
      await tenantStore.switchAccount(account.id)
      accountDropdownOpen.value = false
      
      // Redirect to dashboard for the new account
      router.push({ name: 'admin-dashboard' })
    }
  } catch (error) {
    console.error('Failed to switch account:', error)
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push({ name: 'login' })
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// Close dropdowns when clicking outside
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.relative')) {
    accountDropdownOpen.value = false
    userDropdownOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
