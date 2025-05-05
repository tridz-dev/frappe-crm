# Real-time Messenger Updates

This document describes how real-time updates work in the Messenger module of the CRM application.

## Overview

The Messenger module uses document events and WebSocket connections to provide real-time updates for:
- New messages
- Conversation updates
- Unread message counts

## Implementation

### Backend Components

1. **Document Events**
   - Located in `crm/hooks.py`
   - Registers events for Messenger Message:
     ```python
     "Messenger Message": {
         "validate": ["crm.api.messenger.validate"],
         "on_update": ["crm.api.messenger.on_update"]
     }
     ```

2. **Messenger API Handler**
   - Located in `crm/api/messenger.py`
   - Handles document events and emits real-time updates
   - Key functions:
     - `validate`: Sets up conversation for new messages
     - `on_update`: Emits real-time events
     - `get_or_create_conversation`: Manages conversation creation
   - Emits three types of events:
     - `messenger:conversation_update`: When conversation details change
     - `messenger:message_update`: When new messages arrive
     - `messenger:unread_update`: When unread counts change

### Frontend Components

1. **Messenger.vue**
   - Uses global socket instance from `globalStore`
   - Handles three types of updates:
     ```javascript
     // Socket event listeners
     const { $socket } = globalStore()

     // Conversation updates
     $socket.on('messenger:conversation_update', (data) => {
       // Updates conversation list and sorts by last message time
     })

     // New messages
     $socket.on('messenger:message_update', (data) => {
       // Adds new messages to current conversation
       // Auto-scrolls to bottom
     })

     // Unread counts
     $socket.on('messenger:unread_update', (data) => {
       // Updates unread message counts
     })
     ```

## Event Flow

1. New Messenger Message is created/updated
2. Document events (`validate`/`on_update`) are triggered
3. Events handler processes the message and manages conversations
4. Real-time events are emitted via WebSocket
5. Frontend receives events and updates UI in real-time

## Benefits

- Instant message updates without page refresh
- Real-time conversation list updates
- Live unread message count updates
- Improved user experience with immediate feedback
- Better integration with Frappe's document lifecycle
- Consistent with WhatsApp implementation
- Automatic conversation management
- Efficient unread count tracking

## Error Handling

- Backend logs errors in `Messenger Update Error` log
- Frontend gracefully handles missing or invalid data
- Socket connection errors are automatically handled by Frappe UI
- Fallback to polling for unread counts every 30 seconds

## Dependencies

- Frappe Document Events
- Frappe Socket IO
- Frappe UI Socket implementation
- Messenger Settings configuration
- Global Store for socket management 