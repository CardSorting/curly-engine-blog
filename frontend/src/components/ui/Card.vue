<template>
  <div :class="cardClasses" @click="handleClick">
    <div v-if="hasHeader || $slots.header" class="px-4 py-5 sm:px-6">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <slot name="header" :title="title" :subtitle="subtitle">
            <h3 v-if="title" class="text-lg leading-6 font-medium text-gray-900">
              {{ title }}
            </h3>
            <p v-if="subtitle" class="mt-1 max-w-2xl text-sm text-gray-500">
              {{ subtitle }}
            </p>
          </slot>
        </div>
        <div v-if="$slots.actions" class="flex-shrink-0">
          <slot name="actions" />
        </div>
      </div>
    </div>

    <div v-if="$slots.default || content" :class="contentClasses">
      <slot>{{ content }}</slot>
    </div>

    <div v-if="$slots.footer" class="px-4 py-3 bg-gray-50 px-4 py-3 sm:px-6 rounded-b-lg">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  subtitle?: string
  content?: string
  variant?: 'default' | 'elevated' | 'bordered' | 'ghost'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  rounded?: boolean
  hoverable?: boolean
  clickable?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
  padding: 'md',
  rounded: true,
  hoverable: false,
  clickable: false,
})

const emit = defineEmits<{
  click: [event: Event]
}>()

const hasHeader = computed(() => props.title || props.subtitle)

const handleClick = (event: Event) => {
  if (props.clickable) {
    emit('click', event)
  }
}

const cardClasses = computed(() => {
  const baseClasses = ['bg-white']

  // Variant classes
  const variantClasses = {
    default: 'shadow-sm border border-gray-200',
    elevated: 'shadow-lg border border-gray-100',
    bordered: 'border-2 border-gray-200',
    ghost: 'border-0',
  }

  // Size classes
  const sizeClasses = {
    sm: props.rounded ? 'rounded' : '',
    md: props.rounded ? 'rounded-lg' : '',
    lg: props.rounded ? 'rounded-xl' : '',
    xl: props.rounded ? 'rounded-2xl' : '',
  }

  // Interactive classes
  const interactiveClasses = props.clickable || props.hoverable
    ? 'cursor-pointer transition-transform duration-200 hover:scale-[1.02] hover:shadow-md'
    : ''

  return [
    ...baseClasses,
    variantClasses[props.variant],
    sizeClasses[props.size],
    interactiveClasses,
  ].filter(Boolean).join(' ')
})

const contentClasses = computed(() => {
  const paddingClasses = {
    none: '',
    sm: 'px-4 py-2 sm:p-6',
    md: 'px-4 py-5 sm:px-6',
    lg: 'px-6 py-6 sm:px-8',
    xl: 'px-8 py-8 sm:px-10',
  }

  return paddingClasses[props.padding]
})
</script>
