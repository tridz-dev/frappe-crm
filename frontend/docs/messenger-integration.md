# Messenger Integration Documentation

## Overview
This document describes the integration between the CRM module and the `frappe-messenger` app, specifically focusing on the messenger functionality within the CRM interface.

## Technical Implementation

### Data Flow
- Messages are sourced from the `Messenger Message` DocType
- The integration uses Frappe UI Resource APIs for all data operations
- Messages are displayed in real-time in the chat conversation section

### Key Components

#### Resource APIs Used
1. **Message Fetching**
   ```javascript
   useResource({
     url: 'frappe.client.get_list',
     doctype: 'Messenger Message'
   })
   ```

2. **Message Sending**
   ```javascript
   useResource({
     url: 'frappe.client.insert',
     method: 'POST'
   })
   ```

3. **Conversation Management**
   ```javascript
   useResource({
     url: 'frappe.client.get_list',
     doctype: 'Messenger Conversation'
   })
   ```

### Message Handling
- Outgoing messages are created with `message_direction = "Outgoing"`
- Messages are automatically refreshed after sending
- Messages are ordered by timestamp in descending order

### UI Components
- Left sidebar: Displays conversation list
- Main area: Shows selected conversation messages
- Input area: Allows message composition and sending

## Dependencies
- Frappe UI library
- Vue.js 3
- Frappe Messenger DocTypes

## Limitations
- Messages are currently limited to text only
- Fetches latest 50 messages per conversation
- No real-time updates (polling-based)

## Future Improvements
1. Add real-time message updates using Frappe's socket.io integration
2. Implement message read status
3. Add support for media attachments
4. Add typing indicators

## Related Documentation
- [Frappe UI Documentation](https://ui.frappe.io/)
- [Vue Router Documentation](https://router.vuejs.org/) 