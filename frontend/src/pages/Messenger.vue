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
      
      <!-- Conversations List with infinite scroll -->
      <div 
        class="flex-1 overflow-y-auto" 
        @scroll="(e) => {
          const el = e.target
          if (el.scrollTop <= 50) {
            loadMoreConversations()
          }
        }"
      >
        <!-- Loading indicator for conversations -->
        <div v-if="conversationsLoading" class="p-4 text-center text-gray-500">
          {{ __('Loading more conversations...') }}
        </div>
        
        <div
          v-for="conversation in conversations"
          :key="conversation.name"
          class="group flex items-center p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
          :class="{ 'bg-gray-50': selectedConversation === conversation.name }"
          @click="handleConversationSelect(conversation)"
        >
          <div class="relative">
            <Avatar
              :label="conversation.title"
              size="md"
              class="flex-shrink-0"
            />
            <!-- Platform Icon -->
            <div class="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5 shadow-sm">
              <component 
                :is="conversation.platform === 'Messenger' ? MessengerIcon : InstagramIcon"
                class="size-3.5 text-ink-gray-6"
              />
            </div>
          </div>
          <div class="ml-3 flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-gray-900 truncate">{{ conversation.title }}</p>
              <div class="flex flex-col items-end gap-0.5">
                <p class="text-xs text-gray-500">{{ formatTime(conversation.last_message_time) }}</p>
                <div
                  v-if="unreadMessageCounts[conversation.name]"
                  class="flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-surface-gray-6 px-1 text-xs font-medium text-white ring-1 ring-white"
                >
                  {{ unreadMessageCounts[conversation.name] }}
                </div>
              </div>
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

      <!-- Messages Area with infinite scroll -->
      <div 
        ref="messagesContainer" 
        class="flex-1 overflow-y-auto p-4"
        @scroll="handleMessagesScroll"
      >
        <!-- Loading indicator for messages -->
        <div v-if="messagesLoading" class="p-4 text-center text-gray-500">
          {{ __('Loading older messages...') }}
        </div>
        
        <!-- Message Component -->
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
import { ref, onMounted, watch, computed, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar, Badge } from 'frappe-ui'
import MessengerArea from '@/components/MessengerArea.vue'
import MessengerBox from '@/components/MessengerBox.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import InstagramIcon from '@/components/Icons/InstagramIcon.vue'
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
const conversationsLoading = ref(false)
const messagesLoading = ref(false)
const conversationPage = ref(0)
const messagePage = ref(0)
const hasMoreConversations = ref(true)
const hasMoreMessages = ref(true)
const unreadMessageCounts = ref({})

// Function to handle ESC key press
function handleEscKey(event) {
  if (event.key === 'Escape' && selectedConversation.value) {
    selectedConversation.value = null
    reply.value = {}
  }
}

// Add event listeners when component is mounted
onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
  fetchUnreadCounts() // Initial fetch of unread counts
})

// Clean up event listeners when component is unmounted
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
  clearInterval(unreadCountsInterval)
})

// Resource for fetching messages
const messagesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
    filters: [],
    order_by: 'timestamp desc',
    limit: 100
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

