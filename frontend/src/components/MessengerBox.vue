<template>
  <div>
    <div
      v-if="reply?.message"
      class="flex items-center justify-around gap-2 px-3 pt-2 sm:px-10"
    >
      <div
        class="mb-1 ml-13 flex-1 cursor-pointer rounded border-0 border-l-4 border-green-500 bg-surface-gray-2 p-2 text-base text-ink-gray-5"
        :class="reply.message_direction == 'Incoming' ? 'border-green-500' : 'border-blue-400'"
      >
        <div
          class="mb-1 text-sm font-bold"
          :class="reply.message_direction == 'Incoming' ? 'text-ink-green-2' : 'text-ink-blue-link'"
        >
          {{ reply.sender_user || reply.sender_id || __('You') }}
        </div>
        <div class="max-h-12 overflow-hidden" v-html="reply.message" />
      </div>

      <Button variant="ghost" icon="x" @click="reply = {}" />
    </div>
    <div class="flex items-end gap-2 px-3 py-2.5 sm:px-10">
      <div class="flex h-8 items-center gap-2">
        <IconPicker
          v-model="emoji"
          v-slot="{ togglePopover }"
          @update:modelValue="
            () => {
              content += emoji
              $refs.textareaRef.el.focus()
            }
          "
        >
          <SmileIcon
            @click="togglePopover"
            class="flex size-4.5 cursor-pointer rounded-sm text-xl leading-none text-ink-gray-4"
          />
        </IconPicker>
      </div>
      <Textarea
        ref="textareaRef"
        type="textarea"
        class="min-h-8 w-full"
        :rows="rows"
        v-model="content"
        :placeholder="placeholder"
        @focus="rows = 6"
        @blur="rows = 1"
        @keydown.enter.exact="(e) => sendTextMessage(e)"
      />
    </div>
  </div>
</template>

<script setup>
import IconPicker from '@/components/IconPicker.vue'
import SmileIcon from '@/components/Icons/SmileIcon.vue'
import { Textarea, Button } from 'frappe-ui'
import { ref, nextTick, watch } from 'vue'

const props = defineProps({
  conversation: String,
})

const emit = defineEmits(['send'])
const reply = defineModel('reply')
const rows = ref(1)
const textareaRef = ref(null)
const emoji = ref('')
const content = ref('')
const placeholder = ref(__('Type your message here...'))

function show() {
  nextTick(() => textareaRef.value.el.focus())
}

function sendTextMessage(event) {
  if (event.shiftKey) return
  
  if (!content.value.trim() || !props.conversation) return
  
  emit('send', {
    message: content.value,
    conversation: props.conversation,
    reply_to: reply.value?.name || '',
  })
  
  textareaRef.value.el?.blur()
  content.value = ''
  reply.value = {}
}

watch(reply, (value) => {
  if (value?.message) {
    show()
  }
})

defineExpose({ show })
</script> 