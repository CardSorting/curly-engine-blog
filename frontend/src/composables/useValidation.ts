import { ref, computed } from 'vue'

// Validation rule types
type ValidationRule<T = any> = {
  validator: (value: T, ...args: any[]) => boolean
  message: string
  params?: any[]
}

type ValidationSchema = Record<string, ValidationRule[]>

// Common validation patterns
const patterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  url: /^https?:\/\/(?:[-\w.])+(?:[:\d]+)?(?:\/(?:[\w._~:/?#[\]@!$&'()*+,;=-]|%[\da-f]{2})*)?$/i,
  phone: /^\+?[\d\s\-\(\)]{10,}$/,
  slug: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
  username: /^[a-zA-Z0-9_]{3,30}$/,
}

// Common validation rules
const rules = {
  required: (value: any) => {
    if (Array.isArray(value)) return value.length > 0
    if (typeof value === 'string') return value.trim().length > 0
    if (typeof value === 'number') return !isNaN(value)
    return value != null && value !== undefined
  },

  email: (value: string) => patterns.email.test(value),

  url: (value: string) => patterns.url.test(value),

  phone: (value: string) => patterns.phone.test(value),

  minLength: (value: string | any[], min: number) => {
    if (Array.isArray(value)) return value.length >= min
    return typeof value === 'string' && value.length >= min
  },

  maxLength: (value: string | any[], max: number) => {
    if (Array.isArray(value)) return value.length <= max
    return typeof value === 'string' && value.length <= max
  },

  min: (value: number, min: number) => typeof value === 'number' && value >= min,

  max: (value: number, max: number) => typeof value === 'number' && value <= max,

  pattern: (value: string, pattern: RegExp) => pattern.test(value),

  slug: (value: string) => patterns.slug.test(value),

  username: (value: string) => patterns.username.test(value),

  confirmPassword: (value: string, confirmValue: string) => value === confirmValue,

  unique: async (value: any, list: any[], field: string = 'id') => {
    // Check if value is unique in the list
    return !list.some(item => item[field] === value)
  },
}

// Validation messages
const messages = {
  required: 'This field is required',
  email: 'Please enter a valid email address',
  url: 'Please enter a valid URL',
  phone: 'Please enter a valid phone number',
  minLength: (min: number) => `Must be at least ${min} characters`,
  maxLength: (max: number) => `Must be no more than ${max} characters`,
  min: (min: number) => `Must be at least ${min}`,
  max: (max: number) => `Must be no more than ${max}`,
  pattern: 'Invalid format',
  slug: 'Must be a valid slug (lowercase letters, numbers, and hyphens only)',
  username: 'Username must be 3-30 characters and contain only letters, numbers, and underscores',
  confirmPassword: 'Passwords do not match',
  unique: 'This value must be unique',
}

// Sanitization functions
const sanitizers = {
  trim: (value: string) => value.trim(),
  lowercase: (value: string) => value.toLowerCase(),
  uppercase: (value: string) => value.toUpperCase(),
  removeHtml: (value: string) => value.replace(/<[^>]*>/g, ''),
  removeSpecialChars: (value: string) => value.replace(/[^a-zA-Z0-9\s]/g, ''),
  normalizeSpaces: (value: string) => value.replace(/\s+/g, ' '),
  alphanumeric: (value: string) => value.replace(/[^a-zA-Z0-9]/g, ''),
}

// Validation result interface
interface ValidationResult {
  isValid: boolean
  errors: string[]
}

interface ValidationState {
  errors: Record<string, string[]>
  touched: Record<string, boolean>
  isValid: boolean
}

/**
 * Composable for form validation
 */
export function useValidation() {
  const state = ref<ValidationState>({
    errors: {},
    touched: {},
    isValid: true,
  })

  // Create a validation schema from rules
  const createSchema = (schema: Record<string, ValidationRule>): ValidationSchema => {
    const validationSchema: ValidationSchema = {}

    for (const [field, rule] of Object.entries(schema)) {
      validationSchema[field] = [rule]
    }

    return validationSchema
  }

  // Validate a field
  const validateField = (field: string, value: any, rule?: ValidationRule): ValidationResult => {
    const fieldErrors: string[] = []

    if (rule) {
      const isValid = rule.validator(value, ...(rule.params || []))
      if (!isValid) {
        fieldErrors.push(rule.message)
      }
    }

    return {
      isValid: fieldErrors.length === 0,
      errors: fieldErrors,
    }
  }

  // Validate entire form
  const validateForm = (data: Record<string, any>, schema: ValidationSchema): ValidationResult => {
    const allErrors: Record<string, string[]> = {}
    let isFormValid = true

    for (const [field, fieldRules] of Object.entries(schema)) {
      const fieldErrors: string[] = []

      for (const rule of fieldRules) {
        const result = validateField(field, data[field], rule)
        if (!result.isValid) {
          fieldErrors.push(...result.errors)
        }
      }

      if (fieldErrors.length > 0) {
        allErrors[field] = fieldErrors
        isFormValid = false
      }
    }

    // Update state
    state.value.errors = allErrors
    state.value.isValid = isFormValid

    return {
      isValid: isFormValid,
      errors: Object.values(allErrors).flat(),
    }
  }

  // Validate single field
  const validateSingleField = (field: string, value: any, fieldRules: ValidationRule[]): string[] => {
    const errors: string[] = []

    for (const rule of fieldRules) {
      const result = validateField(field, value, rule)
      errors.push(...result.errors)
    }

    state.value.errors[field] = errors
    state.value.errors = { ...state.value.errors } // Trigger reactivity

    return errors
  }

  // Mark field as touched
  const touchField = (field: string) => {
    state.value.touched[field] = true
    state.value.touched = { ...state.value.touched }
  }

  // Clear field errors
  const clearField = (field: string) => {
    if (state.value.errors[field]) {
      delete state.value.errors[field]
      state.value.errors = { ...state.value.errors }
    }
  }

  // Reset validation state
  const reset = () => {
    state.value = {
      errors: {},
      touched: {},
      isValid: true,
    }
  }

  // Sanitize input
  const sanitize = (value: any, sanitizerKeys: Array<keyof typeof sanitizers>): any => {
    let sanitized = value

    for (const key of sanitizerKeys) {
      if (typeof sanitized === 'string' && sanitizers[key]) {
        sanitized = sanitizers[key](sanitized)
      }
    }

    return sanitized
  }

  // Computed properties
  const isValid = computed(() => state.value.isValid)
  const errors = computed(() => state.value.errors)
  const touched = computed(() => state.value.touched)

  // Utility functions for creating common validation schemas
  const createLoginSchema = () => ({
    email: [
      { validator: rules.required, message: messages.required },
      { validator: rules.email, message: messages.email },
    ],
    password: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 6), message: messages.minLength(6) },
    ],
  })

  const createRegisterSchema = () => ({
    first_name: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 2), message: messages.minLength(2) },
    ],
    last_name: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 2), message: messages.minLength(2) },
    ],
    email: [
      { validator: rules.required, message: messages.required },
      { validator: rules.email, message: messages.email },
    ],
    password: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 8), message: messages.minLength(8) },
    ],
    password_confirm: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string, confirmValue: string) => rules.confirmPassword(value, confirmValue), message: messages.confirmPassword },
    ],
  })

  const createArticleSchema = () => ({
    title: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 3), message: messages.minLength(3) },
      { validator: (value: string) => rules.maxLength(value, 150), message: messages.maxLength(150) },
    ],
    slug: [
      { validator: rules.required, message: messages.required },
      { validator: rules.slug, message: messages.slug },
    ],
    excerpt: [
      { validator: (value: string) => rules.maxLength(value || '', 300), message: messages.maxLength(300) },
    ],
    content: [
      { validator: rules.required, message: messages.required },
      { validator: (value: string) => rules.minLength(value, 10), message: messages.minLength(10) },
    ],
  })

  return {
    // State
    isValid,
    errors,
    touched,

    // Methods
    validateForm,
    validateSingleField,
    touchField,
    clearField,
    reset,
    sanitize,
    createSchema,

    // Utilities
    rules,
    messages,
    patterns,
    sanitizers,

    // Pre-built schemas
    createLoginSchema,
    createRegisterSchema,
    createArticleSchema,
  }
}

// Debounced validation composable
export function useDebouncedValidation(debounceMs: number = 300) {
  const validation = useValidation()
  const debounceTimers: Record<string, number> = {}

  const debouncedValidateField = (field: string, value: any, rules: ValidationRule[]) => {
    if (debounceTimers[field]) {
      clearTimeout(debounceTimers[field])
    }

    debounceTimers[field] = setTimeout(() => {
      validation.validateSingleField(field, value, rules)
    }, debounceMs)
  }

  return {
    ...validation,
    debouncedValidateField,
  }
}

// Export types
export type { ValidationRule, ValidationSchema, ValidationResult, ValidationState }
