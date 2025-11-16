<template>
  <AdminLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
        <p class="mt-2 text-gray-600">Configure your blog settings</p>
      </div>

      <!-- Coming Soon Placeholder -->
      <div class="bg-white shadow rounded-lg p-8 text-center">
        <Cog6ToothIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">Blog Settings</h3>
        <p class="mt-1 text-sm text-gray-500">Settings panel is coming soon.</p>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
import { Cog6ToothIcon } from '@heroicons/vue/24/outline'
</script>
