<template>
  <div v-if="messengerEnabled" class="flex h-full">
    <!-- Left Column: Conversations List -->
    <div class="w-80 border-r border-gray-200 flex flex-col">
      <div class="p-4 space-y-2 border-b border-gray-200">
        <div class="flex items-center justify-between gap-x-2">
          <h2 class="text-lg font-medium text-gray-900">{{ __('Messages') }}</h2>
          <Button
            appearance="minimal"
            class="text-gray-600 hover:text-gray-900"
            :icon="RefreshIcon"
            @click="conversationsResource.reload()"
          />
        </div>
        <div class="flex items-center gap-2">
          <Dropdown
            :options="platformOptions"
            placement="bottom-start"
            class="w-full"
          >
            <template #default>
              <Button
                appearance="minimal"
                class="min-w-[200px] justify-between text-gray-600 hover:text-gray-900"
                :label="selectedPlatformFilter === 'all' ? __('All') : selectedPlatformFilter"
                :icon-right="ChevronDownIcon"
              />
            </template>
          </Dropdown>
          <Filter
            v-model="list"
            doctype="Messenger Conversation"
            :default_filters="{}"
            @update="updateFilter"
          />
        </div>
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
          v-for="conversation in filteredConversations"
          :key="conversation.name"
          class="group flex items-center p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
          :class="{ 'bg-gray-50': selectedConversation === conversation.name }"
          @click="handleConversationSelect(conversation)"
        >
          <div class="relative">
            <Avatar
              :label="conversation.title"
              :image="conversation.profile"
              size="md"
              class="flex-shrink-0"
            />
            <!-- Platform Icon -->
            <div class="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5 shadow-sm">
              <component 
                :is="getPlatformIcon(conversation.platform)"
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
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <div class="flex items-center">
          <Avatar
            :label="selectedConversationTitle"
            :image="selectedConversationProfile"
            size="md"
            class="flex-shrink-0"
          />
          <div class="ml-3">
            <h3 class="text-base font-medium text-gray-900">{{ selectedConversationTitle }}</h3>
            <p class="text-sm text-gray-500">{{ selectedConversationPlatform }}</p>
          </div>
        </div>
        <AssignTo
          v-if="selectedConversation"
          :data="currentConversation"
          doctype="Messenger Conversation"
          v-model="assignees"
        />
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
import { ref, onMounted, watch, computed, onUnmounted, nextTick, h } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar, Badge, Dropdown } from 'frappe-ui'
import ChevronDownIcon from '@/components/Icons/ChevronDownIcon.vue'
import MessengerArea from '@/components/MessengerArea.vue'
import MessengerBox from '@/components/MessengerBox.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import InstagramIcon from '@/components/Icons/InstagramIcon.vue'
import WhatsAppIcon from '../components/Icons/WhatsAppIcon.vue'
import ChatIcon from '@/components/Icons/ChatIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import EmojiIcon from '@/components/Icons/EmojiIcon.vue'
import SendIcon from '@/components/Icons/SendIcon.vue'
import { messengerEnabled } from '@/composables/settings'
import { globalStore } from '@/stores/global'
import AssignTo from '@/components/AssignTo.vue'
import { call } from 'frappe-ui'
import Filter from '@/components/Filter.vue'

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
const userProfiles = ref({})
const selectedPlatformFilter = ref('all')
const assignees = ref([])

const { $socket } = globalStore()

// Add filter functionality
const list = ref(null)

// Add a computed property to track current filters
const currentFilters = computed(() => {
  return conversationsResource.params?.filters || {}
})

