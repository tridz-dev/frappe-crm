<template>
  <div v-if="messengerEnabled" class="flex h-full">
    <!-- Sidebar: Conversation List and Filters -->
    <div class="w-80 border-r border-outline-gray-1 flex flex-col">
      <div class="p-4 space-y-2 border-b border-outline-gray-1">
        <div class="flex items-center justify-between gap-x-2">
          <h2 class="text-lg font-medium text-ink-gray-9">{{ __('Messages') }}</h2>
          <Button
            appearance="minimal"
            class="text-ink-gray-4 hover:text-ink-gray-9"
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
                class="min-w-[200px] justify-between text-ink-gray-4 hover:text-ink-gray-9"
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
          const scrollTop = el.scrollTop
          const scrollHeight = el.scrollHeight
          const clientHeight = el.clientHeight
          // Load more when user scrolls down to bottom (within 50px of bottom)
          if (scrollTop + clientHeight >= scrollHeight - 50) {
            loadMoreConversations()
          }
        }"
      >
        <!-- Loading indicator for conversations -->
        <div v-if="conversationsLoading" class="p-4 text-center text-ink-gray-3">
          {{ __('Loading more conversations...') }}
        </div>
        
        <div
          v-for="conversation in filteredConversations"
          :key="conversation.name"
          class="group flex items-center p-4 hover:bg-surface-gray-1 cursor-pointer border-b border-outline-gray-1 transition-colors"
          :class="{ 'bg-surface-gray-1': selectedConversation === conversation.name }"
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
            <!-- First row: Profile name (left), timestamp (right) -->
            <div class="flex items-center justify-between">
              <p class="text-sm font-medium text-ink-gray-9 truncate">
                {{ conversation.title }}
              </p>
              <p class="text-xs text-ink-gray-3">{{ frappeTimeAgo(conversation.last_message_time) }}</p>
            </div>
            <!-- Second row: Last message (left), unread count (right) and/or assignees if no unread count -->
            <div class="flex items-center justify-between mt-0.5">
              <p class="text-xs text-ink-gray-3 truncate">
                {{ conversation.last_message }}
              </p>
              <div class="flex items-center">
                <div
                  v-if="unreadMessageCounts[conversation.name]"
                  class="flex h-[16px] min-w-[16px] items-center justify-center rounded-full bg-surface-gray-6 px-1 text-[10px] font-medium text-white ring-1 ring-white ml-2"
                >
                  {{ unreadMessageCounts[conversation.name] }}
                </div>
                <!-- If no unread count, show assignees here -->
                <template v-else-if="conversationAssignees[conversation.name] && conversationAssignees[conversation.name].length">
                  <div class="flex items-center gap-0.5 ml-2">
                    <Tooltip v-for="assignee in conversationAssignees[conversation.name]" :key="assignee.name" :text="assignee.label">
                      <Avatar
                        :label="assignee.label"
                        :image="assignee.image"
                        size="sm"
                        class="border border-white -ml-1"
                      />
                    </Tooltip>
                  </div>
                </template>
              </div>
            </div>
            <!-- Third row: Tags (smaller), then assigned user avatars (if unread count exists) -->
            <template v-if="(conversationTags[conversation.name] && conversationTags[conversation.name].length) || (unreadMessageCounts[conversation.name] && conversationAssignees[conversation.name] && conversationAssignees[conversation.name].length)">
              <div class="flex items-center mt-1 overflow-hidden min-h-[20px]">
                <!-- Tags left, avatars right -->
                <div class="flex items-center gap-1 flex-1" v-if="conversationTags[conversation.name] && conversationTags[conversation.name].length">
                  <template v-for="(tag, idx) in (conversationTags[conversation.name] || [])" :key="tag.tag_name">
                    <span :class="'px-1 py-0.5 rounded-full text-[9px] font-medium truncate max-w-[70px] border ' + (tagColorMap[tag.color] || 'border-outline-gray-2 text-ink-gray-6')">
                      {{ tag.tag_name }}
                    </span>
                  </template>
                  <span v-if="shouldShowEllipsis(conversation.name)" class="text-[9px] text-ink-gray-3">...</span>
                </div>
                <div class="flex-1" v-else></div>
                <!-- Assigned user avatars (if unread count exists) -->
                <div class="flex items-center gap-0.5 ml-2" v-if="unreadMessageCounts[conversation.name] && conversationAssignees[conversation.name] && conversationAssignees[conversation.name].length">
                  <Tooltip v-for="assignee in conversationAssignees[conversation.name]" :key="assignee.name" :text="assignee.label">
                    <Avatar
                      :label="assignee.label"
                      :image="assignee.image"
                      size="sm"
                      class="border border-white -ml-1"
                    />
                  </Tooltip>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
    <!-- Main Content: Router View for Placeholder or Detail -->
    <div class="flex-1">
      <router-view :key="$route.fullPath" />
    </div>
  </div>
  <div v-else class="flex h-full items-center justify-center">
    <div class="text-center">
      <MessengerIcon class="mx-auto h-12 w-12 text-ink-gray-2" />
      <h3 class="mt-2 text-sm font-medium text-ink-gray-9">{{ __('Messenger not available') }}</h3>
      <p class="mt-1 text-sm text-ink-gray-3">
        {{ __('Please ensure Messenger is enabled in Messenger Settings.') }}
      </p>
    </div>
  </div>
