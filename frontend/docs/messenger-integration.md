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

#### Resource APIs Used
1. **Message Fetching**
   ```javascript
   createResource({
     url: 'frappe.client.get_list',
     doctype: 'Messenger Message',
     // Includes sender information handling
   })
   ```

2. **User Information Fetching**
   ```javascript
   createResource({
     url: 'frappe.client.get_list',
     doctype: 'Messenger User',
     // Maps user_id to username
   })
   ```

3. **Conversation Management**
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

### User Resolution
- Conversations display usernames by matching `sender_id` with `user_id`
- Fallback to `sender_id` if username is not found
- Caches user information to minimize API calls

### UI Components
- Left sidebar: Displays conversation list with resolved usernames
- Main area: Shows selected conversation messages with sender information
- Input area: Allows message composition and sending

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