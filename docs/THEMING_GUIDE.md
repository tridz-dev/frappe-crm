# CRM Comprehensive Theming Guide: Colors, Typography, Spacing & Sizing

## Overview

The CRM project uses a sophisticated theming system that allows you to **create complete design system themes using CSS variables**. This approach leverages the semantic color system from frappe-ui combined with custom typography, spacing, and sizing variables, making theme switching seamless across all design aspects.

## How It Works

### 1. **Comprehensive Design System**
Instead of just colors, themes now control:
- **Colors**: All surface, text, and outline colors
- **Typography**: Font families, sizes, weights, line heights
- **Spacing**: Margins, padding, gaps, component spacing
- **Sizing**: Border radius, component dimensions

### 2. **Semantic Variable System**
Variables use consistent naming patterns:
```css
/* Colors */
--surface-cards, --ink-gray-8, --outline-blue-2

/* Typography */
--font-family-sans, --text-base, --leading-normal, --font-medium

/* Spacing */
--space-md, --component-padding-lg

/* Sizing */
--border-radius-lg, --input-height-md, --button-height-lg
```

### 3. **Theme Scoping**
Themes are scoped using CSS attribute selectors:
```css
:root { /* Light theme (default) */ }
[data-theme="ocean"] { /* Ocean theme with condensed layout */ }
[data-theme="sunset"] { /* Sunset theme with generous spacing */ }
[data-theme="compact"] { /* Compact theme for dense interfaces */ }
[data-theme="cozy"] { /* Cozy theme for comfortable reading */ }
```

## Theme Variations

### Built-in Themes

1. **Light** (Default)
   - Standard sizing and spacing
   - Inter font family
   - Light color palette

2. **Dark** 
   - Same sizing as light
   - Dark color palette

3. **Ocean**
   - **Condensed typography** (smaller font sizes)
   - **Tighter spacing** (professional, data-heavy interfaces)
   - **Sharper borders** (more geometric feel)
   - Blue/teal color focus

4. **Sunset**
   - **Generous typography** (larger font sizes)
   - **Comfortable spacing** (relaxed, readable)
   - **Softer borders** (more rounded feel)
   - Warm orange/red color focus

5. **High Contrast**
   - **Large typography** (accessibility)
   - **Extra generous spacing** (touch-friendly)
   - **High contrast colors** (WCAG compliant)

6. **Compact**
   - **Minimal typography** (dense interfaces)
   - **Tight spacing** (information-heavy screens)
   - **Small components** (efficient use of space)

7. **Cozy**
   - **Large typography** (comfortable reading)
   - **Generous spacing** (relaxed feel)
   - **Large components** (easy interaction)

## CSS Variable Categories

### Typography Variables

```css
/* Font Families */
--font-family-sans: 'Inter', ui-sans-serif, system-ui, sans-serif;
--font-family-mono: ui-monospace, SFMono-Regular, monospace;

/* Font Sizes */
--text-xs: 0.75rem;       /* 12px */
--text-sm: 0.875rem;      /* 14px */
--text-base: 1rem;        /* 16px */
--text-lg: 1.125rem;      /* 18px */
--text-xl: 1.25rem;       /* 20px */
--text-2xl: 1.5rem;       /* 24px */
--text-3xl: 1.875rem;     /* 30px */

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Spacing Variables

```css
/* Base Spacing Scale */
--space-xs: 0.25rem;      /* 4px */
--space-sm: 0.5rem;       /* 8px */
--space-md: 0.75rem;      /* 12px */
--space-lg: 1rem;         /* 16px */
--space-xl: 1.25rem;      /* 20px */
--space-2xl: 1.5rem;      /* 24px */
--space-3xl: 2rem;        /* 32px */
--space-4xl: 2.5rem;      /* 40px */

/* Component-Specific Padding */
--component-padding-xs: 0.5rem;   /* 8px */
--component-padding-sm: 0.75rem;  /* 12px */
--component-padding-md: 1rem;     /* 16px */
--component-padding-lg: 1.25rem;  /* 20px */
--component-padding-xl: 1.5rem;   /* 24px */
```

### Sizing Variables

```css
/* Border Radius */
--border-radius-xs: 0.125rem;  /* 2px */
--border-radius-sm: 0.25rem;   /* 4px */
--border-radius-md: 0.375rem;  /* 6px */
--border-radius-lg: 0.5rem;    /* 8px */
--border-radius-xl: 0.75rem;   /* 12px */
--border-radius-2xl: 1rem;     /* 16px */

/* Component Heights */
--input-height-sm: 2rem;       /* 32px */
--input-height-md: 2.5rem;     /* 40px */
--input-height-lg: 3rem;       /* 48px */

