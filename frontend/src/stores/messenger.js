import { defineStore } from 'pinia'
import { createResource, call } from 'frappe-ui'

export const useMessengerStore = defineStore('messenger', {
  state: () => ({
    conversations: [],
    userProfiles: {},
    conversationTags: {},
    conversationAssignees: {},
    unreadMessageCounts: {},
    loading: false,
    hasMoreConversations: true,
    conversationPage: 0,
    list: null,
    platformFilter: 'all',
  }),

  getters: {
    filteredConversations(state) {
      if (state.platformFilter === 'all') {
        return state.conversations
      }
      return state.conversations.filter(
        (conv) => conv.platform?.toLowerCase() === state.platformFilter.toLowerCase()
      )
    },
  },

  actions: {
    async fetchConversations(loadMore = false) {
      if (this.loading) return
      this.loading = true

      if (!loadMore) {
        this.conversationPage = 0
        this.hasMoreConversations = true
      }

      try {
        const response = await call('crm.api.messenger.get_conversations_with_details', {
          limit: 20,
          offset: this.conversationPage * 20,
          platform_filter: this.platformFilter,
          filters: this.list?.data?.params?.filters || {}
        })

        if (response && response.conversations) {
          if (loadMore) {
            this.conversations = [...this.conversations, ...response.conversations]
          } else {
            this.conversations = response.conversations
          }
          
          Object.assign(this.userProfiles, response.user_profiles || {})
          Object.assign(this.conversationTags, response.conversation_tags || {})
          Object.assign(this.conversationAssignees, response.conversation_assignees || {})
          Object.assign(this.unreadMessageCounts, response.unread_counts || {})

          this.hasMoreConversations = response.conversations.length === 20
          if (this.hasMoreConversations) {
            this.conversationPage++
          }
        }
      } catch (error) {
        console.error('Failed to fetch conversations:', error)
      } finally {
        this.loading = false
      }
    },
    
    refreshConversationList() {
      this.fetchConversations(false)
    },

    updateFilters(filters) {
      if (!this.list) {
        this.list = {
          data: { params: { doctype: 'Messenger Conversation', filters: {} } },
          params: { doctype: 'Messenger Conversation', filters: {} }
        }
      }
      this.list.data.params.filters = filters
      this.list.params.filters = filters
      this.refreshConversationList()
    },

    updatePlatformFilter(platform) {
      this.platformFilter = platform
      this.refreshConversationList()
    },

    handleMessageUpdate(data) {
        if (data.type === 'new') {
            const index = this.conversations.findIndex(c => c.name === data.conversation_id)
            if (index !== -1) {
                this.conversations[index].last_message = data.message.message
                this.conversations[index].last_message_time = data.message.timestamp
                this.conversations.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
            } else {
                this.refreshConversationList()
            }
        }
    },
    
    handleConversationUpdate(data) {
        if (data.type === 'update') {
            const index = this.conversations.findIndex(c => c.name === data.conversation.name)
            if (index !== -1) {
                this.conversations[index] = {
                    ...this.conversations[index],
                    ...data.conversation
                }
            } else {
                this.refreshConversationList()
            }
        }
    },

    handleStatusUpdate(data) {
      const index = this.conversations.findIndex(c => c.name === data.conversation_id)
      if (index !== -1) {
        this.conversations[index].status = data.status
      } else {
        this.refreshConversationList()
      }
    },

    handleUnreadUpdate(data) {
        if(data.conversation_id) {
            this.unreadMessageCounts[data.conversation_id] = data.unread_count
        }
    }
  },
}) 