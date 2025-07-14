# Real-time Update Improvements for Messenger Components

## Issues Fixed

### 1. Outgoing Messages Not Updating Sidebar
**Problem:** When sending outgoing messages, the conversation list (sidebar) was not updating with the new last message and timestamp.

**Root Cause:** The backend was not emitting the `messenger:message_sent` socket event for outgoing messages, and the frontend was not listening for this event.

### 2. Read Status Not Updating in Real-time
**Problem:** When opening a conversation and messages were marked as read, the unread count was not updating in real-time across all components.

**Root Cause:** The `mark_messages_as_read` function was emitting the correct event, but the frontend wasn't properly handling the unread count updates for the current conversation.

## Solutions Implemented

### Backend Changes (`messenger.py`)

#### 1. Enhanced Socket Event Emission for Outgoing Messages
```python
# Handle outgoing messages - emit message_sent event for sidebar updates
if doc.message_direction == "Outgoing":
    frappe.publish_realtime(
        "messenger:message_sent",
        {
            "conversation_id": doc.conversation,
            "message": doc.as_dict()
        }
    )
    
    # Also emit conversation update for sidebar
    conversation = frappe.get_doc("Messenger Conversation", doc.conversation)
    frappe.publish_realtime(
        "messenger:conversation_update",
        {
            "conversation": conversation.as_dict(),
            "type": "update"
        }
    )
```

**What this does:**
- Emits `messenger:message_sent` event when any outgoing message is sent
- Emits `messenger:conversation_update` to refresh conversation details in sidebar
- Ensures both the message and conversation data are updated in real-time

#### 2. Improved Event Structure
- **Before:** Only auto-generated outgoing messages were handled
- **After:** All outgoing messages trigger real-time updates
- **Result:** Sidebar updates immediately when any message is sent

### Frontend Changes

#### 1. MessengerLayout.vue - Added Message Sent Handler
```javascript
function onMessageSent(data) {
  console.log('Message sent event received in layout:', data)
  const conversationIndex = conversations.value.findIndex(c => c.name === data.conversation_id)
  if (conversationIndex !== -1) {
    // Update the conversation's last message and timestamp
    conversations.value[conversationIndex] = {
      ...conversations.value[conversationIndex],
      last_message: data.message.message,
      last_message_time: data.message.timestamp
    }
    
    // Re-sort conversations by last message time
    conversations.value.sort((a, b) => new Date(b.last_message_time) - new Date(a.last_message_time))
  }
}
```

**What this does:**
- Listens for `messenger:message_sent` events
- Updates the conversation's last message and timestamp in the sidebar
- Re-sorts conversations to show the most recent message first

#### 2. MessengerDetail.vue - Enhanced Unread Count Handling
```javascript
function onUnreadUpdate(data) {
  console.log('Unread update received in detail:', data)
  if (data.conversation_id === selectedConversation.value) {
    console.log('Unread count updated for current conversation:', data.unread_count)
    
    // If unread count is 0, mark all messages as read locally
    if (data.unread_count === 0) {
      messages.value.forEach(message => {
        if (message.message_direction === 'Incoming') {
          message.is_read = 1
        }
      })
    }
  }
}
```

**What this does:**
- Handles unread count updates for the current conversation
- When unread count becomes 0, marks all incoming messages as read locally
- Ensures UI reflects the correct read status immediately

## Socket Event Flow

### Outgoing Message Flow
1. **User sends message** → `handleSendMessage()` in MessengerDetail.vue
2. **Backend processes** → `send_message()` in messenger_message.py
3. **Socket event emitted** → `messenger:message_sent` with message data
4. **Sidebar updates** → `onMessageSent()` in MessengerLayout.vue updates conversation list
5. **Conversation re-sorts** → Most recent conversation appears at top

### Read Status Flow
1. **User opens conversation** → `markMessagesAsRead()` called
2. **Backend marks messages read** → `mark_messages_as_read()` in messenger_message.py
3. **Socket event emitted** → `messenger:unread_update` with new count
4. **All components update** → Sidebar and detail view update unread counts
5. **Local state updated** → Messages marked as read in current conversation

## Benefits

### 1. Immediate Sidebar Updates
- **Before:** Sidebar only updated on page refresh or conversation selection
- **After:** Sidebar updates instantly when any message is sent
- **Result:** Users see real-time conversation activity

### 2. Accurate Read Status
- **Before:** Read status was inconsistent between components
- **After:** Read status updates immediately across all components
- **Result:** Unread counts are always accurate

### 3. Better User Experience
- **Before:** Users had to refresh or navigate to see updates
- **After:** All updates happen in real-time
- **Result:** More responsive and intuitive interface

## Technical Details

### Socket Events Used
- `messenger:message_sent` - For outgoing message updates
- `messenger:message_update` - For incoming message updates
- `messenger:unread_update` - For read status updates
- `messenger:conversation_update` - For conversation detail updates

### Event Data Structure
```javascript
// messenger:message_sent
{
  conversation_id: "CONV-001",
  message: {
    name: "MSG-001",
    message: "Hello world",
    timestamp: "2024-01-01 12:00:00",
    // ... other message fields
  }
}

// messenger:unread_update
{
  conversation_id: "CONV-001",
  unread_count: 0
}
```

## Testing

To verify the improvements work:

1. **Send a message** from any conversation
2. **Verify sidebar updates** immediately with new last message and timestamp
3. **Open a conversation** with unread messages
4. **Verify unread count** becomes 0 and messages are marked as read
5. **Check other conversations** still show correct unread counts

## Backward Compatibility

- All existing socket events continue to work
- No breaking changes to existing functionality
- Enhanced events are additive, not replacing existing ones
- All existing features remain intact 