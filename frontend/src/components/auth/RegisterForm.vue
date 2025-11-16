<template>
  <Card class="mx-auto max-w-md">
    <template #header>
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-900">Create Your Account</h2>
        <p class="mt-2 text-sm text-gray-600">
          Join Chronicle and start building your blog
        </p>
      </div>
    </template>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label for="firstName" class="block text-sm font-medium text-gray-700">
            First Name
          </label>
          <Input
            id="firstName"
            v-model="form.firstName"
            type="text"
            placeholder="John"
            :error-message="errors.firstName"
            full-width
            class="mt-1"
            @blur="validateField('firstName')"
          />
        </div>

        <div>
          <label for="lastName" class="block text-sm font-medium text-gray-700">
            Last Name
          </label>
          <Input
            id="lastName"
            v-model="form.lastName"
            type="text"
            placeholder="Doe"
            :error-message="errors.lastName"
            full-width
            class="mt-1"
            @blur="validateField('lastName')"
          />
        </div>
      </div>

      <div>
        <label for="email" class="block text-sm font-medium text-gray-700">
          Email Address
        </label>
        <Input
          id="email"
          v-model="form.email"
          type="email"
          placeholder="john@example.com"
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
          placeholder="Create a strong password"
          :error-message="errors.password"
          full-width
          class="mt-1"
          @blur="validateField('password')"
        />
        <div v-if="!errors.password" class="mt-1 text-xs text-gray-500">
          At least 8 characters with numbers and letters
        </div>
      </div>

      <div>
        <label for="passwordConfirm" class="block text-sm font-medium text-gray-700">
          Confirm Password
        </label>
        <Input
          id="passwordConfirm"
          v-model="form.passwordConfirm"
          type="password"
          placeholder="Confirm your password"
          :error-message="errors.passwordConfirm"
          full-width
          class="mt-1"
          @blur="validateField('passwordConfirm')"
        />
      </div>

      <div class="flex items-center">
        <input
          id="terms"
          v-model="form.acceptTerms"
          type="checkbox"
          class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label for="terms" class="ml-2 block text-sm text-gray-700">
          I agree to the
          <router-link to="/terms" class="text-blue-600 hover:text-blue-500">
            Terms of Service
          </router-link>
          and
          <router-link to="/privacy" class="text-blue-600 hover:text-blue-500">
            Privacy Policy
          </router-link>
        </label>
      </div>
      <div v-if="errors.acceptTerms" class="text-sm text-red-600">
        {{ errors.acceptTerms }}
      </div>

      <Button
        type="submit"
        variant="primary"
        :loading="authStore.isLoading"
        full-width
        size="lg"
        class="justify-center"
      >
        Create Account
      </Button>

      <div class="text-center">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link
            to="/login"
            class="font-medium text-blue-600 hover:text-blue-500"
          >
            Sign in
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
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Card from '@/components/ui/Card.vue'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  passwordConfirm: '',
  acceptTerms: false,
})

const errors = reactive({
  firstName: '',
  lastName: '',
  email: '',
  password: '',
  passwordConfirm: '',
  acceptTerms: '',
})

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const validatePassword = (password: string): boolean => {
  // At least 8 characters, one letter, one number
  const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/
  return passwordRegex.test(password)
}

const validateField = (field: keyof typeof errors) => {
  switch (field) {
    case 'firstName':
      errors.firstName = form.firstName.trim() ? '' : 'First name is required'
      break
    case 'lastName':
      errors.lastName = form.lastName.trim() ? '' : 'Last name is required'
      break
    case 'email':
      if (!form.email) {
        errors.email = 'Email is required'
      } else if (!validateEmail(form.email)) {
        errors.email = 'Please enter a valid email address'
      } else {
        errors.email = ''
      }
      break
    case 'password':
      if (!form.password) {
        errors.password = 'Password is required'
      } else if (form.password.length < 8) {
        errors.password = 'Password must be at least 8 characters'
      } else if (!validatePassword(form.password)) {
        errors.password = 'Password must contain at least one letter and one number'
      } else {
        errors.password = ''
      }
      break
    case 'passwordConfirm':
      if (!form.passwordConfirm) {
        errors.passwordConfirm = 'Please confirm your password'
      } else if (form.passwordConfirm !== form.password) {
        errors.passwordConfirm = 'Passwords do not match'
      } else {
        errors.passwordConfirm = ''
      }
      break
    case 'acceptTerms':
      errors.acceptTerms = form.acceptTerms ? '' : 'You must accept the terms and conditions'
      break
  }
}

const validateForm = (): boolean => {
  const fields: (keyof typeof errors)[] = ['firstName', 'lastName', 'email', 'password', 'passwordConfirm', 'acceptTerms']
  fields.forEach(field => validateField(field))

  return !Object.values(errors).some(error => error)
}

const handleSubmit = async () => {
  if (!validateForm()) return

  try {
    await authStore.register({
      email: form.email,
      password: form.password,
      password_confirm: form.passwordConfirm,
      first_name: form.firstName,
      last_name: form.lastName,
    })

    // Registration successful - redirect to login or auto-login
    router.push('/login?message=Account created successfully! Please sign in.')
  } catch (error: any) {
    // Handle specific registration errors
    if (error.response?.data?.email) {
      errors.email = error.response.data.email[0] || 'Email already exists'
    } else if (error.response?.data?.password) {
      errors.password = error.response.data.password[0]
    }
  }
}
</script>
