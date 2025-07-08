<template>
  <div v-if="messengerEnabled" class="flex h-full">
    <!-- Left Column: Conversations List -->
    <div class="w-80 border-r border-outline-gray-1 flex flex-col">
      <div class="p-4 space-y-2 border-b border-outline-gray-1">
        <div class="flex items-center justify-between gap-x-2">
          <h2 class="text-lg font-medium text-ink-gray-9">{{ __('Messages') }}</h2>
          <Button
            appearance="minimal"
            class="text-ink-gray-4 hover:text-ink-gray-9 text-sm font-medium px-2 py-1.5 rounded gap-2"
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
                class="min-w-[200px] justify-between text-ink-gray-4 hover:text-ink-gray-9 text-sm font-medium px-2 py-1.5 rounded gap-2"
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
              <p class="text-xs text-ink-gray-3">{{ formatTimeAgo(conversation.last_message_time) }}</p>
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

    <!-- Right Column: Chat View -->
    <div class="flex-1 flex flex-col bg-surface-white" v-if="selectedConversation">
      <!-- Chat Header -->
      <div class="flex items-center justify-between p-4 border-b border-outline-gray-1">
        <div class="flex items-center gap-4">
          <Avatar
            :label="selectedConversationTitle"
            :image="selectedConversationProfile"
            size="md"
            class="flex-shrink-0"
          />
          <div class="flex items-center gap-4">
            <div>
              <div class="flex items-center gap-2">
                <h3 class="text-base font-medium text-ink-gray-9">
                  {{ selectedConversationTitle }}
                </h3>
              </div>
              <div class="flex items-center gap-2">
                <p class="text-sm text-ink-gray-3">{{ selectedConversationPlatform }}</p>
              </div>
            </div>
            <!-- Tag pills and plus button aligned here -->
            <div class="flex items-center gap-2">
              <template v-for="(tag, idx) in selectedTags.slice(0,2)" :key="tag.tag_name">
                <span :class="'px-2 py-0.5 rounded-full text-xs font-medium cursor-pointer border ' + (tagColorMap[tag.color] || 'border-outline-gray-2 text-ink-gray-6')">
                  {{ tag.tag_name }}
                  <span class="ml-1 cursor-pointer" @click.stop="removeTag(tag)">&times;</span>
                </span>
              </template>
              <span v-if="selectedTags.length > 2" class="px-2 py-0.5 rounded-full text-xs font-medium border border-outline-gray-2 text-ink-gray-6 cursor-pointer" @click="showAllTags = true">
                +{{ selectedTags.length - 2 }}
              </span>
              <span v-if="unselectedTags.length" class="relative">
                <span class="px-2 py-0.5 rounded-full text-xs font-medium border border-dashed border-outline-gray-3 text-ink-gray-6 cursor-pointer" @click="() => { showAddTagDropdown = !showAddTagDropdown; tagSearchQuery = '' }">
                  +
                </span>
                <div v-if="showAddTagDropdown" class="absolute left-0 mt-2 min-w-max bg-surface-white border rounded shadow z-50">
                  <input
                    v-model="tagSearchQuery"
                    type="text"
                    placeholder="Search tags..."
                    class="w-full px-2 py-1 border-b border-outline-gray-1 outline-none text-sm"
                    @click.stop
                  />
                  <div v-for="tag in dropdownTags" :key="tag.tag_name" @click="addTag(tag)" :class="'px-3 py-1 cursor-pointer hover:bg-surface-gray-1 ' + (tagColorMap[tag.color] || '')">
                    {{ tag.tag_name }}
                  </div>
                  <div v-if="dropdownTags.length === 0" class="px-3 py-2 text-ink-gray-2 text-sm">No tags found</div>
                </div>
              </span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <div v-if="selectedConversationLatestTicketStatus" :class="`flex items-center gap-1 px-2 py-1 rounded ${getTicketStatusColor(selectedConversationLatestTicketStatus).bg} ${getTicketStatusColor(selectedConversationLatestTicketStatus).border} ${getTicketStatusColor(selectedConversationLatestTicketStatus).text} text-xs font-semibold`" style="height:32px;">
            <TicketIcon :class="`w-4 h-4 ${getTicketStatusColor(selectedConversationLatestTicketStatus).icon}`" />
            <span>{{ selectedConversationLatestTicketStatus }}</span>
          </div>
          <Dropdown
            :options="statusOptions"
            placement="bottom-start"
            @select="handleStatusChange"
          >
            <template #default>
              <Button
                appearance="minimal"
                class="flex items-center gap-2 text-sm text-ink-gray-3 hover:text-ink-gray-9 border border-outline-gray-1 rounded-md px-3 py-1.5"
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
                class="text-ink-gray-4 hover:text-ink-gray-9"
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
        <div v-if="messagesLoading" class="p-4 text-center text-ink-gray-3">
          {{ __('Loading older messages...') }}
        </div>
        
        <!-- Messages and Status Updates -->
        <template v-if="Object.keys(groupedTimeline).length > 0">
          <div v-for="(items, dateKey) in groupedTimeline" :key="dateKey">
            <!-- Date Header -->
            <div class="flex justify-center my-4">
              <div class="bg-surface-gray-1 rounded-full px-4 py-1 text-sm text-ink-gray-4">
                {{ formatDate(items[0].timestamp) }}
              </div>
            </div>
            <!-- Items for this date -->
            <div v-for="item in items" :key="item.type === 'message' ? item.name : `status-${item.changed_on}`">
              <!-- Status Update Info Block -->
              <div v-if="item.type === 'status'" class="flex justify-center my-4">
                <div class="bg-surface-gray-1 border border-outline-gray-1 rounded-lg px-4 py-2 text-sm">
                  <div class="flex items-center gap-2">
                    <component 
                      :is="getStatusIcon(item.status)"
                      :class="getStatusColor(item.status)"
                    />
                    <span class="text-ink-gray-4">{{ __('Status changed to') }}</span>
                    <span class="font-medium text-ink-gray-7">{{ item.status }}</span>
                    <span class="text-ink-gray-4">{{ __('by') }}</span>
                    <span class="font-medium text-ink-gray-7">{{ item.changed_by }}</span>
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
          <div class="text-center text-ink-gray-3">
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
    <div v-else class="flex-1 grid place-items-center bg-surface-gray-1">
      <div class="text-center">
        <div class="mx-auto h-12 w-12 text-ink-gray-2">
          <MessengerIcon />
        </div>
        <h3 class="mt-2 text-sm font-medium text-ink-gray-9">{{ __('No conversation selected') }}</h3>
        <p class="mt-1 text-sm text-ink-gray-3">{{ __('Choose a conversation to start messaging') }}</p>
      </div>
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
  <!-- Modal for all tags -->
  <div v-if="showAllTags" class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-30" @click.self="showAllTags = false">
    <div class="bg-surface-white rounded-lg p-4 min-w-[200px]">
      <div class="flex flex-wrap gap-2">
        <span v-for="tag in selectedTags" :key="tag.tag_name" :class="'px-2 py-0.5 rounded-full text-xs font-medium border flex items-center gap-1 ' + (tagColorMap[tag.color] || 'border-outline-gray-2 text-ink-gray-6')">
          {{ tag.tag_name }}
          <span class="cursor-pointer hover:text-red-500" @click="removeTag(tag)">&times;</span>
        </span>
      </div>
      <button class="mt-4 px-4 py-1 bg-surface-gray-1 rounded" @click="showAllTags = false">Close</button>
    </div>
  </div>
  <!-- Add click-outside handler for add tag dropdown -->
  <div v-if="showAddTagDropdown" class="fixed inset-0 z-40" @click="showAddTagDropdown = false"></div>
  <!-- Helpdesk Ticket Creation Modal -->
  <Dialog v-model="showHelpdeskModal" :options="{ size: 'xl', class: 'crm-modal-tight' }">
    <template #body-title>
      <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
        {{ __('Helpdesk Tickets') }}
      </h3>
    </template>
    <template #body-content>
      <div class="bg-surface-modal px-0 pb-4 pt-4 flex flex-col " style="min-width:400px;">
        <div v-if="pastTickets.length">
          <div v-for="ticket in pastTickets" :key="ticket.hd_ticket" class="flex items-center justify-between border-b py-2 cursor-pointer hover:bg-surface-gray-1 px-4" @click="goToTicket(ticket.hd_ticket)">
            <div class="flex items-center gap-2">
              <TicketIcon :class="`w-4 h-4 ${getTicketStatusColor(ticket.status).icon}`" />
              <span :class="`text-xs font-medium ${getTicketStatusColor(ticket.status).text}`">{{ ticket.status }}</span>
              <span class="text-xs text-ink-gray-6">{{ ticket.subject }}</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="text-xs font-medium" :class="{'text-green-600': ticket.status === 'Open', 'text-gray-500': ticket.status !== 'Open'}">{{ ticket.status }}</span>
              <span class="text-xs text-ink-gray-4">{{ formatTimeAgo(ticket.creation_time) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-xs text-ink-gray-4 mb-4 px-4">{{ __('No tickets yet for this conversation.') }}</div>
        <div class="flex justify-end mt-4 px-4">
          <Button v-if="!showCreateTicketFields" class="bg-surface-gray-7 text-white hover:bg-surface-gray-6" appearance="primary" @click="showCreateTicketFields = true">{{ __('Create New Ticket') }}</Button>
        </div>
        <div v-if="showCreateTicketFields" class="flex flex-col gap-4 mt-2 px-4">
          <FormControl
            v-model="helpdeskSubject"
            :label="__('Subject')"
            :placeholder="__('Short description')"
            required
            class="!w-full"
          />
          <Link
            v-model="helpdeskTicketType"
            doctype="HD Ticket Type"
            :placeholder="__('Select Ticket Type')"
            class="form-control !w-full"
            :hideMe="true"
            required
          />
          <div>
            <div class="mb-1.5 text-xs text-ink-gray-5">{{ __('Detailed Explanation') }}</div>
            <TextEditor
              variant="outline"
              :content="helpdeskDescription"
              @change="val => helpdeskDescription = val"
              editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 rounded border border-[--surface-gray-2] bg-surface-gray-2 placeholder-ink-gray-4 hover:border-outline-gray-modals hover:bg-surface-gray-3 hover:shadow-sm focus:bg-surface-white focus:border-outline-gray-4 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3 text-ink-gray-8 transition-colors !w-full"
              :bubbleMenu="true"
              :placeholder="__('Describe the issue or request in detail')"
            />
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <Button
              appearance="minimal"
              class="bg-surface-gray-2 text-ink-gray-7 hover:bg-surface-gray-3 rounded px-6 py-2 text-base font-medium"
              @click="closeHelpdeskModal"
              :disabled="helpdeskModalLoading"
            >
              {{ __('Cancel') }}
            </Button>
            <Button
              appearance="primary"
              class="bg-surface-gray-7 text-white hover:bg-surface-gray-6 rounded px-6 py-2 text-base font-medium"
              :loading="helpdeskModalLoading"
              @click="submitHelpdeskTicket"
            >
              {{ __('Submit') }}
            </Button>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue'
import { createResource } from 'frappe-ui'
import { Button, Input, Avatar, Badge, Dropdown, Tooltip, TextEditor, Dialog, FormControl } from 'frappe-ui'
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
import TicketIcon from '@/components/Icons/TicketIcon.vue'
import { ref as vueRef } from 'vue'
import { useRouter as useVueRouter } from 'vue-router'
import { markRaw } from 'vue'
import Link from '@/components/Controls/Link.vue'

const router = useRouter()
const route = useRoute()
const { $socket } = globalStore()
const vueRouter = useVueRouter()

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
  return list.value?.data?.params?.filters || {}
})

