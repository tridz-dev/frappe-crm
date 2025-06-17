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
                <p class="text-xs text-gray-500">{{ formatTimeAgo(conversation.last_message_time) }}</p>
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
            <div class="flex items-center gap-2">
              <p class="text-sm text-gray-500">{{ selectedConversationPlatform }}</p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Dropdown
            :options="statusOptions"
            placement="bottom-start"
            @select="handleStatusChange"
          >
            <template #default>
              <Button
                appearance="minimal"
                class="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-900 border border-gray-200 rounded-md px-3 py-1.5"
                :label="currentStatus"
                :icon-right="ChevronDownIcon"
              />
            </template>
          </Dropdown>
          <AssignTo
            v-if="selectedConversation"
            :data="currentConversation"
            doctype="Messenger Conversation"
            v-model="assignees"
          />
          <Dropdown :options="conversationMenuOptions" placement="bottom-end">
            <template #default>
              <Button
                appearance="minimal"
                class="text-gray-600 hover:text-gray-900"
                :icon="MoreVerticalIcon"
              />
            </template>
          </Dropdown>
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
        
        <!-- Messages and Status Updates -->
        <template v-if="Object.keys(groupedTimeline).length > 0">
          <div v-for="(items, dateKey) in groupedTimeline" :key="dateKey">
            <!-- Date Header -->
            <div class="flex justify-center my-4">
              <div class="bg-gray-100 rounded-full px-4 py-1 text-sm text-gray-600">
                {{ formatDate(items[0].timestamp) }}
              </div>
            </div>
            <!-- Items for this date -->
            <div v-for="item in items" :key="item.type === 'message' ? item.name : `status-${item.changed_on}`">
              <!-- Status Update Info Block -->
              <div v-if="item.type === 'status'" class="flex justify-center my-4">
                <div class="bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 text-sm">
                  <div class="flex items-center gap-2">
                    <component 
                      :is="getStatusIcon(item.status)"
                      :class="getStatusColor(item.status)"
                    />
                    <span class="text-gray-600">{{ __('Status changed to') }}</span>
                    <span class="font-medium text-gray-700">{{ item.status }}</span>
                    <span class="text-gray-600">{{ __('by') }}</span>
                    <span class="font-medium text-gray-700">{{ item.changed_by }}</span>
                  </div>
                </div>
              </div>
              <!-- Message -->
              <MessengerArea 
                v-else-if="item.type === 'message'"
                :messages="[item]"
                @reply="handleReply"
              />
            </div>
          </div>
        </template>
        
        <!-- Empty state -->
        <div v-else class="flex items-center justify-center h-full">
          <div class="text-center text-gray-500">
            {{ __('No messages yet') }}
          </div>
        </div>
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
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar, Badge, Dropdown } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
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
import MoreVerticalIcon from '@/components/Icons/MoreVerticalIcon.vue'
import StatusIcon from '@/components/Icons/StatusIcon.vue'
import CheckCircleIcon from '@/components/Icons/CheckCircleIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'

const router = useRouter()
const route = useRoute()
const { $socket } = globalStore()

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
const statusOptions = ref([])
const currentStatus = ref('')

// Add filter functionality
const list = ref(null)

// Add a computed property to track current filters
const currentFilters = computed(() => {
  return conversationsResource.params?.filters || {}
})

function updateFilter(filters) {
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat','status'],
    order_by: 'last_message_time desc',
    filters: {
      ...filters
    }
  }
  
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
    list.value.data.params.filters = filters
    list.value.params.filters = filters
  }
  
  conversationsResource.reload()
}

// Add platform resource
const platformsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Platform',
    fields: ['platform'],
    order_by: 'platform asc'
  },
  onSuccess: (data) => {
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
  selectedPlatformFilter.value = platform
  conversationPage.value = 0
  conversations.value = []
  
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform','status'],
    order_by: 'last_message_time desc',
    filters: platform !== 'all' ? [['platform', '=', platform]] : []
  }
  
  conversationsResource.reload()
}