function updateFilter(filters) {
  // console.log("update clicked ... ")
  // console.log("updateFilter", filters)
  
  // Update conversations resource params with new filters
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform'],
    order_by: 'last_message_time desc',
    filters: {
      ...filters
    }
  }
  
  // Initialize list model if not already initialized
  if (!list.value) {
    list.value = {
      data: {
        params: {
          doctype: 'Messenger Conversation',
          filters: filters
        }
      },
      params: {
        doctype: 'Messenger Conversation',
        filters: filters
      }
    }
  } else {
    // Update existing list model
    list.value.data.params.filters = filters
    list.value.params.filters = filters
  }
  
  console.log("conversationsResource.params", conversationsResource.params)
  conversationsResource.reload()
}

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
  
  // Listen for messenger message updates
  $socket.on('messenger:message_update', (data) => {
    if (data.conversation_id === selectedConversation.value) {
      // Add new message to messages array
      if (data.type === 'new') {
        // For file type messages, only add if attachment exists
        if (['image', 'video', 'audio', 'document'].includes(data.message.content_type)) {
          if (data.message.attach) {
            // If message already exists, update it
            const existingIndex = messages.value.findIndex(m => m.name === data.message.name)
            if (existingIndex !== -1) {
              messages.value[existingIndex] = data.message
            } else {
              messages.value.push(data.message)
            }
          }
        } else {
          // For text messages, add normally
          messages.value.push(data.message)
        }
        
        // Scroll to bottom after new message
        setTimeout(() => {
          if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
          }
        }, 100)
      }
    }
  })

  // Listen for conversation updates
  $socket.on('messenger:conversation_update', (data) => {
    console.log("Conversation update", data)
    if (data.type === 'update') {
      // Update conversation in list
      const index = conversations.value.findIndex(c => c.name === data.conversation.name)
      if (index !== -1) {
        // Fetch updated user profile if needed
        if (data.conversation.sender_id && !userProfiles.value[data.conversation.sender_id]) {
          fetchUserProfile(data.conversation.sender_id)
        }
        
        conversations.value[index] = {
          ...conversations.value[index],
          ...data.conversation,
          profile: userProfiles.value[data.conversation.sender_id]?.profile || null
        }
        // Re-sort conversations by last message time
        conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
      }else{
        
          fetchUserProfile(data.conversation.sender_id).then(() => {
            const newConversation = {
              ...data.conversation,
              title: userProfiles.value[data.conversation.sender_id]?.username || data.conversation.sender_id,
              profile: userProfiles.value[data.conversation.sender_id]?.profile || null
            }
            
            conversations.value = [
              newConversation,
              ...conversations.value
            ].sort((a, b) => 
              new Date(b.last_message_time) - new Date(a.last_message_time)
            )
            
            // Immediately check unread counts for new conversation
            fetchUnreadCounts()
          })
          }
        }
      
  })

  // Listen for unread count updates
  $socket.on('messenger:unread_update', (data) => {
    if (data.conversation_id) {
      unreadMessageCounts.value[data.conversation_id] = data.unread_count
    }
  })
  
  // Listen for message status updates
  $socket.on('messenger:message_status_update', (data) => {
    console.log("Message status update", data)
    if (data.message_id) {
      // Find and update the message status
      const messageIndex = messages.value.findIndex(m => m.name === data.name)
      if (messageIndex !== -1) {
        messages.value[messageIndex].status = data.status
      }else{
        console.warn("Message not found for ID:", data.name);
      }
    }
  })
})

// Clean up event listeners when component is unmounted
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
  clearInterval(unreadCountsInterval)
  $socket.off('messenger:message_update')
  $socket.off('messenger:conversation_update')
  $socket.off('messenger:unread_update')
  $socket.off('messenger:message_status_update')
})

// Add platform resource
const platformsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Platform',
    fields: ['platform'],
    order_by: 'platform asc'
  },
  onSuccess: (data) => {

    // Update platform options with backend data
    platformOptions.value = [
      { 
        label: __('All'), 
        value: 'all',
        onClick: () => handlePlatformSelect('all'),
        icon: ChatIcon
      },
      ...data.map(platform => ({
        label: platform.platform,
        value: platform.platform,
        onClick: () => handlePlatformSelect(platform.platform),
        icon: getPlatformIcon(platform.platform)
      }))
    ]
  },
  auto: true
})