function updateFilter(filters) {
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
  
  conversationsResource.params = {
    doctype: 'Messenger Conversation',
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat','status','latest_ticket_status'],
    order_by: 'last_message_time desc',
    filters: {
      ...filters
    }
  }
  
  conversationsResource.reload()
}

// Add platform resource
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
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform','status','latest_ticket_status'],
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
    fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform', 'block_chat','status','latest_ticket_status'],
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

// Update handleConversationSelect to fetch tags
async function handleConversationSelect(conversation) {
  if (!conversation) return
  
  await fetchEnableHelpdeskTicketCreation()
  selectedConversation.value = conversation.name
  currentStatus.value = conversation.status || ''
  
  // Ensure tickets are fetched before menu renders
  await fetchPastTickets()
  
  // Reset messages and status updates
  messages.value = []
  statusUpdates.value = []
  
  // Fetch tags for the selected conversation
  try {
    const tags = await call('crm.api.messenger.get_conversation_tags', { conversation_name: conversation.name })
    conversationTags.value[conversation.name] = tags || []
  } catch (e) {
    conversationTags.value[conversation.name] = []
  }
  
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
        fields: ['name', 'sender_id', 'last_message', 'last_message_time', 'platform','status','latest_ticket_status'],
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
const conversationMenuOptions = computed(() => {
  const hasTickets = pastTickets.value.length > 0
  let latestStatus = null
  if (hasTickets) {
    latestStatus = pastTickets.value[0]?.status || null
  }
  // Default to black icon if no status
  const iconColor = latestStatus ? getTicketStatusColor(latestStatus).icon : 'text-gray-700'
  const options = [
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
  ]
  if (enableHelpdeskTicketCreation.value) {
    options.unshift({
      label: hasTickets ? __('View Tickets') : __('Create Ticket'),
      icon: hasTickets ? markRaw(TicketIcon) : 'plus',
      onClick: () => openHelpdeskModal()
    })
  }
  return options
})

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

  // Fetch helpdesk ticket creation flag FIRST
  await new Promise((resolve) => {
    createResource({
      url: 'crm.api.messenger.is_helpdesk_ticket_creation_enabled',
      cache: 'Is Helpdesk Ticket Creation Enabled',
      auto: true,
      onSuccess: (data) => {
        enableHelpdeskTicketCreation.value = Boolean(data)
        resolve()
      },
      onError: () => resolve(), // resolve even if error
    })
  })

  // Now fetch conversations
  await conversationsResource.fetch()

  // Check if conversationId is in route params
  if (route.params.conversationId) {
    const conversation = conversations.value.find(c => c.name === route.params.conversationId)
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

// All available tags
const allTags = ref([])
// Tags selected for the current conversation
const selectedTags = ref([])
// Show all tags modal
const showAllTags = ref(false)
// Show add tag dropdown
const showAddTagDropdown = ref(false)

// Add a new ref for the search query
const tagSearchQuery = ref('')

// Fetch all tags on mount
async function fetchAllTags() {
  const tagsResource = createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: 'Messenger Tags',
      fields: ['tag_name', 'color'],
      order_by: 'tag_name asc',
    },
  })
  allTags.value = await tagsResource.fetch()
}

