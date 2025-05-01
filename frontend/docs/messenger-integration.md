# Messenger Integration Documentation

## Overview
This document describes the integration between the CRM module and the `frappe-messenger` app, specifically focusing on the messenger functionality within the CRM interface.

## Technical Implementation

### Data Flow
- Messages are sourced from the `Messenger Message` DocType
- User information is fetched from the `Messenger User` DocType
- Conversations display usernames by matching `sender_id` with `user_id`
- The integration uses Frappe UI Resource APIs for all data operations

### Key Components

#### Message Fetching
```javascript
// Resource definition
const messagesResource = createResource({
  url: 'frappe.client.get_list',
  doctype: 'Messenger Message',
  auto: false // Don't fetch automatically
})

// Conversation selection handler
async function handleConversationSelect(conversation) {
  // Update selected conversation
  selectedConversation.value = conversation.name
  
  // Update message resource params
  messagesResource.params = {
    doctype: 'Messenger Message',
    fields: ['name', 'message', 'sender_id', 'sender_user', 'timestamp', 'message_direction', 'conversation'],
    filters: [['conversation', '=', conversation.name]],
    order_by: 'timestamp desc',
    limit: 50
  }
  
  // Fetch and display messages
  await messagesResource.reload()
  messages.value = messagesResource.data.reverse()
}
```

#### User Information Resolution
```javascript
createResource({
  url: 'frappe.client.get_list',
  doctype: 'Messenger User',
  // Maps user_id to username
})
```

#### Conversation Management
```javascript
createResource({
  url: 'frappe.client.get_list',
  doctype: 'Messenger Conversation',
  // Includes user information resolution
})
```

### Message Handling
- Outgoing messages are created with `message_direction = "Outgoing"`
- Messages are automatically refreshed after sending
- Messages are ordered by timestamp in descending order
- Sender information is resolved using `Messenger User` doctype
- Messages are fetched when a conversation is selected

### User Resolution
- Conversations display usernames by matching `sender_id` with `user_id`
- Fallback to `sender_id` if username is not found
- Caches user information to minimize API calls

### UI Components
- Left sidebar: Displays conversation list with resolved usernames
- Main area: Shows selected conversation messages with sender information
- Input area: Allows message composition and sending

### Event Flow
1. User clicks on a conversation
2. `handleConversationSelect` is called
3. Message resource parameters are updated
4. Messages are fetched and displayed
5. View scrolls to latest message

## Dependencies
- Frappe UI library
- Vue.js 3
- Frappe Messenger DocTypes:
  - Messenger Message
  - Messenger User
  - Messenger Conversation

## Limitations
- Messages are currently limited to text only
- Fetches latest 50 messages per conversation
- No real-time updates (polling-based)
- User information is fetched on-demand

## Future Improvements
1. Add real-time message updates using Frappe's socket.io integration
2. Implement message read status
3. Add support for media attachments
4. Add typing indicators
5. Implement user information caching
6. Add user presence indicators

## Related Documentation
- [Frappe UI Documentation](https://ui.frappe.io/)
- [Vue Router Documentation](https://router.vuejs.org/) 