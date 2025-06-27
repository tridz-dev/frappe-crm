export const themeDefinitions = [
  { 
    label: 'Light', 
    value: 'light',
    description: 'Clean and bright interface',
    preview: {
      colors: ['bg-gray-50', 'bg-gray-200', 'bg-blue-100']
    }
  },
  { 
    label: 'Dark', 
    value: 'dark',
    description: 'Easy on the eyes',
    preview: {
      colors: ['bg-gray-800', 'bg-gray-600', 'bg-blue-900']
    }
  },
  { 
    label: 'Compact', 
    value: 'compact',
    description: 'Dense, space-efficient',
    preview: {
      colors: ['bg-gray-100', 'bg-gray-300', 'bg-blue-200']
    }
  },
  { 
    label: 'Ant', 
    value: 'ant',
    description: 'Modern dark theme with vibrant accents',
    preview: {
      colors: ['bg-slate-900', 'bg-blue-500', 'bg-indigo-600']
    }
  },
  { 
    label: 'Nebula', 
    value: 'nebula',
    description: 'Cosmic dashboard with stellar accents',
    preview: {
      colors: ['bg-slate-800', 'bg-cyan-400', 'bg-amber-400']
    }
  }
]

export const getThemeByValue = (value) => {
  return themeDefinitions.find(theme => theme.value === value)
}

export const getAvailableThemes = () => {
  return themeDefinitions
} 