// Resource for marking messages as read
const markMessagesAsReadResource = createResource({
  url: 'frappe.client.set_value',
  onSuccess: (response) => {
    // Update local unread count
    if (selectedConversation.value) {
      unreadMessageCounts.value[selectedConversation.value] = 0
    }
  }
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

const conversationLimit = computed(() => 20)
const messageLimit = computed(() => 20)

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

// Function to mark messages as read
async function markMessagesAsRead(conversationName) {
  try {
    await markMessagesAsReadResource.submit({
      doctype: 'Messenger Message',
      name: messages.value.find(m => !m.is_read && m.message_direction === 'Incoming')?.name,
      fieldname: 'is_read',
      value: 1
    })
    
    // Reload messages to get updated read status
    await messagesResource.reload()
  } catch (error) {
    console.error('Failed to mark messages as read:', error)
  }
}

// Modify handleConversationSelect to mark messages as read
async function handleConversationSelect(conversation) {
  selectedConversation.value = conversation.name
  
  // Reset message pagination
  messagePage.value = 0
  hasMoreMessages.value = true
  messages.value = []
  
  // First get total count of messages
  const countResource = createResource({
    url: 'frappe.client.get_count',
    params: {
      doctype: 'Messenger Message',
      filters: [['conversation', '=', conversation.name]]
    }
  })
  
  const totalMessages = await countResource.fetch()
  
  // Update message resource params to get latest batch of messages
  messagesResource.params = {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation', 'is_read'],
    filters: [['conversation', '=', conversation.name]],
    order_by: 'timestamp asc',
    limit_start: Math.max(0, totalMessages - messageLimit.value),
    limit_page_length: messageLimit.value
  }
  
  await messagesResource.reload()
  messages.value = messagesResource.data
  
  // Mark messages as read after loading them
  if (unreadMessageCounts.value[conversation.name] > 0) {
    await markMessagesAsRead(conversation.name)
  }
  
  // Set hasMoreMessages based on whether there are older messages
  hasMoreMessages.value = totalMessages > messageLimit.value
  
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

// Modify handleSendMessage to use the scrollToBottom function
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
    
    // Add the new message to the messages array
    messages.value.push({
      ...newMessage,
      name: response.name
    })

    // Update conversation in the list
    const conversationIndex = conversations.value.findIndex(c => c.name === currentConversation.name)
    if (conversationIndex !== -1) {
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        last_message: messageData.message,
        last_message_time: timestamp
      }

      // Re-sort conversations
      conversations.value.sort((a, b) => {
        return new Date(b.last_message_time) - new Date(a.last_message_time)
      })
    }

    // Use the scrollToBottom function
    setTimeout(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }, 100)

    // Refresh conversations list
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

// Add these methods before the existing methods
async function loadMoreConversations() {
  if (!hasMoreConversations.value || conversationsLoading.value) return
  
  conversationsLoading.value = true
  try {
    const nextPage = conversationPage.value + 1
    const response = await createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger Conversation',
        fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform'],
        order_by: 'last_message_time desc',
        limit_start: nextPage * conversationLimit.value,
        limit_page_length: conversationLimit.value
      }
    }).fetch()

    if (response.length < conversationLimit.value) {
      hasMoreConversations.value = false
    }

    // Get user information for new conversations
    const senderIds = [...new Set(response.map(conv => conv.sender_id))]
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
    const newConversations = response.map(conv => ({
      ...conv,
      title: userMap[conv.sender_id] || conv.sender_id
    }))

    conversations.value = [...conversations.value, ...newConversations]
    conversationPage.value = nextPage
  } catch (error) {
    console.error('Failed to load more conversations:', error)
  } finally {
    conversationsLoading.value = false
  }
}

// Modify loadMoreMessages function
async function loadMoreMessages() {
  if (!hasMoreMessages.value || messagesLoading.value || !selectedConversation.value) return
  
  messagesLoading.value = true
  try {
    // Get current first message timestamp
    const firstMessageTimestamp = messages.value[0]?.timestamp

    if (!firstMessageTimestamp) {
      messagesLoading.value = false
      return
    }

    // Fetch older messages before the first displayed message
    const olderMessages = await createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger Message',
        fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
        filters: [
          ['conversation', '=', selectedConversation.value],
          ['timestamp', '<', firstMessageTimestamp]
        ],
        order_by: 'timestamp desc',
        limit_page_length: messageLimit.value
      }
    }).fetch()

    if (olderMessages.length > 0) {
      // Preserve scroll position
      const scrollElement = messagesContainer.value
      const oldScrollHeight = scrollElement.scrollHeight
      const oldScrollTop = scrollElement.scrollTop

      // Add older messages at the beginning
      messages.value = [...olderMessages.reverse(), ...messages.value]

      // Update hasMoreMessages flag
      hasMoreMessages.value = olderMessages.length === messageLimit.value

      // Restore scroll position after DOM update
      setTimeout(() => {
        const newScrollHeight = scrollElement.scrollHeight
        scrollElement.scrollTop = oldScrollTop + (newScrollHeight - oldScrollHeight)
      }, 0)
    } else {
      hasMoreMessages.value = false
    }
  } catch (error) {
    console.error('Failed to load more messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

// Add scroll handler for messages container
function handleMessagesScroll(e) {
  const el = e.target
  // Load more when scrolled near top (threshold of 100px)
  if (el.scrollTop <= 100) {
    loadMoreMessages()
  }
}

// Add function to fetch unread counts
async function fetchUnreadCounts() {
  try {
    const unreadCountsResource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger Message',
        fields: ['conversation', 'count(name) as unread_count'],
        filters: [
          ['message_direction', '=', 'Incoming'],
          ['is_read', '=', 0]
        ],
        group_by: 'conversation'
      }
    })
    
    const counts = await unreadCountsResource.fetch()
    counts.forEach(count => {
      unreadMessageCounts.value[count.conversation] = count.unread_count
    })
  } catch (error) {
    console.error('Failed to fetch unread counts:', error)
  }
}

// Add polling for unread counts
let unreadCountsInterval
onMounted(() => {
  window.addEventListener('keydown', handleEscKey)
  fetchUnreadCounts()
  
  // Poll for unread counts every 30 seconds
  unreadCountsInterval = setInterval(fetchUnreadCounts, 30000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
  clearInterval(unreadCountsInterval)
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