// Update filtered conversations computed
const filteredConversations = computed(() => {
  if (selectedPlatformFilter.value === 'all') {
    return conversations.value
  }
  
  return conversations.value.filter(conv => {
    return conv.platform?.toLowerCase() === selectedPlatformFilter.value.toLowerCase()
  })
})

// Update conversations resource
const conversationsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat','status'],
    order_by: 'last_message_time desc',
    filters: [['block_chat', '=', 0]]
  },
  onSuccess: async (data) => {
    const senderIds = [...new Set(data.map(conv => conv.sender_id))]
    
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
    
    conversations.value = data.map(conv => ({
      ...conv,
      title: userMap[conv.sender_id]?.username || conv.sender_id,
      profile: userMap[conv.sender_id]?.profile || null
    }))

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

// Add formatTimeAgo function
function formatTimeAgo(timestamp) {
  if (!timestamp) return ''
  
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  const seconds = Math.floor(diff / 1000)
  
  if (seconds < 60) {
    return __('Just now')
  }
  
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) {
    return minutes === 1 ? __('1 minute ago') : __('{0} minutes ago', [minutes])
  }
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) {
    return hours === 1 ? __('1 hour ago') : __('{0} hours ago', [hours])
  }
  
  const days = Math.floor(hours / 24)
  if (days < 7) {
    return days === 1 ? __('1 day ago') : __('{0} days ago', [days])
  }
  
  const weeks = Math.floor(days / 7)
  if (weeks < 4) {
    return weeks === 1 ? __('1 week ago') : __('{0} weeks ago', [weeks])
  }
  
  const months = Math.floor(days / 30)
  if (months < 12) {
    return months === 1 ? __('1 month ago') : __('{0} months ago', [months])
  }
  
  const years = Math.floor(months / 12)
  return years === 1 ? __('1 year ago') : __('{0} years ago', [years])
}

// Function to fetch unread counts
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
    conversations.value.forEach(conv => {
      unreadMessageCounts.value[conv.name] = 0
    })
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
    const newAssignee = newAssignees[0]?.name
    assignees.value = newAssignees
    
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

// Add these refs after existing refs
const statusUpdates = ref([])

// Replace statusLogResource definition
const statusLogResource = createResource({
  url: 'frappe.client.get',
  params: {
    doctype: 'Messenger Conversation',
    name: '', // will be set dynamically
    fields: ['status_log']
  },
  auto: false
})