// Update platform options to be reactive
const platformOptions = ref([
  { 
    label: __('All'), 
    value: 'all',
    onClick: () => handlePlatformSelect('all'),
    icon: ChatIcon
  }
])

// Update getPlatformIcon function to handle more platforms
function getPlatformIcon(platform) {
  switch (platform?.toLowerCase()) {
    case 'messenger':
      return MessengerIcon
    case 'instagram':
      return InstagramIcon
    case 'whatsapp':
      return WhatsAppIcon
    default:
      return ChatIcon
  }
}

// Update platform selection handler
function handlePlatformSelect(platform) {
  // Update the filter value
  selectedPlatformFilter.value = platform
  
  // Reset conversations
  conversationPage.value = 0
  conversations.value = []
  
  // Update resource params with platform filter
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform'],
    order_by: 'last_message_time desc',
    filters: platform !== 'all' ? [['platform', '=', platform]] : []
  }
  
  // Force reload conversations
  conversationsResource.reload()
}

// Update filtered conversations computed
const filteredConversations = computed(() => {

  if (selectedPlatformFilter.value === 'all') {
    return conversations.value
  }
  
  const filtered = conversations.value.filter(conv => {
    const matches = conv.platform?.toLowerCase() === selectedPlatformFilter.value.toLowerCase()
    return matches
  })
  

  return filtered
})

// Update conversations resource
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
    
    // Fetch user information
    const usersResource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger User',
        fields: ['user_id', 'username', 'profile'],
        filters: [['user_id', 'in', senderIds]]
      }
    })
    
    const users = await usersResource.fetch()
    const userMap = {}
    users.forEach(user => {
      userMap[user.user_id] = user
      userProfiles.value[user.user_id] = user
    })
    
    // Update conversations
    conversations.value = data.map(conv => ({
      ...conv,
      title: userMap[conv.sender_id]?.username || conv.sender_id,
      profile: userMap[conv.sender_id]?.profile || null
    }))

    // Update list model with current filters
    if (list.value) {
      list.value.data.params.filters = conversationsResource.params.filters
      list.value.params.filters = conversationsResource.params.filters
    }
  },
  auto: true
})

// Resource for fetching messages
const messagesResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Message',
    fields: [
      'name',
      'message',
      'sender_id',
      'sender_user',
      'timestamp',
      'message_direction',
      'conversation',
      'is_read',
      'content_type',
      'attach',
      'status'
    ],
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

// Resource for marking messages as read
const markMessagesAsReadResource = createResource({
  url: 'frappe_messenger.frappe_messenger.doctype.messenger_message.messenger_message.mark_messages_as_read',
  onSuccess: (response) => {
    // Update local unread count
    if (selectedConversation.value) {
      unreadMessageCounts.value[selectedConversation.value] = response || 0
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
  if (!conversation?.platform) return ''
  
  switch (conversation.platform) {
    case 'Messenger':
      return 'Facebook Messenger'
    case 'Instagram':
      return 'Instagram DM'
    default:
      return `${conversation.platform} DM`
  }
})

const selectedConversationProfile = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.profile || null
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

// Function to fetch unread counts for all conversations
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
    // Reset all counts first
    conversations.value.forEach(conv => {
      unreadMessageCounts.value[conv.name] = 0
    })
    // Then update with new counts
    counts.forEach(count => {
      unreadMessageCounts.value[count.conversation] = count.unread_count
    })
  } catch (error) {
    console.error('Failed to fetch unread counts:', error)
  }
}

// Function to mark messages as read
async function markMessagesAsRead(conversationName) {
  try {
    await markMessagesAsReadResource.submit({
      conversation: conversationName
    })
  } catch (error) {
    console.error('Failed to mark messages as read:', error)
  }
}

// Add function to handle assignment changes
async function handleAssignmentChange(newAssignees) {
  if (!selectedConversation.value || !currentConversation.value) return
  
  try {
    // Get the new assignee (we only support single assignment for now)
    const newAssignee = newAssignees[0]?.name
    
    // Update local state
    assignees.value = newAssignees
    
    // Update conversation in the list
    const conversationIndex = conversations.value.findIndex(c => c.name === selectedConversation.value)
    if (conversationIndex !== -1) {
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        assignees: newAssignees
      }
    }
  } catch (error) {
    console.error('Failed to assign conversation:', error)
  }
}



