<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-lg w-full space-y-8">
      <AccountCreateForm />
    </div>
  </div>
</template>

<script setup lang="ts">
import AccountCreateForm from '@/components/auth/AccountCreateForm.vue'
</script>
