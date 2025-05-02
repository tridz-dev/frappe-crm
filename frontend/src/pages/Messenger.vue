<template>
  <div v-if="messengerEnabled" class="flex h-full">
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
          @click="handleConversationSelect(conversation)"
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
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4">
        <MessengerArea 
          :messages="messages"
          @reply="handleReply"
        />
      </div>

      <!-- Message Input -->
      <MessengerBox
        :conversation="selectedConversation"
        v-model:reply="reply"
        @send="handleSendMessage"
      />
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
  <div v-else class="flex h-full items-center justify-center">
    <div class="text-center">
      <MessengerIcon class="mx-auto h-12 w-12 text-gray-400" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">{{ __('Messenger not available') }}</h3>
      <p class="mt-1 text-sm text-gray-500">
        {{ __('Please ensure Messenger is enabled in Messenger Settings.') }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar } from 'frappe-ui'
import MessengerArea from '@/components/MessengerArea.vue'
import MessengerBox from '@/components/MessengerBox.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import EmojiIcon from '@/components/Icons/EmojiIcon.vue'
import SendIcon from '@/components/Icons/SendIcon.vue'
import { messengerEnabled } from '@/composables/settings'

// State management
const messages = ref([])
const conversations = ref([])
const selectedConversation = ref(null)
const messagesContainer = ref(null)
const reply = ref({})

// Resource for fetching messages
const messagesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
    filters: [],
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
    messagesResource.reload()
  }
})

// Resource for fetching conversations
const conversationsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform'],
    order_by: 'last_message_time desc'
  },
  onSuccess: async (data) => {
    // Get unique sender IDs
    const senderIds = [...new Set(data.map(conv => conv.sender_id))]
    
    // Fetch user information for all senders
    const usersResource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger User',
        fields: ['user_id', 'username'],
        filters: [['user_id', 'in', senderIds]]
      }
    })
    
    const users = await usersResource.fetch()
    const userMap = {}
    users.forEach(user => {
      userMap[user.user_id] = user.username
    })
    
    // Map conversations with user information
    conversations.value = data.map(conv => ({
      ...conv,
      title: userMap[conv.sender_id] || conv.sender_id // Fallback to sender_id if username not found
    }))
  },
  auto: true
})

// Computed properties
const selectedConversationTitle = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.title || ''
})

const selectedConversationPlatform = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.platform === 'Messenger' ? 'Facebook Messenger' : 'Instagram DM'
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

// Function to handle conversation selection
async function handleConversationSelect(conversation) {
  selectedConversation.value = conversation.name
  
  // Update message resource params and fetch messages
  messagesResource.params = {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
    filters: [['conversation', '=', conversation.name]],
    order_by: 'timestamp desc',
    limit: 50
  }
  
  await messagesResource.reload()
  messages.value = messagesResource.data.reverse() // Show oldest messages first
  
  // Scroll to bottom after messages load
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 100)
}

// Function to get current conversation details
function getCurrentConversation() {
  return conversations.value.find(c => c.name === selectedConversation.value)
}

// Handle sending messages
async function handleSendMessage(messageData) {
  const currentConversation = getCurrentConversation()
  if (!currentConversation) return

  // Format timestamp to match Frappe's datetime format (YYYY-MM-DD HH:mm:ss)
  const now = new Date()
  const timestamp = now.getFullYear() + '-' + 
    String(now.getMonth() + 1).padStart(2, '0') + '-' +
    String(now.getDate()).padStart(2, '0') + ' ' +
    String(now.getHours()).padStart(2, '0') + ':' +
    String(now.getMinutes()).padStart(2, '0') + ':' +
    String(now.getSeconds()).padStart(2, '0')

  const newMessage = {
    doctype: 'Messenger Message',
    message: messageData.message,
    conversation: messageData.conversation,
    message_direction: 'Outgoing',
    recipient_id: currentConversation.sender_id,
    timestamp: timestamp,
    reply_to: messageData.reply_to || ''
  }

  try {
    const response = await sendMessageResource.submit({
      doc: newMessage
    })
    
    // Add the new message to the messages array with the returned name
    messages.value.push({
      ...newMessage,
      name: response.name
    })

    // Update the conversation in the list with new last message
    const conversationIndex = conversations.value.findIndex(c => c.name === currentConversation.name)
    if (conversationIndex !== -1) {
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        last_message: messageData.message,
        last_message_time: timestamp
      }

      // Re-sort conversations to move this one to top
      conversations.value.sort((a, b) => {
        return new Date(b.last_message_time) - new Date(a.last_message_time)
      })
    }

    // Scroll to bottom after adding new message
    setTimeout(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }, 100)

    // Also refresh conversations list from server to ensure sync
    conversationsResource.reload()
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

// Watch for conversation changes
watch(selectedConversation, async (newVal) => {
  if (newVal) {
    await messagesResource.reload()
  }
})

// Handle message reply
function handleReply(message) {
  reply.value = message
}

// Only fetch conversations if messenger is enabled
watch(messengerEnabled, (enabled) => {
  if (enabled) {
    conversationsResource.fetch()
  }
})
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