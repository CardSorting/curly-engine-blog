import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Account, AccountUser } from '@/types/api'
import { apiClient } from '@/services/api/config'

export const useTenantStore = defineStore('tenant', () => {
  // State
  const currentAccount = ref<Account | null>(null)
  const userAccounts = ref<Account[]>([])
  const accountUsers = ref<AccountUser[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const accountSlug = computed(() => currentAccount.value?.slug || null)
  const accountId = computed(() => currentAccount.value?.id || null)

  const currentUserRole = computed(() => {
    if (!currentAccount.value) return null
    const accountUser = accountUsers.value.find(
      au => au.account.id === currentAccount.value!.id
    )
    return accountUser?.role || null
  })

  const canManageUsers = computed(() => currentUserRole.value === 'admin')
  const canManageBilling = computed(() => currentUserRole.value === 'admin')
  const canPublishArticles = computed(() =>
    ['admin', 'editor', 'author'].includes(currentUserRole.value || '')
  )
  const canEditAllArticles = computed(() =>
    ['admin', 'editor'].includes(currentUserRole.value || '')
  )
  const canViewAnalytics = computed(() =>
    ['admin', 'editor'].includes(currentUserRole.value || '')
  )

  // Actions
  const initializeTenant = () => {
    const savedAccount = localStorage.getItem('current_account')
    if (savedAccount) {
      try {
        currentAccount.value = JSON.parse(savedAccount)
      } catch (e) {
        console.error('Failed to parse saved account:', e)
        localStorage.removeItem('current_account')
      }
    }
  }

  const setCurrentAccount = (account: Account | null) => {
    currentAccount.value = account
    if (account) {
      localStorage.setItem('current_account', JSON.stringify(account))
      apiClient.defaults.headers['X-Account-ID'] = account.id
    } else {
      localStorage.removeItem('current_account')
      delete apiClient.defaults.headers['X-Account-ID']
    }
  }

  const fetchUserAccounts = async () => {
    try {
      const response = await apiClient.get<Account[]>('/accounts/')
      userAccounts.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch accounts'
      throw err
    }
  }

  const createAccount = async (accountData: { name: string; slug?: string; description?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await apiClient.post<Account>('/accounts/', accountData)
      userAccounts.value.push(response.data)
      return response.data
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Failed to create account'
      error.value = errorMsg
      throw new Error(errorMsg)
    } finally {
      isLoading.value = false
    }
  }

  const switchAccount = (accountId: string) => {
    const account = userAccounts.value.find(acc => acc.id === accountId)
    if (account) {
      setCurrentAccount(account)
      return account
    }
    throw new Error('Account not found')
  }

  const updateAccount = async (updates: Partial<Account>) => {
    if (!currentAccount.value) throw new Error('No current account')

    try {
      const response = await apiClient.patch<Account>(
        `/accounts/${currentAccount.value.id}/`,
        updates
      )
      currentAccount.value = { ...currentAccount.value, ...response.data }
      localStorage.setItem('current_account', JSON.stringify(currentAccount.value))
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update account'
      throw err
    }
  }

  const fetchAccountUsers = async () => {
    if (!currentAccount.value) return []

    try {
      const response = await apiClient.get<AccountUser[]>(
        `/accounts/${currentAccount.value.id}/users/`
      )
      accountUsers.value = response.data
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch account users'
      throw err
    }
  }

  const inviteUser = async (invitationData: {
    email: string
    role: 'admin' | 'editor' | 'author' | 'viewer'
  }) => {
    if (!currentAccount.value) throw new Error('No current account')

    try {
      const response = await apiClient.post<AccountUser>(
        `/accounts/${currentAccount.value.id}/invite/`,
        invitationData
      )
      accountUsers.value.push(response.data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to invite user'
      throw err
    }
  }

  const updateUserRole = async (userId: string, role: 'admin' | 'editor' | 'author' | 'viewer') => {
    if (!currentAccount.value) throw new Error('No current account')

    try {
      const response = await apiClient.patch<AccountUser>(
        `/accounts/${currentAccount.value.id}/users/${userId}/`,
        { role }
      )
      const index = accountUsers.value.findIndex(au => au.user.id === userId)
      if (index !== -1) {
        accountUsers.value[index] = response.data
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update user role'
      throw err
    }
  }

  const removeUser = async (userId: string) => {
    if (!currentAccount.value) throw new Error('No current account')

    try {
      await apiClient.delete(`/accounts/${currentAccount.value.id}/users/${userId}/`)
      accountUsers.value = accountUsers.value.filter(au => au.user.id !== userId)
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to remove user'
      throw err
    }
  }

  const clearTenant = () => {
    currentAccount.value = null
    userAccounts.value = []
    accountUsers.value = []
    error.value = null
    localStorage.removeItem('current_account')
    delete apiClient.defaults.headers['X-Account-ID']
  }

  return {
    // State
    currentAccount,
    userAccounts,
    accountUsers,
    isLoading,
    error,

    // Getters
    accountSlug,
    accountId,
    currentUserRole,
    canManageUsers,
    canManageBilling,
    canPublishArticles,
    canEditAllArticles,
    canViewAnalytics,

    // Actions
    initializeTenant,
    setCurrentAccount,
    fetchUserAccounts,
    createAccount,
    switchAccount,
    updateAccount,
    fetchAccountUsers,
    inviteUser,
    updateUserRole,
    removeUser,
    clearTenant,
  }
})
