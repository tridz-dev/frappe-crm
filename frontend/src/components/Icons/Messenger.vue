<!-- Messenger Icon -->
<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 24 24"
    :width="size"
    :height="size"
    class=""
  >
    <path
      fill="currentColor"
      d="M12 2C6.477 2 2 6.145 2 11.259c0 2.913 1.454 5.512 3.726 7.21V22l3.405-1.869c.909.252 1.871.388 2.869.388 5.523 0 10-4.145 10-9.259C22 6.145 17.523 2 12 2zm1 13.5l-2.5-2.667L6 16l5.5-5.833L14 13l4.5-3.167L13 15.5z"
    />
  </svg>
</template>

<script setup>
defineProps({
  size: {
    type: [Number, String],
    default: 24
  },
  class: {
    type: String,
    default: ''
  }
})
</script> 