</template>

<script setup>
// Imports
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
import { createResource, call } from 'frappe-ui'
import { Button, Avatar, Dropdown, Tooltip } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'
import ChevronDownIcon from '@/components/Icons/ChevronDownIcon.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import InstagramIcon from '@/components/Icons/InstagramIcon.vue'
import WhatsAppIcon from '../components/Icons/WhatsAppIcon.vue'
import ChatIcon from '@/components/Icons/ChatIcon.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import { messengerEnabled } from '@/composables/settings'
import { globalStore } from '@/stores/global'
import Filter from '@/components/Filter.vue'
import { formatDate, timeAgo, frappeTimeAgo } from '@/utils'

const router = useRouter()
const route = useRoute()
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
const list = ref(null)
const conversationTags = ref({})
const conversationAssignees = ref({})

// Add socket event listener tracking
const isFetchingUnreadCounts = ref(false)

// Add caching for static data
const cachedData = ref({
  allTags: [],
  allStatuses: [],
  helpdeskEnabled: false
})

// Add cache for conversation details
const conversationCache = ref(new Map())

// Add function to load cached data
async function loadCachedData() {
  try {
    const data = await call('crm.api.messenger.get_cached_data')
    if (data) {
      cachedData.value = {
        allTags: data.all_tags || [],
        allStatuses: data.all_statuses || [],
        helpdeskEnabled: data.helpdesk_enabled || false
      }
    }
  } catch (error) {
    console.error('Failed to load cached data:', error)
  }
}

// Tag color mapping
const tagColorMap = {
  black: 'border-ink-gray-9 text-ink-gray-9',
  gray: 'border-outline-gray-2 text-ink-gray-6',
  blue: 'border-outline-blue-2 text-ink-blue-2',
  green: 'border-outline-green-2 text-ink-green-2',
  red: 'border-outline-red-2 text-ink-red-2',
  pink: 'border-ink-pink-1 text-ink-pink-1',
  orange: 'border-outline-orange-1 text-outline-orange-1',
  amber: 'border-outline-amber-2 text-ink-amber-2',
  yellow: 'border-outline-amber-1 text-ink-amber-2',
  cyan: 'border-ink-cyan-1 text-ink-cyan-1',
  teal: 'border-ink-cyan-1 text-ink-cyan-1',
  violet: 'border-ink-violet-1 text-ink-violet-1',
  purple: 'border-ink-violet-1 text-ink-violet-1',
}

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

