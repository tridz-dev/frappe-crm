<template>
  <div class="flex-1 flex flex-col h-full min-h-0">
    <template v-if="conversationLoading">
      <div class="flex-1 flex items-center justify-center">
        <span class="text-ink-gray-4 text-lg">{{ __('Loading conversation...') }}</span>
      </div>
    </template>
    <template v-else-if="selectedConversation && currentConversation">
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
        class="flex-1 overflow-y-auto p-4 min-h-0"
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
            <!-- Items for this date (reversed) -->
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
        <!-- Dummy div for scroll anchor -->
        <div ref="bottomAnchor"></div>
      </div>
      <!-- Message Input -->
      <MessengerBox
        :conversation="selectedConversation"
        v-model:reply="reply"
        @send="handleSendMessage"
      />
    </template>
    <template v-else>
      <div class="flex-1 grid place-items-center bg-surface-gray-1">
        <div class="text-center">
          <div class="mx-auto h-12 w-12 text-ink-gray-2">
            <MessengerIcon />
          </div>
          <h3 class="mt-2 text-sm font-medium text-ink-gray-9">{{ __('No conversation selected') }}</h3>
          <p class="mt-1 text-sm text-ink-gray-3">{{ __('Choose a conversation to start messaging') }}</p>
        </div>
      </div>
    </template>
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
import { nextTick, ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createResource, call } from 'frappe-ui'
import { Button, Avatar, Dropdown, Tooltip, TextEditor, Dialog, FormControl } from 'frappe-ui'
import MessengerArea from '@/components/MessengerArea.vue'
import MessengerBox from '@/components/MessengerBox.vue'
import MessengerIcon from '@/components/Icons/Messenger.vue'
import ChevronDownIcon from '@/components/Icons/ChevronDownIcon.vue'
import AssignTo from '@/components/AssignTo.vue'
import MoreVerticalIcon from '@/components/Icons/MoreVerticalIcon.vue'
import TicketIcon from '@/components/Icons/TicketIcon.vue'
import Link from '@/components/Controls/Link.vue'
import { createToast } from '@/utils'
import StatusIcon from '@/components/Icons/StatusIcon.vue'
import CheckCircleIcon from '@/components/Icons/CheckCircleIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { markRaw } from 'vue'
import { globalStore } from '@/stores/global'

const route = useRoute()
const router = useRouter()
const { $socket } = globalStore()

// --- State ---
const selectedConversation = ref(null)
const conversationLoading = ref(false)
const messages = ref([])
const messagesLoading = ref(false)
const reply = ref({})
const assignees = ref([])
const statusOptions = ref([])
const currentStatus = ref('')
const showAllTags = ref(false)
const showAddTagDropdown = ref(false)
const tagSearchQuery = ref('')
const selectedTags = ref([])
const allTags = ref([])
const unselectedTags = computed(() => allTags.value.filter(tag => !selectedTags.value.find(t => t.tag_name === tag.tag_name)))

// --- Tag Search Logic (frontend-only, no backend calls) ---
const dropdownTags = computed(() => {
  if (!tagSearchQuery.value) {
    return unselectedTags.value.slice(0, 10)
  }
  // Filter unselected tags by search query (case-insensitive)
  return unselectedTags.value.filter(tag =>
    tag.tag_name.toLowerCase().includes(tagSearchQuery.value.toLowerCase())
  ).slice(0, 10)
})

const showHelpdeskModal = ref(false)
const helpdeskSubject = ref('')
const helpdeskDescription = ref('')
const helpdeskTicketType = ref('')
const helpdeskModalLoading = ref(false)
const showCreateTicketFields = ref(false)
const pastTickets = ref([])
const selectedConversationLatestTicketStatus = ref(null)
const currentConversation = ref(null)
const statusUpdates = ref([])
const enableHelpdeskTicketCreation = ref(false)
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

// Add conversation cache
const conversationCache = ref(new Map())

const messagePageLimit = 20
let hasMoreMessages = ref(true)

// --- Status Resource (same as Messenger.vue) ---
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

// --- Status Change Handler (same as Messenger.vue) ---
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
    createToast({
      title: __('Status updated successfully'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
    // Don't reload all messages, just update the status
    // fetchConversation(selectedConversation.value) - REMOVED
  } catch (error) {
    createToast({
      title: __('Failed to update status'),
      icon: 'x',
      iconClasses: 'text-ink-red-4',
    })
  }
}

// --- Action Menu (with icons, ticket logic, same as Messenger.vue) ---
const conversationMenuOptions = computed(() => {
  const hasTickets = pastTickets.value.length > 0
  let latestStatus = null
  if (hasTickets) {
    latestStatus = pastTickets.value[0]?.status || null
  }
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
      onClick: () => showHelpdeskModal.value = true
    })
  }
  return options
})

