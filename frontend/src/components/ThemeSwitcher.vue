<template>
  <div class="theme-switcher-full">
    <!-- Theme Selection -->
    <div class="space-y-4">
      <h4 class="text-ink-gray-8 text-sm font-medium">Choose Theme</h4>
      
      <!-- Theme Options -->
      <div class="grid grid-cols-2 gap-3 md:grid-cols-3">
        <button
          v-for="themeOption in themes"
          :key="themeOption.value"
          @click="handleThemeChange(themeOption.value)"
          :class="[
            'flex flex-col items-center gap-2 p-3 rounded-lg border transition-all',
            currentTheme === themeOption.value
              ? 'border-outline-blue-2 bg-surface-blue-1 text-ink-blue-3'
              : 'border-outline-gray-2 bg-surface-white hover:bg-surface-gray-1'
          ]"
        >
          <div class="flex gap-1">
            <!-- Theme preview colors -->
            <div 
              v-for="color in themeOption.preview" 
              :key="color"
              :class="`w-3 h-3 rounded-full ${color}`"
            ></div>
          </div>
          <span class="text-xs font-medium">{{ themeOption.label }}</span>
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
      
      <div class="p-4 bg-surface-cards border border-outline-gray-2 rounded-lg space-y-4">
        <!-- Surface Colors -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Surface Colors</p>
          <div class="flex gap-2">
            <div class="w-8 h-8 bg-surface-gray-1 border border-outline-gray-2 rounded"></div>
            <div class="w-8 h-8 bg-surface-gray-2 border border-outline-gray-2 rounded"></div>
            <div class="w-8 h-8 bg-surface-gray-3 border border-outline-gray-2 rounded"></div>
            <div class="w-8 h-8 bg-surface-blue-1 border border-outline-gray-2 rounded"></div>
            <div class="w-8 h-8 bg-surface-green-1 border border-outline-gray-2 rounded"></div>
            <div class="w-8 h-8 bg-surface-red-1 border border-outline-gray-2 rounded"></div>
          </div>
        </div>
        
        <!-- Text Colors -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Text Colors</p>
          <div class="space-y-1">
            <p class="text-ink-gray-9 text-sm">Primary text (gray-9)</p>
            <p class="text-ink-gray-6 text-sm">Secondary text (gray-6)</p>
            <p class="text-ink-blue-2 text-sm">Blue accent text</p>
            <p class="text-ink-green-2 text-sm">Green accent text</p>
            <p class="text-ink-red-2 text-sm">Red accent text</p>
          </div>
        </div>
        
        <!-- Interactive Elements -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Buttons</p>
          <div class="flex gap-2">
            <button class="px-3 py-1.5 bg-surface-blue-2 text-ink-white text-sm rounded-md">
              Primary
            </button>
            <button class="px-3 py-1.5 bg-surface-gray-2 text-ink-gray-8 text-sm rounded-md border border-outline-gray-2">
              Secondary
            </button>
          </div>
        </div>
        
        <!-- Form Elements -->
        <div>
          <p class="text-xs text-ink-gray-6 mb-2">Form Elements</p>
          <div class="space-y-2 max-w-xs">
            <input 
              type="text" 
              placeholder="Sample input field"
              class="form-input w-full"
            />
            <div class="flex items-center gap-2">
              <input type="checkbox" class="form-checkbox" />
              <label class="text-ink-gray-8 text-sm">Sample checkbox</label>
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

// Props to control display
const props = defineProps({
  showPreview: {
    type: Boolean,
    default: false
  }
})

const currentTheme = ref('light')

const themes = [
  { 
    label: 'Light', 
    value: 'light',
    preview: ['bg-gray-50', 'bg-gray-200', 'bg-blue-100']
  },
  { 
    label: 'Dark', 
    value: 'dark',
    preview: ['bg-gray-800', 'bg-gray-600', 'bg-blue-900']
  },
  { 
    label: 'Ocean', 
    value: 'ocean',
    preview: ['bg-slate-100', 'bg-blue-200', 'bg-teal-100']
  },
  { 
    label: 'Sunset', 
    value: 'sunset',
    preview: ['bg-orange-100', 'bg-red-200', 'bg-amber-100']
  },
  { 
    label: 'High Contrast', 
    value: 'high-contrast',
    preview: ['bg-white', 'bg-black', 'bg-yellow-400']
  }
]

const handleThemeChange = (newTheme) => {
  currentTheme.value = newTheme
  
  // Update the existing theme store for light/dark
  if (['light', 'dark'].includes(newTheme)) {
    setTheme(newTheme)
  } else {
    // Handle custom themes
    document.documentElement.setAttribute('data-theme', newTheme)
    localStorage.setItem('crm-custom-theme', newTheme)
  }
  
  // Special handling for light theme
  if (newTheme === 'light') {
    document.documentElement.removeAttribute('data-theme')
    localStorage.removeItem('crm-custom-theme')
  }
}

onMounted(() => {
  // Initialize current theme
  const savedCustomTheme = localStorage.getItem('crm-custom-theme')
  if (savedCustomTheme) {
    currentTheme.value = savedCustomTheme
  } else {
    currentTheme.value = theme.value || 'light'
  }
})
</script>

<style scoped>
.theme-switcher-full {
  @apply w-full;
}
</style> 