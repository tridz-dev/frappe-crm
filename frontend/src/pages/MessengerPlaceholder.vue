<template>
  <div class="flex-1 grid place-items-center bg-surface-gray-1 h-full min-h-0">
    <div class="text-center">
      <div class="mx-auto h-12 w-12 text-ink-gray-2">
        <MessengerIcon />
      </div>
      <h3 class="mt-2 text-sm font-medium text-ink-gray-9">{{ __('No conversation selected') }}</h3>
      <p class="mt-1 text-sm text-ink-gray-3">{{ __('Choose a conversation to start messaging') }}</p>
    </div>
  </div>
</template>

<script setup>
import MessengerIcon from '@/components/Icons/Messenger.vue'
</script> 