// --- Assignees (same logic as Messenger.vue) ---
async function fetchAssignees(conversationId) {
  // This function is now handled by get_conversation_details API
  // console.log('fetchAssignees is deprecated, use get_conversation_details instead')
}

// --- Message & Status Log Ordering (interleaved, same as Messenger.vue) ---
const groupedTimeline = computed(() => {
  if (!messages.value || !Array.isArray(messages.value)) return {}
  const allItems = [
    ...messages.value.map(msg => ({ ...msg, type: 'message', timestamp: msg.timestamp })),
    ...statusUpdates.value.map(update => ({ ...update, type: 'status', timestamp: update.changed_on }))
  ].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
  const groups = {}
  allItems.forEach(item => {
    if (!item.timestamp) return
    const dateObj = new Date(item.timestamp)
    const dateKey = dateObj.toDateString()
    if (!groups[dateKey]) groups[dateKey] = []
    groups[dateKey].push(item)
  })
  return groups
})

// --- Tag Management (same as Messenger.vue) ---
async function fetchAllTags() {
  // This function is now handled by get_cached_data API
  // console.log('fetchAllTags is deprecated, use get_cached_data instead')
}
async function fetchConversationTags(conversationId) {
  // This function is now handled by get_conversation_details API
  // console.log('fetchConversationTags is deprecated, use get_conversation_details instead')
}
async function saveConversationTags() {
  if (!selectedConversation.value) return
  try {
    await call('crm.api.messenger.set_conversation_tags', {
      conversation_name: selectedConversation.value,
      tags: selectedTags.value
    })
  } catch (e) {}
}
async function addTag(tag) {
  if (!selectedTags.value.find(t => t.tag_name === tag.tag_name)) {
    selectedTags.value.push(tag)
    await saveConversationTags()
  }
  showAddTagDropdown.value = false
  tagSearchQuery.value = ''
}
async function removeTag(tag) {
  selectedTags.value = selectedTags.value.filter(t => t.tag_name !== tag.tag_name)
  await saveConversationTags()
}