onMounted(() => {
  fetchAllTags()
})

// When a conversation is selected, fetch tags from backend
watch(selectedConversation, (val) => {
  fetchConversationTags(val)
})

// Fetch tags for a conversation from backend
async function fetchConversationTags(conversationName) {
  if (!conversationName) return
  try {
    const tags = await call('crm.api.messenger.get_conversation_tags', { conversation_name: conversationName })
    console.log("Tags  ==> ",tags)
    selectedTags.value = tags || []
  } catch (e) {
    selectedTags.value = []
  }
}

// Save tags for a conversation to backend
async function saveConversationTags() {
  if (!selectedConversation.value) return
  try {
    await call('crm.api.messenger.set_conversation_tags', {
      conversation_name: selectedConversation.value,
      tags: selectedTags.value
    })
  } catch (e) {
    // Optionally show error
  }
}

// Add tag to selectedTags and save to backend
async function addTag(tag) {
  if (!selectedTags.value.find(t => t.tag_name === tag.tag_name)) {
    selectedTags.value.push(tag)
    await saveConversationTags()
  }
  showAddTagDropdown.value = false
  tagSearchQuery.value = '' // Reset search
}

// Remove tag from selectedTags and save to backend
async function removeTag(tag) {
  selectedTags.value = selectedTags.value.filter(t => t.tag_name !== tag.tag_name)
  await saveConversationTags()
}

