<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <LoginForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '@/components/auth/LoginForm.vue'
</script>
