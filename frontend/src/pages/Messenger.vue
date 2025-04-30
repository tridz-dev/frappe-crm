<template>
  <div class="flex h-full">
    <!-- Left Column: Conversations List -->
    <div class="w-80 border-r border-gray-200 flex flex-col">
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">{{ __('Messages') }}</h2>
        <Button
          appearance="minimal"
          class="text-gray-600 hover:text-gray-900"
          :icon="RefreshIcon"
          @click="conversationsResource.reload()"
        />
      </div>
      
      <!-- Conversations List -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-for="conversation in conversations"
          :key="conversation.name"
          class="group flex items-center p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
          :class="{ 'bg-gray-50': selectedConversation === conversation.name }"
          @click="selectedConversation = conversation.name"
        >
          <Avatar
            :label="conversation.title"
            size="md"
            class="flex-shrink-0"
          />
          <div class="ml-3 flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-gray-900 truncate">{{ conversation.title }}</p>
              <p class="text-xs text-gray-500">{{ formatTime(conversation.last_message_time) }}</p>
            </div>
            <p class="text-sm text-gray-500 truncate">
              {{ conversation.last_message }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column: Chat View -->
    <div class="flex-1 flex flex-col bg-white" v-if="selectedConversation">
      <!-- Chat Header -->
      <div class="flex items-center p-4 border-b border-gray-200">
        <Avatar
          :label="selectedConversationTitle"
          size="md"
          class="flex-shrink-0"
        />
        <div class="ml-3">
          <h3 class="text-base font-medium text-gray-900">{{ selectedConversationTitle }}</h3>
          <p class="text-sm text-gray-500">{{ selectedConversationPlatform }}</p>
        </div>
      </div>

      <!-- Messages Area -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-for="message in messages" :key="message.name" class="flex flex-col space-y-1">
          <!-- Received message -->
          <div v-if="message.message_direction === 'Incoming'" class="flex items-end space-x-2">
            <Avatar
              :label="message.sender_user || message.sender_id"
              size="sm"
              class="flex-shrink-0"
            />
            <div class="flex flex-col">
              <div class="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-2 max-w-[70%]">
                <p class="text-sm text-gray-900">{{ message.message }}</p>
              </div>
              <span class="text-xs text-gray-500 ml-2 mt-1">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>

          <!-- Sent message -->
          <div v-else class="flex items-end justify-end space-x-2">
            <div class="flex flex-col items-end">
              <div class="bg-blue-500 text-white rounded-2xl rounded-br-none px-4 py-2 max-w-[70%]">
                <p class="text-sm">{{ message.message }}</p>
              </div>
              <span class="text-xs text-gray-500 mr-2 mt-1">{{ formatTime(message.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Input -->
      <div class="p-4 border-t border-gray-200">
        <div class="flex items-center space-x-2">
          <Button
            appearance="minimal"
            :icon="EmojiIcon"
            class="text-gray-500 hover:text-gray-700"
          />
          <Input
            v-model="newMessage"
            type="text"
            placeholder="Type a message..."
            class="flex-1"
            @keyup.enter="sendMessage"
          />
          <Button
            appearance="primary"
            :icon="SendIcon"
            :disabled="!newMessage.trim()"
            @click="sendMessage"
          />
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex-1 grid place-items-center bg-gray-50">
      <div class="text-center">
        <div class="mx-auto h-12 w-12 text-gray-400">
          <MessengerIcon />
        </div>
        <h3 class="mt-2 text-sm font-medium text-gray-900">{{ __('No conversation selected') }}</h3>
        <p class="mt-1 text-sm text-gray-500">{{ __('Choose a conversation to start messaging') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar } from 'frappe-ui'
// import { __ } from 'frappe-ui/utils'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import EmojiIcon from '@/components/Icons/EmojiIcon.vue'
import SendIcon from '@/components/Icons/SendIcon.vue'

// State management
const messages = ref([])
const newMessage = ref('')
const conversations = ref([])
const selectedConversation = ref(null)
const messagesContainer = ref(null)

// Computed properties
const selectedConversationTitle = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.title || ''
})

const selectedConversationPlatform = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.platform === 'facebook' ? 'Facebook Messenger' : 'Instagram DM'
})

// Resource for fetching messages
const messagesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
    filters: { conversation: selectedConversation },
    order_by: 'timestamp desc',
    limit: 50
  },
  auto: false
})

// Resource for sending messages
const sendMessageResource = createResource({
  url: 'frappe.client.insert',
  method: 'POST',
  onSuccess: () => {
    newMessage.value = ''
    messagesResource.reload()
  }
})

// Resource for fetching conversations
const conversationsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Conversation',
    fields: ['name', 'last_message', 'last_message_time', 'platform'],
    order_by: 'last_message_time desc'
  },
  auto: true
})

// Format timestamp
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date

  // If less than 24 hours ago, show time
  if (diff < 24 * 60 * 60 * 1000) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  // If this year, show date without year
  if (date.getFullYear() === now.getFullYear()) {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
  // Otherwise show full date
  return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })
}

// Load conversations and messages
onMounted(async () => {
  await conversationsResource.fetch()
  conversations.value = conversationsResource.data || []
})

// Watch for conversation changes
watch(selectedConversation, async (newVal) => {
  if (newVal) {
    await messagesResource.fetch()
    messages.value = messagesResource.data || []
    // Scroll to bottom after messages load
    setTimeout(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }, 100)
  }
})

// Send message function
const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedConversation.value) return

  await sendMessageResource.submit({
    doc: {
      doctype: 'Messenger Message',
      message: newMessage.value,
      conversation: selectedConversation.value,
      message_direction: 'Outgoing',
      timestamp: new Date().toISOString()
    }
  })
}
</script>

<style scoped>
/* Custom scrollbar styling */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: #E5E7EB transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #E5E7EB;
  border-radius: 3px;
}
</style> 