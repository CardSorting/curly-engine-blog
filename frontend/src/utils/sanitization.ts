/**
 * Input sanitization utilities for security and data integrity
 * Provides comprehensive sanitization for different input types
 */

interface SanitizationOptions {
  trim?: boolean
  lowercase?: boolean
  uppercase?: boolean
  removeHtml?: boolean
  removeSpecialChars?: boolean
  normalizeSpaces?: boolean
  alphanumeric?: boolean
  alpha?: boolean
  numeric?: boolean
  maxLength?: number
  allowedChars?: string
  allowHtml?: string[]
}

// HTML entity mapping for safe display
const htmlEntities: Record<string, string> = {
  '&': '&',
  '<': '<',
  '>': '>',
  '"': '"',
  "'": '&#x27;',
  '/': '&#x2F;',
  '`': '&#x60;',
  '=': '&#x3D;',
}

// Reverse entity mapping
const htmlEntitiesReverse: Record<string, string> = {
  '&': '&',
  '<': '<',
  '>': '>',
  '"': '"',
  '&#x27;': "'",
  '&#x2F;': '/',
  '&#x60;': '`',
  '&#x3D;': '=',
}

// Common patterns
const patterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  url: /^https?:\/\/(?:[-\w.])+(?:[:\d]+)?(?:\/(?:[\w._~:/?#[\]@!$&'()*+,;=-]|%[\da-f]{2})*)?$/i,
  phone: /^\+?[\d\s\-\(\)]{10,}$/,
  slug: /^[a-z0-9]+(?:-[a-z0-9]+)*$/,
  username: /^[a-zA-Z0-9_]{3,30}$/,
  sqlInjection: /(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b|\bDROP\b|\bCREATE\b|\bALTER\b|\bEXEC\b|\bEXECUTE\b).*?(\bor\b|\band\b).*?(\d+\s*=\s*\d+)/i,
  xss: /<script[^>]*>.*?<\/script>|<iframe[^>]*>.*?<\/iframe>|<object[^>]*>.*?<\/object>/gi,
  pathTraversal: /\.\.[\/\\]/,
}

/**
 * Core sanitization function with multiple options
 */
export function sanitize(input: string, options: SanitizationOptions = {}): string {
  if (typeof input !== 'string') {
    return ''
  }

  let sanitized = input

  // Trim whitespace
  if (options.trim !== false) {
    sanitized = sanitized.trim()
  }

  // Case conversions
  if (options.lowercase) {
    sanitized = sanitized.toLowerCase()
  }
  if (options.uppercase) {
    sanitized = sanitized.toUpperCase()
  }

  // Character filtering
  if (options.alphanumeric) {
    sanitized = sanitized.replace(/[^a-zA-Z0-9]/g, '')
  }
  if (options.alpha) {
    sanitized = sanitized.replace(/[^a-zA-Z]/g, '')
  }
  if (options.numeric) {
    sanitized = sanitized.replace(/[^0-9]/g, '')
  }
  if (options.allowedChars) {
    const escapedChars = options.allowedChars.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const pattern = new RegExp(`[^a-zA-Z0-9${escapedChars}]`, 'g')
    sanitized = sanitized.replace(pattern, '')
  }

  // HTML removal/sanitization
  if (options.removeHtml) {
    sanitized = removeHtml(sanitized)
  } else if (options.allowHtml && options.allowHtml.length > 0) {
    sanitized = sanitizeHtml(sanitized, options.allowHtml)
  }

  // Special character removal
  if (options.removeSpecialChars) {
    sanitized = sanitized.replace(/[^a-zA-Z0-9\s]/g, '')
  }

  // Space normalization
  if (options.normalizeSpaces) {
    sanitized = sanitized.replace(/\s+/g, ' ')
  }

  // Length limiting
  if (options.maxLength && sanitized.length > options.maxLength) {
    sanitized = sanitized.substring(0, options.maxLength)
  }

  return sanitized
}

/**
 * Remove all HTML tags and entities
 */
export function removeHtml(input: string): string {
  return input
    .replace(/<[^>]*>/g, '')
    .replace(/&[a-zA-Z0-9#]+;/g, (entity) => {
      return htmlEntitiesReverse[entity] || entity
    })
}

/**
 * Sanitize HTML while allowing specific tags
 */
export function sanitizeHtml(input: string, allowedTags: string[] = []): string {
  // First, remove script and other dangerous tags
  let sanitized = input.replace(/<(script|iframe|object|embed|form|input|button)[^>]*>.*?<\/\1>/gi, '')
  sanitized = sanitized.replace(/<(script|iframe|object|embed|form|input|button)[^>]*\/?>/gi, '')

  // If no tags are allowed, remove all
  if (allowedTags.length === 0) {
    sanitized = removeHtml(sanitized)
  } else {
    // Remove all tags except allowed ones
    const allowedTagsPattern = new RegExp(`<(?!${allowedTags.join('|')})[^>]*>`, 'gi')
    sanitized = sanitized.replace(allowedTagsPattern, '')

    // Remove attributes from allowed tags (basic version)
    allowedTags.forEach(tag => {
      const tagPattern = new RegExp(`<${tag}[^>]*>`, 'gi')
      sanitized = sanitized.replace(tagPattern, `<${tag}>`)
    })
  }

  return sanitized
}

/**
 * Escape HTML entities for safe display
 */
export function escapeHtml(input: string): string {
  return input.replace(/[&<>"'`=/]/g, (char) => htmlEntities[char] || char)
}

/**
 * Unescape HTML entities
 */
export function unescapeHtml(input: string): string {
  return input.replace(/&[a-zA-Z0-9#]+;/g, (entity) => {
    return htmlEntitiesReverse[entity] ?? entity
  })
}

/**
 * Sanitize SQL-like inputs to prevent injection
 */
export function sanitizeSQL(input: string): string {
  return input
    .replace(/'/g, "''")  // Escape single quotes
    .replace(/;/g, '')    // Remove semicolons
    .replace(/--/g, '')   // Remove SQL comments
    .replace(/\/\*.*?\*\//g, '') // Remove /* */ comments
}

/**
 * Sanitize filename for safe filesystem operations
 */
export function sanitizeFilename(filename: string): string {
  return filename
    .replace(/[<>:"/\\|?*]/g, '') // Remove invalid characters
    .replace(/^\.+/, '') // Remove leading dots
    .replace(/\.+$/, '') // Remove trailing dots
    .replace(/\s+/g, '_') // Replace spaces with underscores
    .substring(0, 255) // Limit length
}

/**
 * Validate input against common patterns
 */
export function validateInput(input: string, type: keyof typeof patterns): boolean {
  if (!input || typeof input !== 'string') return false
  return patterns[type].test(input)
}

/**
 * Scan for common security threats
 */
export function securityScan(input: string): {
  hasSQLInjection: boolean
  hasXSS: boolean
  hasPathTraversal: boolean
  threats: string[]
} {
  const threats: string[] = []

  if (patterns.sqlInjection.test(input)) {
    threats.push('SQL Injection')
  }

  if (patterns.xss.test(input)) {
    threats.push('XSS')
  }

  if (patterns.pathTraversal.test(input)) {
    threats.push('Path Traversal')
  }

  return {
    hasSQLInjection: threats.includes('SQL Injection'),
    hasXSS: threats.includes('XSS'),
    hasPathTraversal: threats.includes('Path Traversal'),
    threats,
  }
}

/**
 * Comprehensive input sanitization with security checks
 */
export function secureSanitize(
  input: string,
  options: SanitizationOptions & {
    securityCheck?: boolean
    throwOnThreat?: boolean
  } = {}
): string {
  // Security check first
  if (options.securityCheck !== false) {
    const scan = securityScan(input)
    if (scan.threats.length > 0 && options.throwOnThreat) {
      throw new Error(`Security threat detected: ${scan.threats.join(', ')}`)
    }
  }

  return sanitize(input, options)
}

/**
 * Pre-configured sanitizers for common use cases
 */
export const sanitizers = {
  // General text
  text: (input: string) => sanitize(input, {
    trim: true,
    removeHtml: true,
    normalizeSpaces: true,
    maxLength: 10000
  }),

  // User input for forms
  form: (input: string) => secureSanitize(input, {
    trim: true,
    removeHtml: true,
    normalizeSpaces: true,
    maxLength: 5000,
    securityCheck: true,
  }),

  // Search queries
  search: (input: string) => sanitize(input, {
    trim: true,
    removeHtml: true,
    normalizeSpaces: true,
    maxLength: 100,
  }),

  // Email input
  email: (input: string) => sanitize(input, {
    trim: true,
    lowercase: true,
    maxLength: 254
  }),

  // Username input
  username: (input: string) => sanitize(input, {
    trim: true,
    lowercase: true,
    alphanumeric: false, // Allow underscores
    allowedChars: '_',
    maxLength: 30
  }),

  // Slug input
  slug: (input: string) => sanitize(input, {
    trim: true,
    lowercase: true,
    allowedChars: '-',
    maxLength: 100
  }),

  // URL input
  url: (input: string) => sanitize(input, {
    trim: true,
    maxLength: 2000
  }),

  // Numeric input
  number: (input: string) => sanitize(input, {
    numeric: true,
    maxLength: 20
  }),

  // File path
  path: (input: string) => sanitize(input, {
    trim: true,
    removeHtml: true,
    // Don't remove dots and slashes for paths
    maxLength: 1024
  }),

  // Database queries (additional SQL sanitization)
  database: (input: string) => {
    const basic = sanitize(input, {
      trim: true,
      removeHtml: true,
      maxLength: 1000
    })
    return sanitizeSQL(basic)
  },

  // HTML content (limited tags allowed)
  html: (input: string) => sanitize(input, {
    allowHtml: ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li'],
    maxLength: 50000
  }),

  // Raw HTML removal
  noHtml: (input: string) => removeHtml(input),

  // Filename
  filename: (input: string) => sanitizeFilename(input),
}

/**
 * Validators that combine sanitization with validation
 */
export const validators = {
  email: (value: string) => {
    const sanitized = sanitizers.email(value)
    return patterns.email.test(sanitized)
  },

  url: (value: string) => {
    const sanitized = sanitizers.url(value)
    return patterns.url.test(sanitized)
  },

  phone: (value: string) => {
    const sanitized = sanitize(value, { numeric: false, allowedChars: '+()- ' })
    return patterns.phone.test(sanitized)
  },

  slug: (value: string) => {
    const sanitized = sanitizers.slug(value)
    return patterns.slug.test(sanitized) && sanitized.length > 0
  },

  username: (value: string) => {
    const sanitized = sanitizers.username(value)
    return patterns.username.test(sanitized)
  },

  required: (value: string) => {
    const sanitized = sanitizers.text(value)
    return sanitized.length > 0
  },

  minLength: (value: string, min: number) => {
    const sanitized = sanitizers.text(value)
    return sanitized.length >= min
  },

  maxLength: (value: string, max: number) => {
    const sanitized = sanitizers.text(value)
    return sanitized.length <= max
  },

  secureInput: (value: string) => {
    const scan = securityScan(value)
    return scan.threats.length === 0
  },
}

// Export types
export type { SanitizationOptions }