// Unselected tags for dropdown
const unselectedTags = computed(() => {
  return allTags.value.filter(tag => !selectedTags.value.find(t => t.tag_name === tag.tag_name))
})

// Add a map to store tags for each conversation
const conversationTags = ref({})

// Fetch tags for all conversations
async function fetchAllConversationTags() {
  if (!conversations.value?.length) return
  
  const promises = conversations.value.map(async (conv) => {
    try {
      const tags = await call('crm.api.messenger.get_conversation_tags', { conversation_name: conv.name })
      conversationTags.value[conv.name] = tags || []
    } catch (e) {
      conversationTags.value[conv.name] = []
    }
  })
  await Promise.all(promises)
}

// Fetch tags whenever conversations list changes
watch(() => conversations.value, () => {
  if (conversations.value?.length) {
    fetchAllConversationTags()
  }
}, { deep: true })

// Add this function in the script section
function shouldShowEllipsis(conversationName) {
  const tags = conversationTags.value[conversationName] || []
  if (!tags.length) return false
  
  // If there's only one tag and it's long, show ellipsis
  if (tags.length === 1 && tags[0].tag_name.length > 15) return true
  
  // If there are multiple tags, check if they overflow
  const container = document.querySelector('.overflow-hidden')
  if (!container) return false
  
  const tagElements = container.querySelectorAll('span:not(:last-child)')
  if (!tagElements.length) return false
  
  let totalWidth = 0
  tagElements.forEach(el => {
    totalWidth += el.offsetWidth
  })
  
  return totalWidth > container.offsetWidth - 20 // 20px buffer for ellipsis
}