// --- Ticket Modal Logic (same as Messenger.vue) ---
function openHelpdeskModal() {
  helpdeskSubject.value = ''
  helpdeskDescription.value = ''
  showHelpdeskModal.value = true
}
function closeHelpdeskModal() {
  showHelpdeskModal.value = false
  showCreateTicketFields.value = false
  helpdeskSubject.value = ''
  helpdeskDescription.value = ''
  helpdeskTicketType.value = ''
}
async function submitHelpdeskTicket() {
  if (!helpdeskSubject.value || !helpdeskTicketType.value) {
    createToast('error', __('Subject and Ticket Type are required.'))
    return
  }
  helpdeskModalLoading.value = true
  try {
    await call('crm.api.messenger.create_helpdesk_ticket_from_messenger', {
      subject: helpdeskSubject.value,
      description: helpdeskDescription.value,
      conversation_id: selectedConversation.value,
      ticket_type: helpdeskTicketType.value
    })
    createToast({
      title: __('Helpdesk ticket created successfully'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
    closeHelpdeskModal()
    // Fetch latest tickets after creating new one
    fetchPastTickets(selectedConversation.value)
  } catch (e) {
    createToast({
      title: __('Failed to create helpdesk ticket'),
      icon: 'x',
      iconClasses: 'text-ink-red-4',
    })
  } finally {
    helpdeskModalLoading.value = false
  }
}
function goToTicket(ticketId) {
  window.open(`/helpdesk/tickets/${ticketId}`, '_blank')
}

// --- Fetch Messages (latest batch, like Messenger.vue) ---
async function fetchMessages(conversationId) {
  // This function is now handled by get_conversation_details API
  // Keeping for backward compatibility but it's no longer used
  // console.log('fetchMessages is deprecated, use get_conversation_details instead')
}

// --- Infinite Scroll: Load More Messages (like Messenger.vue) ---
async function loadMoreMessages() {
  if (!hasMoreMessages.value || messagesLoading.value || !selectedConversation.value) return
  messagesLoading.value = true
  try {
    const firstMessageTimestamp = messages.value[0]?.timestamp
    if (!firstMessageTimestamp) {
      messagesLoading.value = false
      return
    }
    // Fetch older messages using paginated API
    const data = await call('crm.api.messenger.get_conversation_details', {
      conversation_id: selectedConversation.value,
      limit: messagePageLimit,
      before: firstMessageTimestamp
    })
    const olderMessages = (data && data.messages) ? data.messages.reverse() : []
    // Only prepend messages that are not already in the list
    const existingNames = new Set(messages.value.map(m => m.name))
    const newMessages = olderMessages.filter(m => !existingNames.has(m.name))
    if (newMessages.length > 0) {
      const scrollElement = messagesContainer.value
      const oldScrollHeight = scrollElement.scrollHeight
      const oldScrollTop = scrollElement.scrollTop
      messages.value = [...newMessages, ...messages.value]
      hasMoreMessages.value = newMessages.length === messagePageLimit
      setTimeout(() => {
        const newScrollHeight = scrollElement.scrollHeight
        scrollElement.scrollTop = oldScrollTop + (newScrollHeight - oldScrollHeight)
      }, 100)
    } else {
      hasMoreMessages.value = false
    }
  } catch (error) {
    hasMoreMessages.value = false
  } finally {
    messagesLoading.value = false
  }
}

// --- Fetch Conversation Details ---
async function fetchConversation(conversationId) {
  // console.log('fetchConversation called with:', conversationId)
  if (!conversationId) {
    selectedConversation.value = null
    currentConversation.value = null
    return
  }
  conversationLoading.value = true
  try {
    // Check cache first
    if (conversationCache.value.has(conversationId)) {
      const cachedData = conversationCache.value.get(conversationId)
      selectedConversation.value = cachedData.conversation.name
      currentConversation.value = cachedData.conversation
      currentStatus.value = cachedData.conversation.status || ''
      selectedConversationLatestTicketStatus.value = cachedData.conversation.latest_ticket_status || null
      messages.value = cachedData.messages || []
      selectedTags.value = cachedData.tags || []
      assignees.value = cachedData.assignees || []
      statusUpdates.value = cachedData.status_updates || []
      pastTickets.value = cachedData.past_tickets || []
      allTags.value = cachedData.all_tags || []
      enableHelpdeskTicketCreation.value = cachedData.helpdesk_enabled || false
      // console.log('Loaded conversation from cache')
      return
    }
    
    // Fetch all conversation details in a single API call (first page)
    const data = await call('crm.api.messenger.get_conversation_details', {
      conversation_id: conversationId,
      limit: messagePageLimit
    })
    
    if (data) {
      selectedConversation.value = data.conversation.name
      currentConversation.value = data.conversation
      currentStatus.value = data.conversation.status || ''
      selectedConversationLatestTicketStatus.value = data.conversation.latest_ticket_status || null
      messages.value = (data.messages || []).reverse()
      // Mark as read if there are unread incoming messages
      if (messages.value.some(m => m.message_direction === 'Incoming' && !m.is_read)) {
        markMessagesAsRead(conversationId)
      }
      selectedTags.value = data.tags || []
      assignees.value = data.assignees || []
      statusUpdates.value = data.status_updates || []
      pastTickets.value = data.past_tickets || []
      
      // Load cached data for tags and helpdesk flag
      const cachedData = await call('crm.api.messenger.get_cached_data')
      if (cachedData) {
        allTags.value = cachedData.all_tags || []
        enableHelpdeskTicketCreation.value = cachedData.helpdesk_enabled || false
      }
      
      // Cache the conversation data
      conversationCache.value.set(conversationId, {
        conversation: data.conversation,
        messages: data.messages,
        tags: data.tags,
        assignees: data.assignees,
        status_updates: data.status_updates,
        past_tickets: data.past_tickets,
        all_tags: allTags.value,
        helpdesk_enabled: enableHelpdeskTicketCreation.value
      })
      
      // console.log('All data fetched successfully')
    }
  } catch (err) {
    console.error('Error fetching conversation:', err)
    selectedConversation.value = null
    currentConversation.value = null
    messages.value = []
  } finally {
    conversationLoading.value = false
  }
}

// --- Past Tickets ---
async function fetchPastTickets(conversationId) {
  try {
    const data = await call('crm.api.messenger.get_last_tickets_for_conversation', {
      conversation_id: conversationId,
      limit: 3
    })
    pastTickets.value = data || []
  } catch (e) {
    pastTickets.value = []
  }
}

// --- Fetch Helpdesk Ticket Creation Flag ---
async function fetchEnableHelpdeskTicketCreation() {
  // This function is now handled by get_cached_data API
  // console.log('fetchEnableHelpdeskTicketCreation is deprecated, use get_cached_data instead')
}

// --- Format Time Ago Function ---
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

// --- Watchers ---
watch(() => route.params.conversationId, (conversationId) => {
  // console.log('Route changed, conversationId:', conversationId)
  selectedConversation.value = conversationId || null
  fetchConversation(conversationId)
}, { immediate: true })

// Add watcher to track selectedConversation changes for debugging
watch(selectedConversation, (newVal) => {
  // console.log('selectedConversation changed to:', newVal)
}, { immediate: true })

// --- Fix: Scroll to bottom when messages are loaded for a new conversation ---
watch([
  () => selectedConversation.value,
  () => conversationLoading.value
], ([convId, loading], [oldConvId, oldLoading]) => {
  // When conversation changes and loading just finished
  if (convId && oldLoading && !loading) {
    nextTick(() => {
      scrollToBottom()
    })
  }
}, { immediate: false })

// --- Message Order & Scroll ---
const messagesContainer = ref(null)
const bottomAnchor = ref(null)
function scrollToBottom() {
  setTimeout(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  }, 200) // Increased delay to ensure DOM is ready
}

// --- SOCKET HANDLERS FOR MESSAGE SECTION ---
function onMessageUpdate(data) {
  console.log('Message update received in detail:', data)
  if (data.conversation_id === selectedConversation.value) {
    if (data.type === 'new') {
      // Add new message to the end
      messages.value.push(data.message)
      scrollToBottom()
      
      // Mark as read if it's an incoming message
      if (data.message.message_direction === 'Incoming' && !data.message.is_read) {
        markMessagesAsRead(selectedConversation.value)
      }
    }
  }
}

function onMessageSent(data) {
  // console.log('Message sent event received in detail: autoooo ', data)
  if (data.conversation_id === selectedConversation.value) {
    // Update the sent message in the list
    const messageIndex = messages.value.findIndex(m => m.name === data.message.name)
    if (messageIndex !== -1) {
      messages.value[messageIndex] = data.message
    } else {
      // If not found, add it
      messages.value.push(data.message)
    }
    scrollToBottom()
  }
}

function onUnreadUpdate(data) {
  // console.log('Unread update received in detail:', data)
  if (data.conversation_id === selectedConversation.value) {
    // Update unread count for current conversation
    // This is handled by the layout, but we can update local state if needed
    // console.log('Unread count updated for current conversation:', data.unread_count)
    
    // If unread count is 0, we can update any local state that tracks unread messages
    if (data.unread_count === 0) {
      // Mark all messages in the current conversation as read locally
      messages.value.forEach(message => {
        if (message.message_direction === 'Incoming') {
          message.is_read = 1
        }
      })
    }
  }
}

function setupMessageSocketListeners() {
  cleanupMessageSocketListeners() // Always clean up first to avoid duplicates
  $socket.on('messenger:message_update', onMessageUpdate)
  $socket.on('messenger:message_auto_sent', onMessageSent)
  $socket.on('messenger:unread_update', onUnreadUpdate)
}

function cleanupMessageSocketListeners() {
  $socket.off('messenger:message_update', onMessageUpdate)
  $socket.off('messenger:message_auto_sent', onMessageSent)
  $socket.off('messenger:unread_update', onUnreadUpdate)
}

onMounted(() => {
  setupMessageSocketListeners()
  
  window.addEventListener('keydown', handleEscKey)
  
  // Only handle conversation updates for the current conversation
  $socket.on('messenger:conversation_update', (data) => {
    // console.log('Conversation update received in detail view:', data, 'Current conversation:', selectedConversation.value)
    if (data.type === 'update' && selectedConversation.value === data.conversation.name) {
      // console.log('Processing conversation update for current conversation')
      // Update conversation details if it's the current one
      currentConversation.value = {
        ...currentConversation.value,
        ...data.conversation
      }
    } else {
      console.log('Conversation update for different conversation, ignoring')
    }
  })

  $socket.on('messenger:message_status_update', (data) => {
    // console.log('Message status update received:', data)
    if (data.message_id) {
      const messageIndex = messages.value.findIndex(m => m.name === data.name)
      if (messageIndex !== -1) {
        messages.value[messageIndex].status = data.status
      }
    }
  })

  $socket.on('messenger:conversation_status_update', (data) => {
    // console.log('Conversation status update received:', data, 'Current conversation:', selectedConversation.value)
    if (data.conversation_id === selectedConversation.value) {
      // console.log('Processing status update for current conversation')
      currentStatus.value = data.status
      if (data.status_log) {
        statusUpdates.value.push(data.status_log)
      }
    } else {
      console.log('Status update for different conversation, ignoring')
    }
  })
})

onBeforeUnmount(() => {
  cleanupMessageSocketListeners()
  
  window.removeEventListener('keydown', handleEscKey)
  
  // Clean up socket event listeners
  $socket.off('messenger:conversation_update')
  $socket.off('messenger:message_status_update')
  $socket.off('messenger:conversation_status_update')
})

function handleEscKey(e) {
  if (e.key === 'Escape' || e.key === 'Esc') {
    router.push({ name: 'MessengerList' })
  }
}
// --- UI Computed ---
const selectedConversationTitle = computed(() => currentConversation.value?.sender_name || currentConversation.value?.name || '')
const selectedConversationProfile = computed(() => currentConversation.value?.profile || null)
const selectedConversationPlatform = computed(() => {
  if (!currentConversation.value?.platform) return ''
  switch (currentConversation.value.platform) {
    case 'Messenger': return 'Facebook Messenger'
    case 'Instagram': return 'Instagram DM'
    default: return `${currentConversation.value.platform} DM`
  }
})
function formatDate(dateString) {
  const date = new Date(dateString)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.toDateString() === today.toDateString()) {
    return 'Today'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return 'Yesterday'
  } else {
    return date.toLocaleDateString()
  }
}

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

function getStatusIcon(status) {
  switch (status) {
    case 'Open':
      return 'TicketIcon'
    case 'Replied':
      return 'TicketIcon'
    case 'Resolved':
      return 'TicketIcon'
    case 'Closed':
      return 'TicketIcon'
    default:
      return 'TicketIcon'
  }
}

function getStatusColor(status) {
  switch (status) {
    case 'Open':
      return 'text-yellow-700'
    case 'Replied':
      return 'text-blue-700'
    case 'Resolved':
      return 'text-green-700'
    case 'Closed':
      return 'text-gray-700'
    default:
      return 'text-gray-700'
  }
}

function handleReply(reply) {
  messages.value.push(reply)
  scrollToBottom()
}

// --- Scroll Handler (trigger loadMoreMessages) ---
function handleMessagesScroll(e) {
  const el = e.target
  if (el.scrollTop <= 100) {
    loadMoreMessages()
  }
}

// --- Message Sending Resource (same as Messenger.vue) ---
const sendMessageResource = createResource({
  url: 'frappe.client.insert',
  method: 'POST',
  onSuccess: () => {
    fetchMessages(selectedConversation.value)
  }
})

function getCurrentConversation() {
  if (!selectedConversation.value) return null
  return currentConversation.value
}

// --- Send Message (same as Messenger.vue) ---
async function handleSendMessage(messageData) {
  const conv = getCurrentConversation()
  if (!conv) return

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
    recipient_id: conv.sender_id,
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
    
    // Add message to local messages array
    messages.value.push({
      ...newMessage,
      name: response.name
    })
    
    // Emit socket event to update conversation list in real-time
    // $socket.emit('messenger:message_sent', {
    //   conversation_id: selectedConversation.value,
    //   message: {
    //     ...newMessage,
    //     name: response.name
    //   }
    // })
    
    // Scroll to bottom after sending message
    setTimeout(() => {
      scrollToBottom()
    }, 100)
  } catch (error) {
    createToast('Failed to send message')
  }
}
// --- Message Marking Resource (same as Messenger.vue) ---
const markMessagesAsReadResource = createResource({
  url: 'frappe_messenger.frappe_messenger.doctype.messenger_message.messenger_message.mark_messages_as_read',
  onSuccess: (response) => {
    // console.log('markMessagesAsReadResource success:', response)
    // console.log('selectedConversation.value:', selectedConversation.value)
    if (selectedConversation.value) {
      // Update unread count if needed
      // console.log('Messages marked as read, unread count:', response)
    }
  }
})

// --- Mark Messages as Read (same as Messenger.vue) ---
async function markMessagesAsRead(conversationId) {
  try {
    await markMessagesAsReadResource.submit({
      conversation: conversationId
    })
  } catch (error) {
    console.error('Failed to mark messages as read:', error)
  }
}

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
      createToast('No lead found for this conversation')
    }
  } catch (error) {
    createToast('Failed to fetch lead information')
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
    createToast('Chat blocked successfully')
    router.push({ name: 'MessengerList' })
  } catch (error) {
    createToast('Failed to block chat')
  }
}

async function fetchStatusUpdates(conversationId) {
  // This function is now handled by get_conversation_details API
  console.log('fetchStatusUpdates is deprecated, use get_conversation_details instead')
}
</script>

<style scoped>
.flex-1 {
  flex: 1 1 0%;
  min-height: 0;
}
.h-full {
  height: 100%;
}
</style> 