// Add function to get current conversation details
function getCurrentConversation() {
  if (!selectedConversation.value) return null
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  if (!conversation) return null
  
  return {
    name: conversation.name,
    title: conversation.title,
    platform: conversation.platform,
    sender_id: conversation.sender_id,
    last_message: conversation.last_message,
    last_message_time: conversation.last_message_time,
    profile: conversation.profile
  }
}

// Add computed property for current conversation
const currentConversation = computed(() => getCurrentConversation())

// Modify handleConversationSelect to properly set up conversation data
async function handleConversationSelect(conversation) {
  selectedConversation.value = conversation.name
  
  // Reset message pagination
  messagePage.value = 0
  hasMoreMessages.value = true
  messages.value = []
  
  // Fetch assignees for the conversation
  try {
  const assigneesResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'ToDo',
      fields: ['allocated_to'],
      filters: [
        ['reference_type', '=', 'Messenger Conversation'],
        ['reference_name', '=', conversation.name],
        ['status', '=', 'Open']
      ]
    }
  })

  const assigneesList = await assigneesResource.fetch()

  // Extract unique user IDs
  const userIds = [...new Set(assigneesList.map(a => a.allocated_to))]

  // Fetch full names from the User doctype
  const userDetailsResource  = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'User',
      fields: ['name', 'full_name'],
      filters: [['name', 'in', userIds]]
    }
  })
  const userDetails = await userDetailsResource.fetch()

  const userMap = Object.fromEntries(
    userDetails.map(user => [user.name, user.full_name])
  )

  assignees.value = assigneesList.map(a => ({
    name: a.allocated_to,
    image: null,
    label: userMap[a.allocated_to] || a.allocated_to
  }))
} catch (error) {
  console.error('Failed to fetch assignees:', error)
}

  
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
    fields: [
      'name',
      'message',
      'sender_id',
      'sender_user',
      'timestamp',
      'message_direction',
      'conversation',
      'is_read',
      'content_type',
      'attach',
      'status'
    ],
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
    content_type: messageData.content_type || 'text',
    attach: messageData.attach || '',
    reply_to: messageData.reply_to || '',
    status: 'Sent' // Add initial status
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

    // Scroll to bottom
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
        limit_page_length: conversationLimit.value,
        filters: selectedPlatformFilter.value !== 'all' ? 
          [['platform', '=', selectedPlatformFilter.value]] : []
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

// Modify loadMoreMessages to handle unread messages in infinite scroll
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
        fields: [
          'name',
          'message',
          'sender_id',
          'sender_user',
          'timestamp',
          'message_direction',
          'conversation',
          'is_read',
          'content_type',
          'attach'
        ],
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

// Add watcher for conversation refresh
watch(() => conversationsResource.data, async () => {
  await fetchUnreadCounts()
}, { deep: true })

// Add function to fetch user profile
async function fetchUserProfile(userId) {
  if (userProfiles.value[userId]) return userProfiles.value[userId]
  
  try {
    const userResource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger User',
        fields: ['user_id', 'username', 'profile'],
        filters: [['user_id', '=', userId]],
        limit: 1
      }
    })
    
    const users = await userResource.fetch()
    if (users.length > 0) {
      userProfiles.value[userId] = users[0]
      return users[0]
    }
    return null
  } catch (error) {
    console.error('Failed to fetch user profile:', error)
    return null
  }
}

// Add watcher for assignees changes
watch(assignees, handleAssignmentChange)

// Add a watcher to keep list and conversationsResource in sync
watch(() => conversationsResource.params.filters, (newFilters) => {
  if (list.value) {
    list.value.data.params.filters = newFilters
    list.value.params.filters = newFilters
  }
}, { deep: true })

// Add debug watch for filtered conversations

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