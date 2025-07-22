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
            @click="messengerStore.refreshConversationList()"
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
                :label="messengerStore.platformFilter === 'all' ? __('All') : messengerStore.platformFilter"
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
        @scroll="handleScroll"
      >
        <!-- Loading indicator for conversations -->
        <div v-if="messengerStore.loading && !messengerStore.conversations.length" class="p-4 text-center text-ink-gray-3">
          {{ __('Loading conversations...') }}
        </div>
        
        <div
          v-for="conversation in messengerStore.filteredConversations"
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
                  v-if="messengerStore.unreadMessageCounts[conversation.name]"
                  class="flex h-[16px] min-w-[16px] items-center justify-center rounded-full bg-surface-gray-6 px-1 text-[10px] font-medium text-white ring-1 ring-white ml-2"
                >
                  {{ messengerStore.unreadMessageCounts[conversation.name] }}
                </div>
                <!-- If no unread count, show assignees here -->
                <template v-else-if="messengerStore.conversationAssignees[conversation.name] && messengerStore.conversationAssignees[conversation.name].length">
                  <div class="flex items-center gap-0.5 ml-2">
                    <Tooltip v-for="assignee in messengerStore.conversationAssignees[conversation.name]" :key="assignee.name" :text="assignee.label">
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
            <template v-if="(messengerStore.conversationTags[conversation.name] && messengerStore.conversationTags[conversation.name].length) || (messengerStore.unreadMessageCounts[conversation.name] && messengerStore.conversationAssignees[conversation.name] && messengerStore.conversationAssignees[conversation.name].length)">
              <div class="flex items-center mt-1 overflow-hidden min-h-[20px]">
                <!-- Tags left, avatars right -->
                <div class="flex items-center gap-1 flex-1" v-if="messengerStore.conversationTags[conversation.name] && messengerStore.conversationTags[conversation.name].length">
                  <template v-for="(tag, idx) in (messengerStore.conversationTags[conversation.name] || [])" :key="tag.tag_name">
                    <span :class="'px-1 py-0.5 rounded-full text-[9px] font-medium truncate max-w-[70px] border ' + (tagColorMap[tag.color] || 'border-outline-gray-2 text-ink-gray-6')">
                      {{ tag.tag_name }}
                    </span>
                  </template>
                  <span v-if="shouldShowEllipsis(conversation.name)" class="text-[9px] text-ink-gray-3">...</span>
                </div>
                <div class="flex-1" v-else></div>
                <!-- Assigned user avatars (if unread count exists) -->
                <div class="flex items-center gap-0.5 ml-2" v-if="messengerStore.unreadMessageCounts[conversation.name] && messengerStore.conversationAssignees[conversation.name] && messengerStore.conversationAssignees[conversation.name].length">
                  <Tooltip v-for="assignee in messengerStore.conversationAssignees[conversation.name]" :key="assignee.name" :text="assignee.label">
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
        <div v-if="messengerStore.loading && messengerStore.conversations.length" class="p-4 text-center text-ink-gray-3">
          {{ __('Loading more conversations...') }}
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
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
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
import { useMessengerStore } from '@/stores/messenger'
import Filter from '@/components/Filter.vue'
import { frappeTimeAgo } from '@/utils'

const router = useRouter()
const route = useRoute()
const { $socket } = globalStore()
const messengerStore = useMessengerStore()

const selectedConversation = ref(null)
const list = computed({
  get: () => messengerStore.list,
  set: (value) => (messengerStore.list = value),
})

const platformOptions = ref([])

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
  messengerStore.updateFilters(filters)
}

function handlePlatformSelect(platform) {
  messengerStore.updatePlatformFilter(platform)
}

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

function handleConversationSelect(conversation) {
  router.push({
    name: 'MessengerDetail',
    params: { conversationId: conversation.name },
  })
}

function handleScroll(e) {
  const el = e.target
  if (el.scrollTop + el.clientHeight >= el.scrollHeight - 50) {
    messengerStore.fetchConversations(true)
  }
}

function shouldShowEllipsis(conversationName) {
  const tags = messengerStore.conversationTags[conversationName] || []
  if (!tags.length) return false
  if (tags.length === 1 && tags[0].tag_name.length > 15) return true
  const container = document.querySelector('.overflow-hidden')
  if (!container) return false
  const tagElements = container.querySelectorAll('span:not(:last-child)')
  if (!tagElements.length) return false
  let totalWidth = 0
  tagElements.forEach((el) => {
    totalWidth += el.offsetWidth
  })
  return totalWidth > container.offsetWidth - 20
}

function setupSocketListeners() {
  cleanupSocketListeners()
  $socket.on('messenger:message_update', messengerStore.handleMessageUpdate)
  $socket.on('messenger:message_sent', messengerStore.handleMessageUpdate)
  $socket.on('messenger:unread_update', messengerStore.handleUnreadUpdate)
  $socket.on('messenger:conversation_update', messengerStore.handleConversationUpdate)
  $socket.on('messenger:conversation_status_update', messengerStore.handleStatusUpdate)
}

function cleanupSocketListeners() {
    $socket.off('messenger:message_update', messengerStore.handleMessageUpdate)
    $socket.off('messenger:message_sent', messengerStore.handleMessageUpdate)
    $socket.off('messenger:unread_update', messengerStore.handleUnreadUpdate)
    $socket.off('messenger:conversation_update', messengerStore.handleConversationUpdate)
    $socket.off('messenger:conversation_status_update', messengerStore.handleStatusUpdate)
}

watch(() => router.currentRoute.value.params.conversationId,
  (newId) => {
    selectedConversation.value = newId || null
  },
  { immediate: true }
)

watch(messengerEnabled, (enabled) => {
  if (enabled) {
    nextTick(() => {
      setupSocketListeners()
      messengerStore.fetchConversations()
    })
  } else {
    cleanupSocketListeners()
  }
}, { immediate: true })

onUnmounted(() => {
  cleanupSocketListeners()
})
</script> 