// Add a map to store assignees for each conversation
const conversationAssignees = ref({})

// Fetch assignees for all conversations
async function fetchAllConversationAssignees() {
  if (!conversations.value?.length) return
  const promises = conversations.value.map(async (conv) => {
    try {
      const assigneesResource = createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'ToDo',
          fields: ['allocated_to'],
          filters: [
            ['reference_type', '=', 'Messenger Conversation'],
            ['reference_name', '=', conv.name],
            ['status', '=', 'Open']
          ]
        }
      })
      const assigneesList = await assigneesResource.fetch()
      if (!assigneesList.length) {
        conversationAssignees.value[conv.name] = []
        return
      }
      const userIds = [...new Set(assigneesList.map(a => a.allocated_to))]
      if (!userIds.length) {
        conversationAssignees.value[conv.name] = []
        return
      }
      const userDetailsResource = createResource({
        url: 'frappe.client.get_list',
        params: {
          doctype: 'User',
          fields: ['name', 'full_name', 'user_image'],
          filters: [['name', 'in', userIds]]
        }
      })
      const userDetails = await userDetailsResource.fetch()
      const userMap = Object.fromEntries(userDetails.map(user => [user.name, user]))
      conversationAssignees.value[conv.name] = assigneesList.map(a => ({
        name: a.allocated_to,
        image: userMap[a.allocated_to]?.user_image || null,
        label: userMap[a.allocated_to]?.full_name || a.allocated_to
      }))
    } catch (e) {
      conversationAssignees.value[conv.name] = []
    }
  })
  await Promise.all(promises)
}

