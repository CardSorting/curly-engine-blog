<template>
  <AdminLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">User Management</h1>
        <p class="mt-2 text-gray-600">Manage team members and permissions</p>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-blue-100 rounded-lg p-3">
              <UserGroupIcon class="h-6 w-6 text-blue-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Total Users</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.totalUsers }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-green-100 rounded-lg p-3">
              <CheckCircleIcon class="h-6 w-6 text-green-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Active Users</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.activeUsers }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-yellow-100 rounded-lg p-3">
              <ClockIcon class="h-6 w-6 text-yellow-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Pending Invites</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.pendingInvites }}</p>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0 bg-purple-100 rounded-lg p-3">
              <ShieldCheckIcon class="h-6 w-6 text-purple-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Admins</p>
              <p class="text-2xl font-bold text-gray-900">{{ stats.admins }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-6 py-4 border-b border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search users..."
                  class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <MagnifyingGlassIcon class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              </div>
              
              <select
                v-model="roleFilter"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="editor">Editor</option>
                <option value="author">Author</option>
                <option value="viewer">Viewer</option>
              </select>
              
              <select
                v-model="statusFilter"
                class="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="pending">Pending</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
            
            <Button
              @click="showInviteModal = true"
              class="bg-blue-600 hover:bg-blue-700"
            >
              <UserPlusIcon class="h-4 w-4 mr-2" />
              Invite User
            </Button>
          </div>
        </div>
        
        <!-- Users Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Joined
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Login
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="user in filteredUsers" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <img
                        v-if="user.user.avatar"
                        :src="user.user.avatar"
                        :alt="user.user.username"
                        class="h-10 w-10 rounded-full"
                      />
                      <div
                        v-else
                        class="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center"
                      >
                        <UserIcon class="h-6 w-6 text-gray-400" />
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ user.user.username }}
                      </div>
                      <div class="text-sm text-gray-500">{{ user.user.email }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <select
                    v-model="user.role"
                    @change="updateUserRole(user.id, user.role)"
                    class="text-sm border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    :disabled="!canManageUser(user)"
                  >
                    <option value="admin">Admin</option>
                    <option value="editor">Editor</option>
                    <option value="author">Author</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="getStatusClass(user)"
                    class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  >
                    {{ getStatusText(user) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(user.joined_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ user.user.last_login ? formatDate(user.user.last_login) : 'Never' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex items-center justify-end space-x-2">
                    <button
                      v-if="user.is_active && canManageUser(user)"
                      @click="deactivateUser(user.id)"
                      class="text-yellow-600 hover:text-yellow-900"
                      title="Deactivate"
                    >
                      <UserMinusIcon class="h-4 w-4" />
                    </button>
                    <button
                      v-if="!user.is_active && canManageUser(user)"
                      @click="activateUser(user.id)"
                      class="text-green-600 hover:text-green-900"
                      title="Activate"
                    >
                      <UserPlusIcon class="h-4 w-4" />
                    </button>
                    <button
                      v-if="!user.user.last_login && canManageUser(user)"
                      @click="resendInvitation(user.id)"
                      class="text-blue-600 hover:text-blue-900"
                      title="Resend Invitation"
                    >
                      <EnvelopeIcon class="h-4 w-4" />
                    </button>
                    <button
                      v-if="canManageUser(user)"
                      @click="confirmRemoveUser(user)"
                      class="text-red-600 hover:text-red-900"
                      title="Remove"
                    >
                      <TrashIcon class="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Invite User Modal -->
    <Modal
      :show="showInviteModal"
      @close="showInviteModal = false"
      title="Invite Team Member"
    >
      <form @submit.prevent="inviteNewUser" class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700">Email Address</label>
          <Input
            v-model="inviteForm.email"
            type="email"
            required
            placeholder="colleague@example.com"
            class="mt-1"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">First Name</label>
          <Input
            v-model="inviteForm.first_name"
            type="text"
            placeholder="John"
            class="mt-1"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Last Name</label>
          <Input
            v-model="inviteForm.last_name"
            type="text"
            placeholder="Doe"
            class="mt-1"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700">Role</label>
          <select
            v-model="inviteForm.role"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Select a role</option>
            <option value="admin">Admin - Full access to all features</option>
            <option value="editor">Editor - Can edit and publish content</option>
            <option value="author">Author - Can create and edit own content</option>
            <option value="viewer">Viewer - Read-only access</option>
          </select>
        </div>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button
            type="button"
            @click="showInviteModal = false"
            variant="secondary"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            :loading="usersApi.loading.value"
            class="bg-blue-600 hover:bg-blue-700"
          >
            Send Invitation
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Confirm Remove Modal -->
    <Modal
      :show="showRemoveModal"
      @close="showRemoveModal = false"
      title="Remove Team Member"
    >
      <div class="space-y-4">
        <p class="text-gray-600">
          Are you sure you want to remove <strong>{{ userToRemove?.user.username }}</strong> from the team?
        </p>
        <p class="text-sm text-red-600">
          This action cannot be undone. The user will lose access to all content and settings.
        </p>
        
        <div class="flex justify-end space-x-3 pt-4 border-t">
          <Button
            type="button"
            @click="showRemoveModal = false"
            variant="secondary"
          >
            Cancel
          </Button>
          <Button
            type="button"
            @click="removeUserById"
            :loading="usersApi.loading.value"
            class="bg-red-600 hover:bg-red-700"
          >
            Remove User
          </Button>
        </div>
      </div>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '@/components/ui/Modal.vue'
import { useUsers } from '@/composables/useUsers'
import { useAuthStore } from '@/stores/auth'
import type { AccountUser } from '@/types/api'
import {
  UserGroupIcon,
  UserPlusIcon,
  UserMinusIcon,
  UserIcon,
  CheckCircleIcon,
  ClockIcon,
  ShieldCheckIcon,
  MagnifyingGlassIcon,
  EnvelopeIcon,
  TrashIcon,
} from '@heroicons/vue/24/outline'

const authStore = useAuthStore()
const usersApi = useUsers<AccountUser[]>()

const showInviteModal = ref(false)
const showRemoveModal = ref(false)
const userToRemove = ref<AccountUser | null>(null)

const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

const inviteForm = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: '',
})

const stats = computed(() => {
  const users = usersApi.data.value || []
  return {
    totalUsers: users.length,
    activeUsers: users.filter(u => u.is_active && u.user.last_login).length,
    pendingInvites: users.filter(u => !u.user.last_login).length,
    admins: users.filter(u => u.role === 'admin').length,
  }
})

const filteredUsers = computed(() => {
  let users = usersApi.data.value || []
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    users = users.filter(user => 
      user.user.username.toLowerCase().includes(query) ||
      user.user.email.toLowerCase().includes(query)
    )
  }
  
  if (roleFilter.value) {
    users = users.filter(user => user.role === roleFilter.value)
  }
  
  if (statusFilter.value) {
    if (statusFilter.value === 'active') {
      users = users.filter(user => user.is_active && user.user.last_login)
    } else if (statusFilter.value === 'pending') {
      users = users.filter(user => !user.user.last_login)
    } else if (statusFilter.value === 'inactive') {
      users = users.filter(user => !user.is_active)
    }
  }
  
  return users
})

const canManageUser = (user: AccountUser) => {
  // Users can't manage themselves or other admins (unless they're the owner)
  const currentUser = authStore.user
  if (!currentUser || user.user.id === currentUser.id) return false
  
  // Only admins can manage other users
  if (authStore.userRole !== 'admin') return false
  
  // Admins can't remove other admins (this could be expanded based on business logic)
  if (user.role === 'admin' && user.user.id !== currentUser.id) return false
  
  return true
}

const getStatusClass = (user: AccountUser) => {
  if (!user.user.last_login) {
    return 'bg-yellow-100 text-yellow-800'
  }
  if (user.is_active) {
    return 'bg-green-100 text-green-800'
  }
  return 'bg-gray-100 text-gray-800'
}

const getStatusText = (user: AccountUser) => {
  if (!user.user.last_login) {
    return 'Pending'
  }
  if (user.is_active) {
    return 'Active'
  }
  return 'Inactive'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString()
}

const inviteNewUser = async () => {
  try {
    await usersApi.inviteUser(inviteForm.value)
    showInviteModal.value = false
    inviteForm.value = { email: '', first_name: '', last_name: '', role: '' }
    await loadUsers()
  } catch (error) {
    // Error is handled by the composable
  }
}

const updateUserRole = async (userId: string, role: string) => {
  try {
    await usersApi.updateUserRole(userId, role)
    await loadUsers()
  } catch (error) {
    // Error is handled by the composable
    // Revert the change in the UI
    await loadUsers()
  }
}

const deactivateUser = async (userId: string) => {
  try {
    await usersApi.deactivateUser(userId)
    await loadUsers()
  } catch (error) {
    // Error is handled by the composable
  }
}

const activateUser = async (userId: string) => {
  try {
    await usersApi.activateUser(userId)
    await loadUsers()
  } catch (error) {
    // Error is handled by the composable
  }
}

const resendInvitation = async (userId: string) => {
  try {
    await usersApi.resendInvitation(userId)
  } catch (error) {
    // Error is handled by the composable
  }
}

const confirmRemoveUser = (user: AccountUser) => {
  userToRemove.value = user
  showRemoveModal.value = true
}

const removeUserById = async () => {
  if (!userToRemove.value) return
  
  try {
    await usersApi.removeUser(userToRemove.value.id)
    showRemoveModal.value = false
    userToRemove.value = null
    await loadUsers()
  } catch (error) {
    // Error is handled by the composable
  }
}

const loadUsers = async () => {
  try {
    await usersApi.fetchAccountUsers()
  } catch (error) {
    // Error is handled by the composable
  }
}

onMounted(() => {
  loadUsers()
})
</script>
