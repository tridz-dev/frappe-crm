<template>
  <div>
    <div
      v-if="reply?.message"
      class="flex items-center justify-around gap-2 px-3 pt-2"
    >
      <div
        class="mb-1 flex-1 cursor-pointer rounded border-0 border-l-4 bg-surface-gray-2 p-2 text-base text-ink-gray-5"
        :class="reply.message_direction == 'Incoming' ? 'border-green-500' : 'border-blue-400'"
      >
        <div
          class="mb-1 text-sm font-bold"
          :class="reply.message_direction == 'Incoming' ? 'text-ink-green-2' : 'text-ink-blue-link'"
        >
          {{ reply.sender_id || __('You') }}
        </div>
        <div class="max-h-12 overflow-hidden" v-html="formatMessage(reply.message)" />
      </div>
      <Button variant="ghost" icon="x" @click="reply = {}" />
    </div>

    <div class="flex items-end gap-2 px-3 py-2.5">
      <div class="flex h-8 items-center gap-2">
        <FileUploader @success="(file) => uploadFile(file)">
          <template v-slot="{ openFileSelector }">
            <div class="flex items-center space-x-2">
              <Dropdown :options="uploadOptions(openFileSelector)">
                <FeatherIcon
                  name="plus"
                  class="size-4.5 cursor-pointer text-ink-gray-5"
                />
              </Dropdown>
            </div>
          </template>
        </FileUploader>
        <IconPicker
          v-model="emoji"
          v-slot="{ togglePopover }"
          @update:modelValue="
            () => {
              message += emoji
              $refs.textareaRef.el.focus()
            }
          "
        >
          <Button
            appearance="minimal"
            class="text-gray-600"
            :icon="EmojiIcon"
            @click="togglePopover"
          />
        </IconPicker>
        <Button
          appearance="minimal"
          class="text-gray-600"
          :icon="CannedResponseIcon"
          @click="showCannedResponseModal = true"
        />
      </div>

      <Textarea
        ref="textareaRef"
        type="textarea"
        class="min-h-8 w-full"
        :rows="rows"
        v-model="message"
        :placeholder="__('Type your message here...')"
        @focus="rows = 6"
        @blur="rows = 1"
        @keydown.enter.stop="(e) => sendTextMessage(e)"
      />

      <Button
        appearance="primary"
        :icon="SendIcon"
        @click="sendTextMessage"
      />
    </div>
  </div>

  <CannedResponseSelectorModal
    v-model="showCannedResponseModal"
    @apply="handleCannedResponseSelect"
  />
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { createResource, Button, Textarea, FileUploader, Dropdown, FeatherIcon } from 'frappe-ui'
import IconPicker from '@/components/IconPicker.vue'
import SendIcon from '@/components/Icons/SendIcon.vue'
import EmojiIcon from '@/components/Icons/EmojiIcon.vue'
import CannedResponseIcon from '@/components/Icons/CannedResponseIcon.vue'
import CannedResponseSelectorModal from '@/components/CannedResponseSelectorModal.vue'

const props = defineProps({
  conversation: String,
})

const emit = defineEmits(['send'])
const reply = defineModel('reply')
const rows = ref(1)
const textareaRef = ref(null)
const emoji = ref('')
const message = ref('')
const fileType = ref('')
const attachment = ref('')
const showCannedResponseModal = ref(false)

function show() {
  nextTick(() => textareaRef.value.el.focus())
}

function uploadFile(file) {
  attachment.value = file.file_url
  sendMessage({
    message: file.file_name,
    content_type: fileType.value,
    attach: file.file_url
  })
}

function sendTextMessage(event) {
  if (event?.shiftKey) return
  if (!message.value.trim()) return
  
  sendMessage({
    message: message.value,
    content_type: 'text'
  })
  
  textareaRef.value.el?.blur()
  message.value = ''
}

function sendMessage(data) {
  emit('send', {
    conversation: props.conversation,
    message: data.message,
    content_type: data.content_type || 'text',
    attach: data.attach || '',
    reply_to: reply.value?.name || ''
  })
  
  // Reset states
  fileType.value = ''
  attachment.value = ''
  reply.value = {}
}

function uploadOptions(openFileSelector) {
  return [
    {
      label: __('Upload Document'),
      icon: 'file',
      onClick: () => {
        fileType.value = 'document'
        openFileSelector()
      },
    },
    {
      label: __('Upload Image'),
      icon: 'image',
      onClick: () => {
        fileType.value = 'image'
        openFileSelector('image/*')
      },
    },
    {
      label: __('Upload Video'),
      icon: 'video',
      onClick: () => {
        fileType.value = 'video'
        openFileSelector('video/*')
      },
    },
    {
      label: __('Upload Audio'),
      icon: 'mic',
      onClick: () => {
        fileType.value = 'audio'
        openFileSelector('audio/*')
      },
    }
  ]
}

function formatMessage(message) {
  if (!message) return ''
  
  message = message.replace(/_(.*?)_/g, '<i>$1</i>')
  message = message.replace(/\*(.*?)\*/g, '<b>$1</b>')
  message = message.replace(/~(.*?)~/g, '<s>$1</s>')
  message = message.replace(/```(.*?)```/g, '<code>$1</code>')
  message = message.replace(/`(.*?)`/g, '<code>$1</code>')
  message = message.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>')
  message = message.replace(/\n/g, '<br>')
  
  return message
}

function handleCannedResponseSelect(template) {
  message.value = template.message
  showCannedResponseModal.value = false
}

watch(reply, (value) => {
  if (value?.message) {
    show()
  }
})

defineExpose({ show })
</script> 