// Fetch assignees whenever conversations list changes
watch(() => conversations.value, () => {
  fetchAllConversationAssignees()
})

// Add this computed property to filter unselected tags based on search query
const filteredUnselectedTags = computed(() => {
  if (!tagSearchQuery.value) return unselectedTags.value
  return unselectedTags.value.filter(tag =>
    tag.tag_name.toLowerCase().includes(tagSearchQuery.value.toLowerCase())
  )
})

const searchedTags = ref([])
const searching = ref(false)
let searchTimeout = null

// Debounce function
function debounce(fn, delay) {
  return (...args) => {
    if (searchTimeout) clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => fn(...args), delay)
  }
}

watch(tagSearchQuery, debounce(async (query) => {
  if (!query) {
    searching.value = false
    searchedTags.value = []
    return
  }
  searching.value = true
  // Fetch tags from backend matching the query, excluding already selected
  try {
    const tagsResource = createResource({
      url: 'frappe.client.get_list',
      params: {
        doctype: 'Messenger Tags',
        fields: ['tag_name', 'color'],
        filters: [
          ['tag_name', 'like', `%${query}%`]
        ],
        order_by: 'tag_name asc',
        limit_page_length: 10
      }
    })
    let tags = await tagsResource.fetch()
    // Exclude already selected
    tags = tags.filter(tag => !selectedTags.value.find(t => t.tag_name === tag.tag_name))
    searchedTags.value = tags
  } catch (e) {
    searchedTags.value = []
  }
}, 300))

const dropdownTags = computed(() => {
  if (searching.value && tagSearchQuery.value) {
    return searchedTags.value
  }
  // Default: first 10 unselected tags
  return unselectedTags.value.slice(0, 10)
})

// --- Helpdesk Ticket Creation Feature ---
const enableHelpdeskTicketCreation = vueRef(false)

// Modal state and form fields
const showHelpdeskModal = ref(false)
const helpdeskSubject = ref('')
const helpdeskDescription = ref('')
const helpdeskAttachments = ref([])
const helpdeskModalLoading = ref(false)

function openHelpdeskModal() {
  helpdeskSubject.value = ''
  helpdeskDescription.value = ''
  helpdeskAttachments.value = []
  showHelpdeskModal.value = true
}
function closeHelpdeskModal() {
  showHelpdeskModal.value = false
}
function submitHelpdeskTicket() {
  helpdeskModalLoading.value = true
  call('crm.api.messenger.create_helpdesk_ticket_from_messenger', {
    subject: helpdeskSubject.value,
    description: helpdeskDescription.value,
    conversation_id: selectedConversation.value,
    ticket_type: helpdeskTicketType.value
  })
    .then((r) => {
      showHelpdeskModal.value = false
      globalStore().$toast.success(__('Helpdesk ticket created successfully'))
      onTicketCreated()
    })
    .catch((err) => {
      globalStore().$toast.error(__('Failed to create helpdesk ticket'))
      console.error(err)
    })
    .finally(() => {
      helpdeskModalLoading.value = false
    })
}

const isSubmitDisabled = computed(() => {
  return (
    helpdeskModalLoading ||
    !helpdeskSubject.value.trim() ||
    !helpdeskDescription.value.trim() ||
    !helpdeskTicketType.value
  )
})

// Add after helpdeskDescription, helpdeskSubject, etc.
const helpdeskTicketType = ref('')

// Fetch ticket types on modal open
watch(showHelpdeskModal, async (val) => {
  if (val) {
    // Fetch ticket types
    try {
      const types = await call('frappe.client.get_list', {
        doctype: 'HD Ticket Type',
        fields: ['name', 'description'],
        order_by: 'name asc',
        limit_page_length: 100
      })
      // ticketTypeOptions.value = types.map(t => ({
      //   label: t.name + (t.description ? ` - ${t.description}` : ''),
      //   value: t.name
      // }))
      // if (ticketTypeOptions.value.length && !helpdeskTicketType.value) {
      //   helpdeskTicketType.value = ticketTypeOptions.value[0].value
      // }
    } catch (e) {
      // ticketTypeOptions.value = []
    }
  }
})

