# CRM Theming Guide: Adding New Themes with CSS Variables

## Overview

The CRM project uses a sophisticated theming system that allows you to **add new themes using only CSS variables**. This approach leverages the semantic color system from frappe-ui where Tailwind classes reference CSS variables, making theme switching seamless.

## How It Works

### 1. **Semantic Color System**
Instead of hard-coded colors, the system uses semantic names:
- `bg-surface-gray-1` → `var(--surface-gray-1)`
- `text-ink-gray-8` → `var(--text-ink-gray-8)`
- `border-outline-gray-2` → `var(--outline-gray-2)`

### 2. **Theme Scoping**
Themes are scoped using CSS attribute selectors:
```css
:root { /* Light theme (default) */ }
[data-theme="dark"] { /* Dark theme */ }
[data-theme="ocean"] { /* Custom ocean theme */ }
```

### 3. **Variable Structure**
All CSS variables follow a consistent naming pattern:
```
--{category}-{color}-{variant}
```

**Categories:**
- `outline-*` - For borders, outlines, dividers
- `surface-*` - For backgrounds, cards, surfaces
- `text-ink-*` - For text colors, icons, foreground elements

## Adding New Themes

### Step 1: Define CSS Variables

Create a new theme by defining all required CSS variables under a data attribute selector:

```css
[data-theme="your-theme-name"] {
  /* OUTLINE VARIABLES - Borders & Dividers */
  --outline-white: 255 255 255;
  --outline-gray-1: 226 232 240;
  --outline-gray-2: 203 213 225;
  --outline-gray-3: 148 163 184;
  --outline-gray-4: 100 116 139;
  --outline-gray-5: 51 65 85;
  --outline-gray-modals: 203 213 225;
  
  /* Status outline colors */
  --outline-red-1: 252 165 165;
  --outline-red-2: 239 68 68;
  --outline-red-3: 220 38 38;
  --outline-green-1: 134 239 172;
  --outline-green-2: 34 197 94;
  --outline-blue-1: 147 197 253;
  --outline-blue-2: 59 130 246;
  --outline-amber-1: 253 230 138;
  --outline-amber-2: 245 158 11;
  --outline-orange-1: 251 146 60;

  /* SURFACE VARIABLES - Backgrounds */
  --surface-white: 248 250 252;
  --surface-gray-1: 241 245 249;
  --surface-gray-2: 226 232 240;
  --surface-gray-3: 203 213 225;
  --surface-gray-4: 148 163 184;
  --surface-gray-5: 51 65 85;
  --surface-gray-6: 30 41 59;
  --surface-gray-7: 15 23 42;
  
  /* Special surfaces */
  --surface-cards: 255 255 255;
  --surface-modal: 255 255 255;
  --surface-menu-bar: 241 245 249;
  --surface-selected: 219 234 254;
  
  /* Status surface colors */
  --surface-red-1: 254 226 226;
  --surface-red-2: 252 165 165;
  --surface-red-3: 239 68 68;
  --surface-green-1: 220 252 231;
  --surface-green-2: 187 247 208;
  --surface-green-3: 34 197 94;
  --surface-blue-1: 219 234 254;
  --surface-blue-2: 59 130 246;
  --surface-amber-1: 254 243 199;
  --surface-amber-2: 245 158 11;
  --surface-orange-1: 254 215 170;
  --surface-violet-1: 237 233 254;
  --surface-cyan-1: 207 250 254;
  --surface-pink-1: 252 231 243;

  /* TEXT/INK VARIABLES - Text & Foreground */
  --text-ink-white: 255 255 255;
  --text-ink-gray-1: 203 213 225;
  --text-ink-gray-2: 148 163 184;
  --text-ink-gray-3: 100 116 139;
  --text-ink-gray-4: 71 85 105;
  --text-ink-gray-5: 51 65 85;
  --text-ink-gray-6: 30 41 59;
  --text-ink-gray-7: 15 23 42;
  --text-ink-gray-8: 2 6 23;
  --text-ink-gray-9: 0 0 0;
  
  /* Status text colors */
  --text-ink-red-1: 254 226 226;
  --text-ink-red-2: 239 68 68;
  --text-ink-red-3: 220 38 38;
  --text-ink-red-4: 185 28 28;
  /* ... continue for all status colors */
}
```

### Step 2: Color Value Format

**Important:** CSS variable values use **space-separated RGB values** (not comma-separated):
```css
/* Correct */
--surface-blue-1: 219 234 254;

/* Wrong */
--surface-blue-1: rgb(219, 234, 254);
--surface-blue-1: #dbdafe;
```

This format allows Tailwind to apply opacity modifiers (`bg-surface-blue-1/50`).

### Step 3: Apply the Theme

Set the theme using JavaScript:
```javascript
// Apply theme
document.documentElement.setAttribute('data-theme', 'your-theme-name')

// Remove theme (back to light)
document.documentElement.removeAttribute('data-theme')
```

## Required CSS Variables

### Core Variables (Must Define)

