<template>
  <div class="theme-switcher-full">
    <!-- Theme Selection -->
    <div class="space-y-4">
      <h4 class="text-ink-gray-8 text-sm font-medium">Choose Theme</h4>
      
      <!-- Theme Options -->
      <div class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
        <button
          v-for="themeOption in themes"
          :key="themeOption.value"
          @click="handleThemeChange(themeOption.value)"
          :class="[
            'flex flex-col items-center gap-2 p-3 rounded-lg border transition-all text-left',
            currentTheme === themeOption.value
              ? 'border-outline-blue-2 bg-surface-blue-1 text-ink-blue-3'
              : 'border-outline-gray-2 bg-surface-white hover:bg-surface-gray-1'
          ]"
        >
          <div class="flex gap-1">
            <!-- Theme preview colors -->
            <div 
              v-for="color in themeOption.preview.colors" 
              :key="color"
              :class="`w-3 h-3 rounded-full ${color}`"
            ></div>
          </div>
          <span class="text-xs font-medium">{{ themeOption.label }}</span>
          <p class="text-2xs text-ink-gray-6 text-center">{{ themeOption.description }}</p>
          <div 
            v-if="currentTheme === themeOption.value"
            class="w-4 h-4 rounded-full bg-ink-blue-2 flex items-center justify-center"
          >
            <div class="w-2 h-2 rounded-full bg-white"></div>
          </div>
        </button>
      </div>
    </div>
    
    <!-- Theme Preview (if enabled) -->
    <div v-if="showPreview" class="mt-6 space-y-4">
      <h4 class="text-ink-gray-8 text-sm font-medium">Preview</h4>
      
      <div class="p-4 bg-surface-cards border border-outline-gray-2 rounded-lg space-y-6">
        <!-- Typography Preview -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Typography</p>
          <div class="space-y-2">
            <div class="text-theme-3xl font-theme-bold leading-theme-tight text-ink-gray-9">
              Heading ({{ getCurrentThemeSize('text-3xl') }})
            </div>
            <div class="text-theme-lg font-theme-medium leading-theme-normal text-ink-gray-8">
              Subheading ({{ getCurrentThemeSize('text-lg') }})
            </div>
            <div class="text-theme-base font-theme-normal leading-theme-normal text-ink-gray-7">
              Body text ({{ getCurrentThemeSize('text-base') }})
            </div>
            <div class="text-theme-sm font-theme-normal leading-theme-relaxed text-ink-gray-6">
              Small text ({{ getCurrentThemeSize('text-sm') }})
            </div>
          </div>
        </div>
        
        <!-- Spacing Preview -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Spacing</p>
          <div class="flex gap-theme-md items-center">
            <div class="space-theme-xs bg-surface-gray-3 rounded-theme-sm"></div>
            <div class="space-theme-sm bg-surface-gray-3 rounded-theme-sm"></div>
            <div class="space-theme-md bg-surface-gray-3 rounded-theme-sm"></div>
            <div class="space-theme-lg bg-surface-gray-3 rounded-theme-sm"></div>
            <div class="space-theme-xl bg-surface-gray-3 rounded-theme-sm"></div>
          </div>
          <p class="text-2xs text-ink-gray-5 mt-1">
            XS: {{ getCurrentThemeSize('space-xs') }}, 
            SM: {{ getCurrentThemeSize('space-sm') }}, 
            MD: {{ getCurrentThemeSize('space-md') }}, 
            LG: {{ getCurrentThemeSize('space-lg') }}, 
            XL: {{ getCurrentThemeSize('space-xl') }}
          </p>
        </div>
        
        <!-- Surface Colors -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Surface Colors</p>
          <div class="flex gap-2">
            <div class="w-8 h-8 bg-surface-gray-1 border border-outline-gray-2 rounded-theme-sm"></div>
            <div class="w-8 h-8 bg-surface-gray-2 border border-outline-gray-2 rounded-theme-sm"></div>
            <div class="w-8 h-8 bg-surface-gray-3 border border-outline-gray-2 rounded-theme-sm"></div>
            <div class="w-8 h-8 bg-surface-blue-1 border border-outline-gray-2 rounded-theme-sm"></div>
            <div class="w-8 h-8 bg-surface-green-1 border border-outline-gray-2 rounded-theme-sm"></div>
            <div class="w-8 h-8 bg-surface-red-1 border border-outline-gray-2 rounded-theme-sm"></div>
          </div>
        </div>
        
        <!-- Border Radius Preview -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Border Radius</p>
          <div class="flex gap-2 items-end">
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-xs"></div>
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-sm"></div>
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-md"></div>
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-lg"></div>
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-xl"></div>
            <div class="w-6 h-6 bg-surface-blue-2 rounded-theme-2xl"></div>
          </div>
        </div>
        
        <!-- Interactive Elements -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Components</p>
          <div class="space-y-3">
            <!-- Buttons -->
            <div class="flex gap-theme-md">
              <button class="button-theme-primary">
                Primary Button
              </button>
              <button class="button-theme-secondary">
                Secondary Button
              </button>
            </div>
            
            <!-- Form Elements -->
            <div class="space-y-2 max-w-xs">
              <input 
                type="text" 
                placeholder="Theme-aware input field"
                class="input-theme w-full"
              />
              <div class="flex items-center gap-theme-sm">
                <input type="checkbox" class="form-checkbox rounded-theme-xs" />
                <label class="text-theme-sm text-ink-gray-8">Sample checkbox</label>
              </div>
            </div>
            
            <!-- Card Example -->
            <div class="card-theme max-w-sm">
              <h5 class="text-theme-lg font-theme-semibold text-ink-gray-8 mb-1">Card Title</h5>
              <p class="text-theme-sm text-ink-gray-6">Theme-aware card component with proper spacing and typography.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { theme, setTheme } from '@/stores/theme'
import { getAvailableThemes } from '@/themes/themeConfig'

// Props to control display
const props = defineProps({
  showPreview: {
    type: Boolean,
    default: false
  }
})

const currentTheme = ref('light')

const themes = getAvailableThemes()

const handleThemeChange = (newTheme) => {
  currentTheme.value = newTheme
  
  // Use the theme store to handle all theme changes
  setTheme(newTheme)
  
  // Debug current theme values
  setTimeout(() => debugThemeValues(), 100)
}

const getCurrentThemeSize = (property) => {
  if (typeof window !== 'undefined') {
    const value = getComputedStyle(document.documentElement).getPropertyValue(`--${property}`)
    return value.trim() || 'default'
  }
  return 'default'
}

// Debug function to log current theme values
const debugThemeValues = () => {
  if (typeof window !== 'undefined') {
    const root = document.documentElement
    console.log('Current theme values:', {
      'text-base': getComputedStyle(root).getPropertyValue('--text-base'),
      'space-md': getComputedStyle(root).getPropertyValue('--space-md'),
      'border-radius-md': getComputedStyle(root).getPropertyValue('--border-radius-md'),
      'input-height-md': getComputedStyle(root).getPropertyValue('--input-height-md'),
      currentTheme: root.getAttribute('data-theme') || 'light'
    })
  }
}

onMounted(() => {
  // Just sync the current theme display with the actual theme
  currentTheme.value = theme.value
})
</script>

<style scoped>
.theme-switcher-full {
  @apply w-full;
}
</style> 