// Add computed property for latest ticket status
const selectedConversationLatestTicketStatus = computed(() => {
  const conversation = conversations.value.find(c => c.name === selectedConversation.value)
  return conversation?.latest_ticket_status || null
})

// Add ref for tickets and UI state
const pastTickets = ref([])
const showCreateTicketFields = ref(false)

// Fetch last 3 tickets for the selected conversation
async function fetchPastTickets() {
  console.log("selectedConversation.value",selectedConversation.value)
  console.log("enableHelpdeskTicketCreation.value",enableHelpdeskTicketCreation.value)
  if (!selectedConversation.value) return
  try {
    const tickets = await call('crm.api.messenger.get_last_tickets_for_conversation', {
      conversation_id: selectedConversation.value,
      limit: 3
    })
    pastTickets.value = tickets || []
  } catch (e) {
    pastTickets.value = []
  }
}

// Watch for modal open to fetch tickets
watch(showHelpdeskModal, (val) => {
  if (val) {
    fetchPastTickets()
    showCreateTicketFields.value = false
  }
})

// Real-time update: refetch tickets and status on ticket creation
function onTicketCreated() {
  fetchPastTickets()
  conversationsResource.reload()
}

// 1. Fetch past tickets when conversation is selected
watch(selectedConversation, (val) => {
  if (val) {
    fetchPastTickets()
  }
})

// 2. Make tickets in modal clickable, redirect to /helpdesk/tickets/<ticket-id>
function goToTicket(ticketId) {
  window.open(`/helpdesk/tickets/${ticketId}`, '_blank')
}

// Add a function to get status color and icon color
function getTicketStatusColor(status) {
  switch ((status || '').toLowerCase()) {
    case 'open':
      return { text: 'text-yellow-700', bg: 'bg-yellow-50', border: 'border-yellow-300', icon: 'text-yellow-500' }
    case 'replied':
      return { text: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-300', icon: 'text-blue-500' }
    case 'resolved':
      return { text: 'text-green-700', bg: 'bg-green-50', border: 'border-green-300', icon: 'text-green-500' }
    case 'closed':
      return { text: 'text-gray-700', bg: 'bg-gray-50', border: 'border-gray-300', icon: 'text-gray-500' }
    default:
      return { text: 'text-gray-700', bg: 'bg-gray-50', border: 'border-gray-300', icon: 'text-gray-500' }
  }
}

// Watch for route param changes to select conversation dynamically
watch(() => route.params.conversationId, async (newId) => {
  if (newId) {
    await fetchEnableHelpdeskTicketCreation()
    let conversation = conversations.value.find(c => c.name === newId)
    if (!conversation) {
      await conversationsResource.fetch()
      conversation = conversations.value.find(c => c.name === newId)
    }
    if (conversation) {
      await handleConversationSelect(conversation)
    }
  }
})

async function fetchEnableHelpdeskTicketCreation() {
  // Always fetch the latest flag before selecting a conversation
  try {
    const data = await call('crm.api.messenger.is_helpdesk_ticket_creation_enabled')
    enableHelpdeskTicketCreation.value = Boolean(data)
  } catch (e) {
    enableHelpdeskTicketCreation.value = false
  }
}
</script>

<style scoped>
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgb(var(--outline-gray-1)) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: rgb(var(--outline-gray-1));
  border-radius: 3px;
}

:deep(.crm-modal-tight .frappe-dialog) {
  border-radius: 16px !important;
  padding: 0 !important;
  max-width: 700px;
}
:deep(.crm-modal-tight .frappe-dialog__body) {
  padding: 0 !important;
}
</style> 