#### Outline/Border Colors:
```css
--outline-white
--outline-gray-1, --outline-gray-2, --outline-gray-3, --outline-gray-4, --outline-gray-5
--outline-gray-modals
--outline-red-1, --outline-red-2, --outline-red-3
--outline-green-1, --outline-green-2
--outline-blue-1, --outline-blue-2
--outline-amber-1, --outline-amber-2
--outline-orange-1
```

#### Surface/Background Colors:
```css
--surface-white
--surface-gray-1 through --surface-gray-7
--surface-cards, --surface-modal, --surface-menu-bar, --surface-selected
--surface-red-1, --surface-red-2, --surface-red-3
--surface-green-1, --surface-green-2, --surface-green-3
--surface-blue-1, --surface-blue-2
--surface-amber-1, --surface-amber-2
--surface-orange-1, --surface-violet-1, --surface-cyan-1, --surface-pink-1
```

#### Text/Ink Colors:
```css
--text-ink-white
--text-ink-gray-1 through --text-ink-gray-9
--text-ink-red-1, --text-ink-red-2, --text-ink-red-3, --text-ink-red-4
--text-ink-green-1, --text-ink-green-2, --text-ink-green-3
--text-ink-blue-1, --text-ink-blue-2, --text-ink-blue-3, --text-ink-blue-4
--text-ink-amber-1, --text-ink-amber-2, --text-ink-amber-3
--text-ink-cyan-1, --text-ink-pink-1, --text-ink-violet-1
```

## Usage in Components

Once themes are defined, use semantic Tailwind classes in your components:

```vue
<template>
  <div class="bg-surface-cards border border-outline-gray-2 rounded-lg p-4">
    <h3 class="text-ink-gray-8 font-medium mb-2">Card Title</h3>
    <p class="text-ink-gray-6 text-sm">Card description text</p>
    
    <button class="bg-surface-blue-2 text-ink-white px-3 py-1.5 rounded-md">
      Primary Action
    </button>
    
    <button class="bg-surface-gray-2 text-ink-gray-8 border border-outline-gray-2 px-3 py-1.5 rounded-md">
      Secondary Action
    </button>
  </div>
</template>
```

## Theme Examples

### Ocean Theme (Blue/Teal Focus)
```css
[data-theme="ocean"] {
  --surface-white: 248 250 252;
  --surface-gray-1: 241 245 249;
  --text-ink-gray-8: 2 6 23;
  --surface-blue-1: 219 234 254;
  --text-ink-blue-2: 59 130 246;
  /* ... */
}
```

### Sunset Theme (Warm Orange/Red Focus)
```css
[data-theme="sunset"] {
  --surface-white: 255 253 250;
  --surface-gray-1: 252 248 245;
  --text-ink-gray-8: 40 25 15;
  --surface-orange-1: 255 237 213;
  --text-ink-red-2: 255 99 71;
  /* ... */
}
```

### High Contrast Theme (Accessibility)
```css
[data-theme="high-contrast"] {
  --surface-white: 255 255 255;
  --surface-gray-1: 250 250 250;
  --text-ink-gray-8: 5 5 5;
  --surface-selected: 255 255 0; /* High contrast selection */
  --text-ink-red-2: 255 0 0; /* Pure red for visibility */
  /* ... */
}
```

## Best Practices

### 1. **Consistent Hierarchy**
Maintain consistent lightness/darkness hierarchy:
- `gray-1` should always be lighter than `gray-2`
- `gray-8` should be dark enough for body text
- `gray-9` should be the darkest text color

### 2. **Sufficient Contrast**
Ensure adequate contrast ratios:
- Body text: minimum 4.5:1 contrast ratio
- Large text: minimum 3:1 contrast ratio
- Interactive elements: minimum 3:1 contrast ratio

### 3. **Status Color Consistency**
Keep status colors semantically consistent:
- Red: errors, danger, deletion
- Green: success, positive actions
- Blue: information, primary actions
- Amber/Yellow: warnings, caution

### 4. **Test Across Components**
Test your theme with:
- Form elements (inputs, buttons, checkboxes)
- Navigation (menus, links, breadcrumbs)
- Data display (tables, cards, lists)
- Modals and overlays
- Status indicators

## Implementation Files

1. **`src/themes.css`** - Define your custom themes
2. **`src/index.css`** - Import themes: `@import './themes.css';`
3. **Theme switcher component** - Handle theme changes via JavaScript

## Advanced Features

### Dynamic Theme Generation
You can generate themes programmatically:

```javascript
function generateTheme(baseColor) {
  const theme = {}
  // Generate variations of baseColor for all required variables
  theme['--surface-blue-1'] = lighten(baseColor, 0.9)
  theme['--surface-blue-2'] = baseColor
  theme['--text-ink-blue-2'] = baseColor
  // Apply to document
  Object.entries(theme).forEach(([prop, value]) => {
    document.documentElement.style.setProperty(prop, value)
  })
}
```

### Theme Inheritance
Create theme variants by extending existing themes:

```css
[data-theme="ocean-dark"] {
  /* Import ocean theme base, then override specific variables */
  --surface-white: 15 23 42;
  --surface-cards: 30 41 59;
  --text-ink-gray-8: 226 232 240;
}
```

This approach gives you complete control over theming while maintaining compatibility with all existing components and the frappe-ui system. 