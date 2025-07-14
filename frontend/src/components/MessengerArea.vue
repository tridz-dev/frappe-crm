<template>
  <div>
    <div
      v-for="message in messages"
      :key="message.name"
      class="activity group flex gap-2"
      :class="[
        message.message_direction == 'Outgoing' ? 'flex-row-reverse' : '',
        'mb-3'
      ]"
    >
      <div
        :id="message.name"
        class="group/message relative max-w-[90%] rounded-md bg-surface-gray-1 text-ink-gray-9 p-1.5 pl-2 text-base shadow-sm"
      >
        <div class="flex gap-2 justify-between">
          <!-- Message Content -->
          <div class="flex flex-col gap-2">
            <!-- Text Message -->
            <div v-if="!message.content_type || message.content_type === 'text' || message.content_type === 'flow'"
              v-html="formatMessage(message.message)"
            />

            <!-- Image Message -->
            <div v-else-if="message.content_type === 'image'" class="flex flex-col gap-2">
              <img
                :src="message.attach"
                class="h-40 cursor-pointer rounded-md"
                @click="() => openFileInNewTab(message.attach)"
              />
            </div>

            <!-- Video Message -->
            <div v-else-if="message.content_type === 'video'" class="flex flex-col gap-2">
              <video
                :src="message.attach"
                controls
                class="h-40 cursor-pointer rounded-md"
              />
            </div>

            <!-- Audio Message -->
            <div v-else-if="message.content_type === 'audio'" class="flex items-center gap-2">
              <audio :src="message.attach" controls class="cursor-pointer" />
            </div>

            <!-- Document Message -->
            <div v-else-if="message.content_type === 'file' || message.content_type === 'document'" class="flex items-center gap-2">
              <DocumentIcon
                class="size-10 cursor-pointer rounded-md text-gray-400"
                @click="() => openFileInNewTab(message.attach)"
              />
              <div class="text-gray-500">
                {{ message.message && message.message !== message.attach ? message.message : 'file' }}
              </div>
            </div>
          </div>

          <div class="-mb-1 flex shrink-0 items-end gap-1 text-ink-gray-5">
            <Tooltip :text="formatDate(message.timestamp, 'ddd, MMM D, YYYY')">
              <div class="text-2xs">
                {{ formatDate(message.timestamp, 'hh:mm a') }}
              </div>
            </Tooltip>
            <div v-if="message.message_direction == 'Outgoing'">
              <MessageStatusIcon :status="message.status || 'Sent'" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils'
import { Tooltip } from 'frappe-ui'
import DocumentIcon from '@/components/Icons/DocumentIcon.vue'
import MessageStatusIcon from '@/components/MessageStatusIcon.vue'

const props = defineProps({
  messages: Array,
})

const emit = defineEmits(['reply'])

function formatMessage(message) {
  if (!message) return ''
  message = message.replace(/_(.*?)_/g, '<i>$1</i>')
  message = message.replace(/\*(.*?)\*/g, '<b>$1</b>')
  message = message.replace(/~(.*?)~/g, '<s>$1</s>')
  message = message.replace(/```(.*?)```/g, '<code>$1</code>')
  message = message.replace(/`(.*?)`/g, '<code>$1</code>')
  message = message.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>')
  message = message.replace(/\n/g, '<br>')
  message = message.replace(/\* (.*?)(?=\s*\*|$)/g, '<li>$1</li>')
  message = message.replace(/- (.*?)(?=\s*-|$)/g, '<li>$1</li>')
  message = message.replace(/(\d+)\. (.*?)(?=\s*(\d+)\.|$)/g, '<li>$2</li>')
  return message
}

function openFileInNewTab(url) {
  window.open(url, '_blank')
}
</script>

<style scoped>
/* No date separator styles needed */
</style> 