// Update handleConversationSelect to fetch status_log from parent doc
async function handleConversationSelect(conversation) {
  if (!conversation) return
  
  selectedConversation.value = conversation.name
  currentStatus.value = conversation.status || ''
  
  // Reset messages and status updates
  messages.value = []
  statusUpdates.value = []
  
  // Fetch status logs from parent doc
  try {
    if (!statusLogResource.params) {
      statusLogResource.params = {
        doctype: 'Messenger Conversation',
        name: conversation.name,
        fields: ['status_log']
      }
    } else {
      statusLogResource.params.name = conversation.name
    }
    await statusLogResource.fetch()
    statusUpdates.value = statusLogResource.data.status_log || []
  } catch (error) {
    console.error('Failed to fetch status logs:', error)
  }
  
  // Reset message pagination
  messagePage.value = 0
  hasMoreMessages.value = true
  
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

    const userIds = [...new Set(assigneesList.map(a => a.allocated_to))]

    const userDetailsResource = createResource({
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
    status: 'Sent'
  }

  try {
    const response = await sendMessageResource.submit({
      doc: newMessage
    })
    
    messages.value.push({
      ...newMessage,
      name: response.name
    })

    const conversationIndex = conversations.value.findIndex(c => c.name === currentConversation.name)
    if (conversationIndex !== -1) {
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        last_message: messageData.message,
        last_message_time: timestamp
      }

      conversations.value.sort((a, b) => {
        return new Date(b.last_message_time) - new Date(a.last_message_time)
      })
    }

    setTimeout(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    }, 100)

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
        fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform','status'],
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
    const firstMessageTimestamp = messages.value[0]?.timestamp

    if (!firstMessageTimestamp) {
      messagesLoading.value = false
      return
    }

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
      const scrollElement = messagesContainer.value
      const oldScrollHeight = scrollElement.scrollHeight
      const oldScrollTop = scrollElement.scrollTop

      messages.value = [...olderMessages.reverse(), ...messages.value]

      hasMoreMessages.value = olderMessages.length === messageLimit.value

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

// Add conversation menu options
const conversationMenuOptions = computed(() => [
  {
    label: __('View Lead'),
    icon: 'user',
    onClick: () => handleViewLead()
  },
  {
    label: __('Block Chat'),
    icon: 'ban',
    onClick: () => handleBlockChat()
  }
])

// Add menu action handlers
async function handleViewLead() {
  if (!selectedConversation.value) return
  
  try {
    const referenceResource = createResource({
      url: 'frappe.client.get',
      params: {
        doctype: 'Messenger Conversation',
        name: selectedConversation.value,
        fields: ['reference_doctype', 'reference_name']
      }
    })
    
    const conversation = await referenceResource.fetch()
    
    if (conversation.reference_doctype === 'CRM Lead' && conversation.reference_name) {
      router.push({
        name: 'Lead',
        params: { leadId: conversation.reference_name },
        hash: '#data'
      })
    } else {
      globalStore().$toast.error(__('No lead found for this conversation'))
    }
  } catch (error) {
    console.error('Failed to fetch lead:', error)
    globalStore().$toast.error(__('Failed to fetch lead information'))
  }
}

async function handleBlockChat() {
  if (!selectedConversation.value) return
  
  try {
    await createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'Messenger Conversation',
        name: selectedConversation.value,
        fieldname: 'block_chat',
        value: 1
      }
    }).submit()
    
    conversations.value = conversations.value.filter(c => c.name !== selectedConversation.value)
    selectedConversation.value = null
    
    globalStore().$toast.success(__('Chat blocked successfully'))
  } catch (error) {
    console.error('Failed to block chat:', error)
    globalStore().$toast.error(__('Failed to block chat'))
  }
}

// Add event listeners
onMounted(async () => {
  await fetchUnreadCounts()
  
  // Wait for conversations to load before selecting from URL
  await conversationsResource.fetch()
  
  // Check if conversationId is in route params
  if (route.params.conversationId) {
    const conversation = conversations.value.find(c => c.name === route.params.conversationId)

    await handleConversationSelect(conversation)
    if (conversation) {
      await handleConversationSelect(conversation)
    }
  }
  
  $socket.on('messenger:message_update', (data) => {
    if (data.conversation_id === selectedConversation.value) {
      if (data.type === 'new') {
        if (['image', 'video', 'audio', 'document'].includes(data.message.content_type)) {
          if (data.message.attach) {
            const existingIndex = messages.value.findIndex(m => m.name === data.message.name)
            if (existingIndex !== -1) {
              messages.value[existingIndex] = data.message
            } else {
              messages.value.push(data.message)
            }
          }
        } else {
          messages.value.push(data.message)
        }
        
        setTimeout(() => {
          if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
          }
        }, 100)
      }
    }
  })

  $socket.on('messenger:conversation_update', (data) => {
    if (data.type === 'update') {
      const index = conversations.value.findIndex(c => c.name === data.conversation.name)
      if (index !== -1) {
        if (data.conversation.sender_id && !userProfiles.value[data.conversation.sender_id]) {
          fetchUserProfile(data.conversation.sender_id)
        }
        
        conversations.value[index] = {
          ...conversations.value[index],
          ...data.conversation,
          profile: userProfiles.value[data.conversation.sender_id]?.profile || null
        }
        conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
      } else {
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
          
          fetchUnreadCounts()
        })
      }
    }
  })

  $socket.on('messenger:unread_update', (data) => {
    if (data.conversation_id) {
      unreadMessageCounts.value[data.conversation_id] = data.unread_count
    }
  })

  $socket.on('messenger:message_status_update', (data) => {
    if (data.message_id) {
      const messageIndex = messages.value.findIndex(m => m.name === data.name)
      if (messageIndex !== -1) {
        messages.value[messageIndex].status = data.status
      }
    }
  })

  $socket.on('messenger:block_status_update', (data) => {
    if (data.conversation_id) {
      conversations.value = conversations.value.filter(c => c.name !== data.conversation_id)
      if (selectedConversation.value === data.conversation_id) {
        selectedConversation.value = null
      }
    }
  })

  $socket.on('messenger:conversation_status_update', (data) => {
    if (data.conversation_id) {
      const conversationIndex = conversations.value.findIndex(c => c.name === data.conversation_id)
      if (conversationIndex !== -1) {
        conversations.value[conversationIndex].status = data.status
        if (selectedConversation.value === data.conversation_id) {
          currentStatus.value = data.status
          if (data.status_log) {
            statusUpdates.value.push(data.status_log)
          }
        }
      }
    }
  })
})