const platformsResource = createResource({
  url: 'frappe.client.get_list',
  params: {
    doctype: 'Messenger Platform',
    fields: ['platform'],
    order_by: 'platform asc',
    filters: [['disabled', '=', 0]]
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

const platformOptions = ref([
  { 
    label: __('All'), 
    value: 'all',
    onClick: () => handlePlatformSelect('all'),
    icon: ChatIcon
  }
])

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

function handlePlatformSelect(platform) {
  selectedPlatformFilter.value = platform
  conversationPage.value = 0
  conversations.value = []
  conversationsResource.params = {
    limit: 20,
    offset: 0,
    platform_filter: platform
  }
  conversationsResource.reload()
}

const filteredConversations = computed(() => {
  if (selectedPlatformFilter.value === 'all') {
    return conversations.value
  }
  return conversations.value.filter(conv => {
    return conv.platform?.toLowerCase() === selectedPlatformFilter.value.toLowerCase()
  })
})

const conversationsResource = createResource({
  url: 'crm.api.messenger.get_conversations_with_details',
  params: {
    limit: 20,
    offset: 0,
    platform_filter: 'all'
  },
  onSuccess: async (data) => {
    if (data) {
      conversations.value = data.conversations || []
      userProfiles.value = data.user_profiles || {}
      conversationTags.value = data.conversation_tags || {}
      conversationAssignees.value = data.conversation_assignees || {}
      unreadMessageCounts.value = data.unread_counts || {}
      
      if (list.value) {
        list.value.data.params.filters = conversationsResource.params.filters
        list.value.params.filters = conversationsResource.params.filters
      }
    }
  },
  auto: true
})

function handleConversationSelect(conversation) {
  router.push({ 
    name: 'MessengerDetail',
    params: { conversationId: conversation.name }
  })
}

async function fetchUnreadCounts() {
  // Prevent multiple simultaneous calls
  if (isFetchingUnreadCounts.value) {
    console.log('fetchUnreadCounts already running, skipping...')
    return
  }
  
  isFetchingUnreadCounts.value = true
  
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
  } finally {
    isFetchingUnreadCounts.value = false
  }
}

async function loadMoreConversations() {
  if (!hasMoreConversations.value || conversationsLoading.value) return
  conversationsLoading.value = true
  try {
    const nextPage = conversationPage.value + 1
    const response = await call('crm.api.messenger.get_conversations_with_details', {
      limit: 20,
      offset: nextPage * 20,
      platform_filter: selectedPlatformFilter.value
    })
    
    if (response && response.conversations) {
      if (response.conversations.length < 20) {
        hasMoreConversations.value = false
      }
      
      // Merge new data with existing data
      conversations.value = [...conversations.value, ...response.conversations]
      Object.assign(userProfiles.value, response.user_profiles || {})
      Object.assign(conversationTags.value, response.conversation_tags || {})
      Object.assign(conversationAssignees.value, response.conversation_assignees || {})
      Object.assign(unreadMessageCounts.value, response.unread_counts || {})
      
      conversationPage.value = nextPage
    } else {
      hasMoreConversations.value = false
    }
  } catch (error) {
    console.error('Failed to load more conversations:', error)
  } finally {
    conversationsLoading.value = false
  }
}

function shouldShowEllipsis(conversationName) {
  const tags = conversationTags.value[conversationName] || []
  if (!tags.length) return false
  if (tags.length === 1 && tags[0].tag_name.length > 15) return true
  const container = document.querySelector('.overflow-hidden')
  if (!container) return false
  const tagElements = container.querySelectorAll('span:not(:last-child)')
  if (!tagElements.length) return false
  let totalWidth = 0
  tagElements.forEach(el => {
    totalWidth += el.offsetWidth
  })
  return totalWidth > container.offsetWidth - 20
}

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

watch(() => conversationsResource.data, async () => {
  // Remove this watcher as it causes continuous API calls
  // Unread counts are already fetched by get_conversations_with_details API
}, { deep: true })

// --- SOCKET HANDLERS ---
function onMessageUpdate(data) {
  // console.log('Message update received in layout:', data)
  // console.log('Current selected conversation:', selectedConversation.value)
  // console.log('Available conversations:', conversations.value.map(c => c.name))
  
  if (data.type === 'new') {
    const conversationIndex = conversations.value.findIndex(c => c.name === data.conversation_id)
    // console.log('Found conversation index:', conversationIndex, 'for conversation:', data.conversation_id)
    
    if (conversationIndex !== -1) {
      // Update the conversation's last message and timestamp
      const oldConversation = conversations.value[conversationIndex]
      conversations.value[conversationIndex] = {
        ...conversations.value[conversationIndex],
        last_message: data.message.message,
        last_message_time: data.message.timestamp
      }
      
      // console.log('Updated conversation from message:', {
      //   old: oldConversation,
      //   new: conversations.value[conversationIndex]
      // })
      
      // Re-sort conversations by last message time
      conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
      
      // console.log('Conversations after sorting:', conversations.value.map(c => ({
      //   name: c.name,
      //   last_message: c.last_message,
      //   last_message_time: c.last_message_time
      // })))
    } else {
      // console.log('Conversation not found in list, available conversations:', conversations.value.map(c => c.name))
      // console.log('This might be a new conversation that needs to be fetched')
      
      // Try to fetch the conversation if it's not in the list
      if (data.conversation_id) {
        // console.log('Attempting to fetch conversation:', data.conversation_id)
        refreshConversationList()
      }
    }
  }
}

function onMessageSent(data) {
  // console.log('Message sent event received in layout:', data)
  const conversationIndex = conversations.value.findIndex(c => c.name === data.conversation_id)
  if (conversationIndex !== -1) {
    // Update the conversation's last message and timestamp
    conversations.value[conversationIndex] = {
      ...conversations.value[conversationIndex],
      last_message: data.message.message,
      last_message_time: data.message.timestamp
    }
    
    // console.log('Updated conversation from sent message:', conversations.value[conversationIndex])
    
    // Re-sort conversations by last message time
    conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
  } else {
    console.log('Conversation not found for sent message, available conversations:', conversations.value.map(c => c.name))
  }
}

function onUnreadUpdate(data) {
  // console.log('Unread update received in layout:', data)
  // console.log('Current unread counts before update:', unreadMessageCounts.value)
  
  if (data.conversation_id) {
    const oldCount = unreadMessageCounts.value[data.conversation_id] || 0
    unreadMessageCounts.value[data.conversation_id] = data.unread_count
    
    // console.log('Unread count updated for conversation:', {
    //   conversation_id: data.conversation_id,
    //   old_count: oldCount,
    //   new_count: data.unread_count,
    //   change: data.unread_count - oldCount
    // })
    
    // console.log('Current unread counts after update:', unreadMessageCounts.value)
  } else {
    console.log('No conversation_id in unread update data')
  }
}

function onConversationUpdate(data) {
  // console.log("Conversation update received in layout:", data)
  if (data.type === 'update') {
    const index = conversations.value.findIndex(c => c.name === data.conversation.name)
    // console.log('Found conversation index:', index, 'for conversation:', data.conversation.name)
    // console.log('Available conversations:', conversations.value.map(c => c.name))
    
    if (index !== -1) {
      // Fetch user profile if not already available
      if (data.conversation.sender_id && !userProfiles.value[data.conversation.sender_id]) {
        fetchUserProfile(data.conversation.sender_id)
      }
      
      // Update conversation with all fields
      conversations.value[index] = {
        ...conversations.value[index],
        ...data.conversation,
        title: userProfiles.value[data.conversation.sender_id]?.username || data.conversation.sender_id,
        profile: userProfiles.value[data.conversation.sender_id]?.profile || null
      }
      
      // console.log('Updated existing conversation:', conversations.value[index])
      
      // Re-sort conversations by last message time
      conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
    } else {
      // console.log('Conversation not found, adding new conversation')
      // New conversation - fetch user profile and add to list
      fetchUserProfile(data.conversation.sender_id).then(() => {
        const newConversation = {
          ...data.conversation,
          title: userProfiles.value[data.conversation.sender_id]?.username || data.conversation.sender_id,
          profile: userProfiles.value[data.conversation.sender_id]?.profile || null
        }
        
        // console.log('Adding new conversation:', newConversation)
        
        conversations.value = [
          newConversation,
          ...conversations.value
        ].sort((a, b) => 
          new Date(b.last_message_time) - new Date(a.last_message_time)
        )
        
        // Remove this call as unread counts are handled by socket events
        // fetchUnreadCounts()
      })
    }
  }
}

function setupSocketListeners() {
  cleanupSocketListeners() // Always clean up first to avoid duplicates
  $socket.on('messenger:message_update', onMessageUpdate)
  $socket.on('messenger:message_sent', onMessageSent)
  $socket.on('messenger:unread_update', onUnreadUpdate)
  $socket.on('messenger:conversation_update', onConversationUpdate)
}

function cleanupSocketListeners() {
  $socket.off('messenger:message_update', onMessageUpdate)
  $socket.off('messenger:message_sent', onMessageSent)
  $socket.off('messenger:unread_update', onUnreadUpdate)
  $socket.off('messenger:conversation_update', onConversationUpdate)
}

// Add watcher to re-initialize socket listeners when messenger is enabled
watch(messengerEnabled, (enabled) => {
  if (enabled) {
    // Small delay to ensure component is fully mounted
    nextTick(() => {
      setupSocketListeners()
    })
  } else {
    cleanupSocketListeners()
  }
})

// Add function to refresh conversation list
function refreshConversationList() {
  // console.log('Refreshing conversation list')
  conversationsResource.reload()
  // Remove fetchUnreadCounts() as the API already returns unread counts
  // fetchUnreadCounts()
}

// Add watcher to track current conversation from route
watch(() => router.currentRoute.value.params.conversationId, (newConversationId) => {
  // console.log('Route conversation ID changed:', newConversationId)
  selectedConversation.value = newConversationId || null
  
  // Only refresh if we have a valid conversation ID
  if (newConversationId) {
    // Don't refresh conversation list for every conversation selection
    // The conversation details are handled by MessengerDetail.vue
    console.log('Conversation selected, details will be loaded by MessengerDetail.vue')
  }
}, { immediate: true })

// Add watcher to refresh conversations when route changes back to list
watch(() => router.currentRoute.value.path, (newPath) => {
  if (newPath === '/messenger' && messengerEnabled.value) {
    // Refresh conversations when navigating back to the list
    conversationsResource.reload()
    // Remove fetchUnreadCounts() as the API already returns unread counts
    // fetchUnreadCounts()
  }
})

watch(() => conversations.value, () => {
  // No longer needed as tags and assignees are fetched by the API
})

onMounted(async () => {
  await loadCachedData()
  setupSocketListeners()
})

onUnmounted(() => {
  cleanupSocketListeners()
})
</script> 