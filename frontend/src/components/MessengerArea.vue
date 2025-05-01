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
          <div
            class="absolute -right-0.5 -top-0.5 flex cursor-pointer gap-1 rounded-full bg-surface-white pb-2 pl-2 pr-1.5 pt-1.5 opacity-0 group-hover/message:opacity-100"
            :style="{
              background:
                'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 1) 0%, rgba(255, 255, 255, 1) 35%, rgba(238, 130, 238, 0) 100%)',
            }"
          >
            <Dropdown :options="messageOptions(message)">
              <FeatherIcon name="chevron-down" class="size-4 text-ink-gray-5" />
            </Dropdown>
          </div>
          
          <!-- Text Message -->
          <div
            v-html="formatMessage(message.message)"
          />

          <div class="-mb-1 flex shrink-0 items-end gap-1 text-ink-gray-5">
            <Tooltip :text="formatDate(message.timestamp, 'ddd, MMM D, YYYY')">
              <div class="text-2xs">
                {{ formatDate(message.timestamp, 'hh:mm a') }}
              </div>
            </Tooltip>
            <div v-if="message.message_direction == 'Outgoing'">
              <CheckIcon class="size-4" />
            </div>
          </div>
        </div>
      </div>
      <div
        class="flex items-center justify-center opacity-0 transition-all ease-in group-hover:opacity-100"
      >
        <Button
          class="rounded-full !size-6 mt-0.5"
        >
          <FeatherIcon name="smile" class="text-ink-gray-3" />
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils'
import { Tooltip, Dropdown, Button } from 'frappe-ui'
import CheckIcon from '@/components/Icons/CheckIcon.vue'

const props = defineProps({
  messages: Array,
})

const emit = defineEmits(['reply'])

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

function messageOptions(message) {
  return [
    {
      label: 'Reply',
      onClick: () => {
        emit('reply', message)
      },
    }
  ]
}
</script> 