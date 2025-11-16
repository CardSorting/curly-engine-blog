import { ref, watch } from 'vue'

type Theme = 'light' | 'dark' | 'system'

const theme = ref<Theme>('system')
const isDark = ref(false)

// Initialize theme from localStorage or system preference
const initTheme = () => {
  const stored = localStorage.getItem('theme') as Theme | null
  
  if (stored && ['light', 'dark', 'system'].includes(stored)) {
    theme.value = stored
  } else {
    theme.value = 'system'
  }
  
  updateTheme()
}

// Update the actual theme applied to the document
const updateTheme = () => {
  const html = document.documentElement
  
  if (theme.value === 'dark') {
    html.classList.add('dark')
    isDark.value = true
  } else if (theme.value === 'light') {
    html.classList.remove('dark')
    isDark.value = false
  } else {
    // system preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      html.classList.add('dark')
      isDark.value = true
    } else {
      html.classList.remove('dark')
      isDark.value = false
    }
  }
  
  // Save to localStorage
  localStorage.setItem('theme', theme.value)
}

// Watch for theme changes
watch(theme, updateTheme)

// Listen for system theme changes
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
mediaQuery.addEventListener('change', () => {
  if (theme.value === 'system') {
    updateTheme()
  }
})

export function useTheme() {
  const setTheme = (newTheme: Theme) => {
    theme.value = newTheme
  }
  
  const toggleTheme = () => {
    if (theme.value === 'light') {
      setTheme('dark')
    } else if (theme.value === 'dark') {
      setTheme('system')
    } else {
      setTheme('light')
    }
  }
  
  // Initialize on first use
  if (!localStorage.getItem('theme') && !document.documentElement.classList.contains('dark')) {
    initTheme()
  }
  
  return {
    theme: theme.value,
    isDark: isDark.value,
    setTheme,
    toggleTheme,
    initTheme
  }
}
