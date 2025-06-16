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

    <!-- Empty State -->
    <div class="flex-1 grid place-items-center bg-gray-50">
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
import { Button, Input, Avatar, Badge, Dropdown } from 'frappe-ui'
import { useRouter } from 'vue-router'
import ChevronDownIcon from '@/components/Icons/ChevronDownIcon.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import InstagramIcon from '@/components/Icons/InstagramIcon.vue'
import WhatsAppIcon from '../components/Icons/WhatsAppIcon.vue'
import ChatIcon from '@/components/Icons/ChatIcon.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import { messengerEnabled } from '@/composables/settings'
import { globalStore } from '@/stores/global'
import Filter from '@/components/Filter.vue'

const router = useRouter()
const { $socket } = globalStore()

// State management
const conversations = ref([])
const conversationsLoading = ref(false)
const conversationPage = ref(0)
const hasMoreConversations = ref(true)
const unreadMessageCounts = ref({})
const userProfiles = ref({})
const selectedPlatformFilter = ref('all')
const selectedConversation = ref(null)

// Add filter functionality
const list = ref(null)

// Add a computed property to track current filters
const currentFilters = computed(() => {
  return conversationsResource.params?.filters || {}
})

function updateFilter(filters) {
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat'],
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
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform'],
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
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat'],
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

// Function to handle conversation selection
function handleConversationSelect(conversation) {
  router.push({ 
    name: 'Messenger',
    params: { conversationId: conversation.name }
  })
}

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

// Add function to load more conversations
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
        limit_start: nextPage * 20,
        limit_page_length: 20,
        filters: selectedPlatformFilter.value !== 'all' ? 
          [['platform', '=', selectedPlatformFilter.value]] : []
      }
    }).fetch()

    if (response.length < 20) {
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

// Add event listeners
onMounted(() => {
  fetchUnreadCounts()
  
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

  $socket.on('messenger:block_status_update', (data) => {
    if (data.conversation_id) {
      conversations.value = conversations.value.filter(c => c.name !== data.conversation_id)
    }
  })
})

// Clean up event listeners
onUnmounted(() => {
  $socket.off('messenger:conversation_update')
  $socket.off('messenger:unread_update')
  $socket.off('messenger:block_status_update')
})

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

// Watch for conversation refresh
watch(() => conversationsResource.data, async () => {
  await fetchUnreadCounts()
}, { deep: true })

// Watch for messenger enabled status
watch(messengerEnabled, (enabled) => {
  if (enabled) {
    conversationsResource.fetch()
  }
})
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