// Clean up event listeners
onUnmounted(() => {
  $socket.off('messenger:message_update')
  $socket.off('messenger:conversation_update')
  $socket.off('messenger:unread_update')
  $socket.off('messenger:message_status_update')
  $socket.off('messenger:block_status_update')
  $socket.off('messenger:conversation_status_update')
})

// Add status resource
const statusResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Conversation Status',
    fields: ['status'],
    order_by: 'status asc'
  },
  onSuccess: (data) => {
    statusOptions.value = data.map(status => ({
      label: status.status,
      value: status.status,
      onClick: () => handleStatusChange(status.status)
    }))
  },
  auto: true
})

// Add status change handler
async function handleStatusChange(status) {
  if (!selectedConversation.value) return
  
  try {
    await createResource({
      url: 'frappe.client.set_value',
      params: {
        doctype: 'Messenger Conversation',
        name: selectedConversation.value,
        fieldname: 'status',
        value: status
      }
    }).submit()
    
    currentStatus.value = status
    
    // Update conversation in the list
    const conversationIndex = conversations.value.findIndex(c => c.name === selectedConversation.value)
    if (conversationIndex !== -1) {
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        status: status
      }
    }
    
    globalStore().$toast.success(__('Status updated successfully'))
  } catch (error) {
    console.error('Failed to update status:', error)
    globalStore().$toast.error(__('Failed to update status'))
  }
}

// Add this computed property to combine and sort messages and status updates
const combinedTimeline = computed(() => {
  if (!messages.value || !statusUpdates.value) return []
  
  const allItems = [
    ...messages.value.map(msg => ({
      ...msg,
      type: 'message',
      timestamp: msg.timestamp
    })),
    ...statusUpdates.value.map(update => ({
      ...update,
      type: 'status',
      timestamp: update.changed_on
    }))
  ]
 
  return allItems.sort((a, b) => {
    return new Date(a.timestamp) - new Date(b.timestamp)
  })
})

// Group timeline items by date, render date header once per group, then all items for that date
const groupedTimeline = computed(() => {
  // Combine messages and status updates, sort by timestamp
  
  const allItems = [
    ...messages.value.map(msg => ({
      ...msg,
      type: 'message',
      timestamp: msg.timestamp
    })),
    ...statusUpdates.value.map(update => ({
      ...update,
      type: 'status',
      timestamp: update.changed_on
    }))
  ].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))

  // Group by date
  const groups = {}
  allItems.forEach(item => {
    const dateObj = new Date(item.timestamp)
    const dateKey = dateObj.toDateString()
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(item)
  })

  return groups
})

// Add this helper function
function formatDate(dateString) {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return __('Today')
  } else if (date.toDateString() === yesterday.toDateString()) {
    return __('Yesterday')
  } else {
    return date.toLocaleDateString()
  }
}

// Add these functions after the existing functions
function getStatusIcon(status) {
  switch (status?.toLowerCase()) {
    case 'open':
      return IndicatorIcon
    case 'resolved':
      return CheckCircleIcon
    case 'closed':
      return CheckCircleIcon
    default:
      return StatusIcon
  }
}

function getStatusColor(status) {
  switch (status?.toLowerCase()) {
    case 'open':
      return 'text-blue-500'
    case 'resolved':
      return 'text-green-500'
    case 'closed':
      return 'text-gray-500'
    default:
      return 'text-gray-400'
  }
}
</script>

<style scoped>
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