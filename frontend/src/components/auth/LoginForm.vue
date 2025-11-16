<template>
  <Card class="mx-auto max-w-md">
    <template #header>
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900">Welcome Back</h2>
        <p class="mt-2 text-sm text-gray-600">
          Sign in to continue to your blog
        </p>
      </div>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">
          Email Address
        </label>
        <Input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="Enter your email"
          :error-message="errors.email"
          full-width
          class="mt-1"
          @blur="validateField('email')"
        />
      </div>

      <div>
        <label for="password" class="block text-sm font-medium text-gray-700">
          Password
        </label>
        <Input
          id="password"
          v-model="form.password"
          type="password"
          placeholder="Enter your password"
          :error-message="errors.password"
          full-width
          class="mt-1"
          @blur="validateField('password')"
        />
      </div>

      <div class="flex items-center justify-between">
        <div class="text-sm">
          <router-link
            to="/forgot-password"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Forgot password?
          </router-link>
        </div>
      </div>

      <Button
        type="submit"
        variant="primary"
        :loading="authStore.isLoading"
        full-width
        class="justify-center"
      >
        Sign In
      </Button>

      <div class="text-center">
        <p class="text-sm text-gray-600">
          Don't have an account?
          <router-link
            to="/register"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Sign up
          </router-link>
        </p>
      </div>
    </form>
  </Card>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTenantStore } from '@/stores/tenant'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const authStore = useAuthStore()
const tenantStore = useTenantStore()

const form = reactive({
  email: '',
  password: '',
})

const errors = reactive({
  email: '',
  password: '',
  general: '',
})

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validateField = (field: 'email' | 'password') => {
  if (field === 'email') {
    if (!form.email) {
      errors.email = 'Email is required'
    } else if (!validateEmail(form.email)) {
      errors.email = 'Please enter a valid email address'
    } else {
      errors.email = ''
    }
  } else if (field === 'password') {
    if (!form.password) {
      errors.password = 'Password is required'
    } else if (form.password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    } else {
      errors.password = ''
    }
  }
}

const validateForm = (): boolean => {
  validateField('email')
  validateField('password')
  return !errors.email && !errors.password
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    const user = await authStore.login({
      email: form.email,
      password: form.password,
    })

    // Redirect based on user/tenant context
    if (tenantStore.currentAccount) {
      router.push('/admin')
    } else {
      // User needs to select an account
      const accounts = await tenantStore.fetchUserAccounts()
      if (accounts && accounts.length > 0) {
        router.push('/account-select')
      } else {
        // No accounts, redirect to create account
        router.push('/account-create')
      }
    }
  } catch (error) {
    // Error is handled by the store and displayed via notification
    console.error('Login failed:', error)
  }
}
</script>
