<template>
  <!-- Billing Tab Button Component - Single Responsibility: Display individual tab button -->
  <button
    @click="$emit('click')"
    :class="[
      'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
      active
        ? 'border-blue-500 text-blue-600'
        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
    ]"
  >
    <component :is="tab.icon" class="h-4 w-4 mr-2 inline" />
    {{ tab.name }}
  </button>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Only renders a single tab button
 * - Open/Closed: Can be extended by changing icon/name, not modifying logic
 * - Interface Segregation: Minimal interface focused on tab button functionality
 * - Liskov Substitution: Can be replaced with different button implementations
 * - Dependency Inversion: Receives tab data through props (dependency injection)
 */
import { defineProps, defineEmits } from 'vue'
import type { Component } from 'vue'

// Props define the contract
interface TabData {
  id: string
  name: string
  icon: Component
}

interface Props {
  tab: TabData
  active: boolean
}

defineProps<Props>()

// Emits define external communication interface
defineEmits<{
  click: []
}>()
</script>
