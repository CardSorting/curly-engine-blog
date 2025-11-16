<template>
  <div class="relative">
    <input
      v-if="multiline"
      :id="id"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :class="inputClasses"
      :aria-invalid="hasError"
      :aria-describedby="hasError ? `${id}-error` : undefined"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />

    <input
      v-else
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :min="min"
      :max="max"
      :step="step"
      :class="inputClasses"
      :aria-invalid="hasError"
      :aria-describedby="hasError ? `${id}-error` : undefined"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />

    <div v-if="hasError" :id="`${id}-error`" class="mt-1 text-sm text-red-600">
      {{ errorMessage }}
    </div>

    <div v-if="hint && !hasError" class="mt-1 text-sm text-gray-500">
      {{ hint }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

interface Props {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search'
  placeholder?: string
  disabled?: boolean
  readonly?: boolean
  multiline?: boolean
  rows?: number
  label?: string
  hint?: string
  errorMessage?: string
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  min?: number | string
  max?: number | string
  step?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  multiline: false,
  rows: 3,
  size: 'md',
  fullWidth: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  blur: [event: Event]
  focus: [event: Event]
}>()

const isFocused = ref(false)
const id = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`)

const hasError = computed(() => !!props.errorMessage)

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement | HTMLTextAreaElement
  const value = props.type === 'number' ? Number(target.value) : target.value
  emit('update:modelValue', value)
}

const handleBlur = (event: Event) => {
  isFocused.value = false
  emit('blur', event)
}

const handleFocus = (event: Event) => {
  isFocused.value = true
  emit('focus', event)
}

const inputClasses = computed(() => {
  const baseClasses = [
    'block border transition-colors duration-200',
    'focus:outline-none focus:ring-2 focus:ring-offset-0',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'placeholder:text-gray-400'
  ]

  // Size classes
  const sizeClasses = {
    sm: 'px-2.5 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
  }

  // State classes
  const stateClasses = hasError.value
    ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
    : isFocused.value
      ? 'border-blue-500 ring-blue-500'
      : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'

  const widthClass = props.fullWidth ? 'w-full' : ''

  const isTextarea = props.multiline ? 'resize-vertical' : 'rounded-md'

  return [
    ...baseClasses,
    sizeClasses[props.size],
    stateClasses,
    widthClass,
    isTextarea,
  ].filter(Boolean).join(' ')
})
</script>