--button-height-sm: 2rem;      /* 32px */
--button-height-md: 2.5rem;    /* 40px */
--button-height-lg: 3rem;      /* 48px */
```

## Creating Custom Themes

### Step 1: Define All Variables

Create a comprehensive theme by defining typography, spacing, sizing, and color variables:

```css
[data-theme="my-custom-theme"] {
  /* TYPOGRAPHY */
  --font-family-sans: 'Custom Font', sans-serif;
  --text-xs: 0.6875rem;
  --text-sm: 0.8125rem;
  --text-base: 0.9375rem;
  --text-lg: 1.0625rem;
  --text-xl: 1.1875rem;
  --text-2xl: 1.4375rem;
  --text-3xl: 1.8125rem;
  
  --leading-tight: 1.2;
  --leading-normal: 1.4;
  --leading-relaxed: 1.5;
  
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
  
  /* SPACING */
  --space-xs: 0.1875rem;
  --space-sm: 0.375rem;
  --space-md: 0.625rem;
  --space-lg: 0.875rem;
  --space-xl: 1.125rem;
  --space-2xl: 1.375rem;
  --space-3xl: 1.875rem;
  --space-4xl: 2.375rem;
  
  --component-padding-xs: 0.375rem;
  --component-padding-sm: 0.625rem;
  --component-padding-md: 0.875rem;
  --component-padding-lg: 1.125rem;
  --component-padding-xl: 1.375rem;
  
  /* SIZING */
  --border-radius-xs: 0.0625rem;
  --border-radius-sm: 0.1875rem;
  --border-radius-md: 0.3125rem;
  --border-radius-lg: 0.4375rem;
  --border-radius-xl: 0.625rem;
  --border-radius-2xl: 0.875rem;
  
  --input-height-sm: 1.875rem;
  --input-height-md: 2.25rem;
  --input-height-lg: 2.75rem;
  
  --button-height-sm: 1.875rem;
  --button-height-md: 2.25rem;
  --button-height-lg: 2.75rem;
  
  /* COLORS */
  --surface-white: 248 250 252;
  --surface-gray-1: 241 245 249;
  /* ... all color variables ... */
}
```

### Step 2: Apply the Theme

Set the theme using JavaScript:
```javascript
// Apply theme
document.documentElement.setAttribute('data-theme', 'my-custom-theme')

// Store preference
localStorage.setItem('crm-custom-theme', 'my-custom-theme')
```

## Using Theme Variables

### With Custom CSS Classes

The system provides utility classes for theme variables:

```vue
<template>
  <!-- Typography -->
  <h1 class="text-theme-3xl font-theme-bold leading-theme-tight">Heading</h1>
  <p class="text-theme-base leading-theme-normal">Body text</p>
  
  <!-- Spacing -->
  <div class="gap-theme-md p-theme-lg m-theme-xl">
    <!-- Content with theme-aware spacing -->
  </div>
  
  <!-- Sizing -->
  <button class="btn-theme-md rounded-theme-lg">
    Theme Button
  </button>
  
  <input class="input-theme rounded-theme-md" />
</template>
```

### With Component Classes

Pre-built component classes that adapt to themes:

```vue
<template>
  <!-- Cards -->
  <div class="card-theme">
    <h3 class="text-theme-lg font-theme-semibold">Card Title</h3>
    <p class="text-theme-sm">Card content</p>
  </div>
  
  <!-- Buttons -->
  <button class="button-theme-primary">Primary</button>
  <button class="button-theme-secondary">Secondary</button>
  
  <!-- Inputs -->
  <input class="input-theme" placeholder="Theme-aware input" />
</template>
```

### Direct CSS Variable Usage

```css
.custom-component {
  font-size: var(--text-lg);
  padding: var(--component-padding-md);
  border-radius: var(--border-radius-lg);
  margin: var(--space-xl);
}
```

## Theme Switching

### ThemeSwitcher Component

The `ThemeSwitcher.vue` component now shows:
- **Visual previews** of each theme
- **Typography samples** with actual font sizes
- **Spacing demonstrations** 
- **Component examples** showing real sizing
- **Live size values** for current theme

### Programmatic Switching

```javascript
import { setTheme } from '@/stores/theme'

// Switch to built-in themes
setTheme('dark')
setTheme('light')

// Switch to custom themes
document.documentElement.setAttribute('data-theme', 'ocean')
localStorage.setItem('crm-custom-theme', 'ocean')
```

## Best Practices

### 1. **Maintain Hierarchical Consistency**
- `text-xs` should always be smaller than `text-sm`
- `space-sm` should always be smaller than `space-md`
- Keep relative relationships consistent across themes

### 2. **Consider Use Cases**
- **Ocean**: Data-heavy interfaces, dashboards
- **Sunset**: Content-focused, reading-heavy interfaces  
- **Compact**: Dense information displays
- **Cozy**: User-friendly, accessible interfaces
- **High Contrast**: Accessibility compliance

### 3. **Test Across Breakpoints**
Typography and spacing should work across all screen sizes:

```css
[data-theme="mobile-optimized"] {
  --text-base: 1.125rem; /* Larger on mobile */
  --component-padding-md: 1.25rem; /* More touch-friendly */
}
```

### 4. **Performance Considerations**
- All variables are CSS custom properties (fast)
- Theme switching is instantaneous
- No JavaScript recalculation needed

## Advanced Usage

### Dynamic Theme Generation

```javascript
function generateTheme(config) {
  const scale = config.scale || 1
  const root = document.documentElement
  
  root.style.setProperty('--text-base', `${1 * scale}rem`)
  root.style.setProperty('--space-md', `${0.75 * scale}rem`)
  root.style.setProperty('--border-radius-md', `${0.375 * scale}rem`)
}

// Generate 120% scaled theme
generateTheme({ scale: 1.2 })
```

### Responsive Themes

```css
[data-theme="responsive"] {
  --text-base: 0.875rem;
  --component-padding-md: 0.75rem;
}

@media (min-width: 768px) {
  [data-theme="responsive"] {
    --text-base: 1rem;
    --component-padding-md: 1rem;
  }
}

@media (min-width: 1024px) {
  [data-theme="responsive"] {
    --text-base: 1.125rem;
    --component-padding-md: 1.25rem;
  }
}
```

### Theme Inheritance

```css
[data-theme="ocean-large"] {
  /* Inherit Ocean theme colors and sizing */
  --text-xs: 0.875rem;    /* Larger than Ocean's 0.6875rem */
  --text-sm: 1rem;        /* Larger than Ocean's 0.8125rem */
  --text-base: 1.125rem;  /* Larger than Ocean's 0.9375rem */
  /* Colors inherited from Ocean theme */
}
```

This comprehensive theming system gives you complete control over the visual and spatial aspects of your application while maintaining consistency and ease of use. 