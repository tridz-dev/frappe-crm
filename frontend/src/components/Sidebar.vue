<template>
  <div>
    <!-- Your existing sidebar template -->
    <div v-for="item in navigationItems" :key="item.name">
      <!-- Your navigation item template -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import { messengerEnabled, isMessengerInstalled } from '@/composables/settings'

// Computed navigation items
const navigationItems = computed(() => {
  const baseItems = [
    // Your other navigation items here
  ]

  // Only add messenger tab if installed and enabled
  if (isMessengerInstalled.value && messengerEnabled.value) {
    baseItems.push({
      name: 'Messenger',
      icon: MessengerIcon,
      to: { name: 'Messenger' }
    })
  }

  return baseItems
})
</script>

<style>
  /* No changes to style section */
</style> 