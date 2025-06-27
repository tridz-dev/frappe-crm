import { useStorage } from '@vueuse/core'

export const theme = useStorage('theme', 'light')

export function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme')
  theme.value = currentTheme === 'dark' ? 'light' : 'dark'
  document.documentElement.setAttribute('data-theme', theme.value)
}

export function setTheme(value) {
  theme.value = value || theme.value
  
  // Handle all themes - both default and custom
  if (['light', 'dark'].includes(theme.value)) {
    // For default themes, set data-theme attribute directly
    document.documentElement.setAttribute('data-theme', theme.value)
  } else if (theme.value) {
    // For custom themes, set data-theme attribute with the custom theme name
    document.documentElement.setAttribute('data-theme', theme.value)
  }
}
