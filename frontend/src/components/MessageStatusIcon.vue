<template>
  <div class="flex items-center">
    <!-- Single tick for sent -->
    <CheckIcon v-if="status === 'Sent'" class="size-4" />
    <!-- Double tick for delivered/read, using DoubleCheckIcon for WhatsApp style -->
    <DoubleCheckIcon v-else-if="status === 'Delivered'" class="size-4" />
    <DoubleCheckIcon v-else-if="status === 'Read'" class="size-4 text-blue-500" />
  </div>
</template>

<script setup>
import CheckIcon from '@/components/Icons/CheckIcon.vue'
import DoubleCheckIcon from '@/components/Icons/DoubleCheckIcon.vue'

defineProps({
  status: {
    type: String,
    default: 'Sent',
    validator: (value) => ['Sent', 'Delivered', 'Read'].includes(value)
  }
})
</script> 