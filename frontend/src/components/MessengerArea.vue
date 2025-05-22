<template>
  <div>
    <template v-for="(messageGroup, date) in groupedMessages" :key="date">
      <!-- Date Separator -->
      <div class="flex items-center justify-center my-4">
        <div class="px-4 py-1 rounded-full bg-surface-gray-2 text-xs text-ink-gray-6 font-medium">
          {{ formatMessageDate(date) }}
        </div>
      </div>

      <!-- Messages for this date -->
      <div
        v-for="message in messageGroup"
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
              <div v-if="!message.content_type || message.content_type === 'text'"
                v-html="formatMessage(message.message)"
              />

              <!-- Image Message -->
              <div v-else-if="message.content_type === 'image'" class="flex flex-col gap-2">
                <img
                  :src="message.attach"
                  class="h-40 cursor-pointer rounded-md"
                  @click="() => openFileInNewTab(message.attach)"
                />
                <!-- <div v-if="message.message && message.message !== message.attach" 
                  v-html="formatMessage(message.message)"
                /> -->
              </div>

              <!-- Video Message -->
              <div v-else-if="message.content_type === 'video'" class="flex flex-col gap-2">
                <video
                  :src="message.attach"
                  controls
                  class="h-40 cursor-pointer rounded-md"
                />
                <!-- <div v-if="message.message && message.message !== message.attach"
                  v-html="formatMessage(message.message)"
                /> -->
              </div>

              <!-- Audio Message -->
              <div v-else-if="message.content_type === 'audio'" class="flex items-center gap-2">
                <audio :src="message.attach" controls class="cursor-pointer" />
                <!-- <div v-if="message.message && message.message !== message.attach"
                  v-html="formatMessage(message.message)"
                  class="ml-2"
                /> -->
              </div>

              <!-- Document Message -->
              <div v-else-if="message.content_type === 'file'" class="flex items-center gap-2">
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
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { formatDate } from '@/utils'
import { Tooltip } from 'frappe-ui'
import CheckIcon from '@/components/Icons/CheckIcon.vue'
import DocumentIcon from '@/components/Icons/DocumentIcon.vue'
import MessageStatusIcon from '@/components/MessageStatusIcon.vue'

const props = defineProps({
  messages: Array,
})

const emit = defineEmits(['reply'])

// Group messages by date
const groupedMessages = computed(() => {
  if (!props.messages) return {}
  
  const groups = {}
  props.messages.forEach(message => {
    const date = new Date(message.timestamp).toDateString()
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(message)
  })
  return groups
})

// Format the date header
function formatMessageDate(dateStr) {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return 'Today'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday'
  } else if (today.getFullYear() === date.getFullYear()) {
    // If same year, show date without year
    return formatDate(date, 'MMMM D')
  } else {
    // If different year, include the year
    return formatDate(date, 'MMMM D, YYYY')
  }
}

function formatMessage(message) {
  if (!message) return ''
  
  // if message contains _text_, make it italic
  message = message.replace(/_(.*?)_/g, '<i>$1</i>')
  // if message contains *text*, make it bold
  message = message.replace(/\*(.*?)\*/g, '<b>$1</b>')
  // if message contains ~text~, make it strikethrough
  message = message.replace(/~(.*?)~/g, '<s>$1</s>')
  // if message contains ```text```, make it monospace
  message = message.replace(/```(.*?)```/g, '<code>$1</code>')
  // if message contains `text`, make it inline code
  message = message.replace(/`(.*?)`/g, '<code>$1</code>')
  // if message contains > text, make it a blockquote
  message = message.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>')
  // if contain /n, make it a new line
  message = message.replace(/\n/g, '<br>')
  // if contains *<space>text, make it a bullet point
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
/* Add subtle fade effect to date separator */
.date-separator {
  position: relative;
}
.date-separator::before,
.date-separator::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30px;
  height: 1px;
  background: linear-gradient(to right, transparent, currentColor);
}
.date-separator::before {
  right: 100%;
}
.date-separator::after {
  left: 100%;
}
</style> 