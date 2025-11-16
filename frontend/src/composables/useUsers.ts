import { ref, type Ref } from 'vue'
import { apiClient } from '@/services/api/config'
import { notify } from '@kyvg/vue3-notification'
import type { ApiError } from '@/types/api'

interface ApiState<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<string | null>
}

export function useApi<T>() {
  const state: ApiState<T> = {
    data: ref(null),
    loading: ref(false),
    error: ref(null),
  }

  const execute = async <P extends unknown[]>(
    apiCall: (...args: P) => Promise<{ data: T }>,
    ...args: P
  ): Promise<T | null> => {
    state.loading.value = true
    state.error.value = null

    try {
      const response = await apiCall(...args)
      state.data.value = response.data
      return response.data
    } catch (error: unknown) {
      const apiError = error as ApiError
      state.error.value = apiError.message || 'An error occurred'

      notify({
        title: 'Error',
        text: state.error.value,
        type: 'error',
      })

      throw error
    } finally {
      state.loading.value = false
    }
  }

  const reset = () => {
    state.data.value = null
    state.loading.value = false
    state.error.value = null
  }

  return {
    ...state,
    execute,
    reset,
  }
}

export function useUsers<T = unknown>() {
  const api = useApi<T>()

  const fetchUsers = (params?: Record<string, unknown>) =>
    api.execute(apiClient.get, '/users/', { params })

  const fetchAccountUsers = (params?: Record<string, unknown>) =>
    api.execute(apiClient.get, '/account/users/', { params })

  const inviteUser = (data: { email: string; role: string; first_name?: string; last_name?: string }) =>
    api.execute(apiClient.post, '/account/users/invite/', data)

  const updateUserRole = (userId: string, role: string) =>
    api.execute(apiClient.patch, `/account/users/${userId}/role/`, { role })

  const removeUser = (userId: string) =>
    api.execute(apiClient.delete, `/account/users/${userId}/`)

  const deactivateUser = (userId: string) =>
    api.execute(apiClient.patch, `/account/users/${userId}/deactivate/`)

  const activateUser = (userId: string) =>
    api.execute(apiClient.patch, `/account/users/${userId}/activate/`)

  const resendInvitation = (userId: string) =>
    api.execute(apiClient.post, `/account/users/${userId}/resend-invitation/`)

  return {
    ...api,
    fetchUsers,
    fetchAccountUsers,
    inviteUser,
    updateUserRole,
    removeUser,
    deactivateUser,
    activateUser,
    resendInvitation,
  }
}
