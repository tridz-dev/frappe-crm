# Socket Handling Improvements for Messenger Components

## Problem

After navigating between conversations or between the conversation list and detail views, socket events (real-time updates) would stop working in the sidebar (conversation list). This required a page refresh to restore real-time functionality.

### Root Causes
1. **Duplicate Event Listeners**: Socket listeners were being registered multiple times without proper cleanup
2. **Stale References**: Old event handlers remained active even after component updates
3. **Inconsistent Lifecycle Management**: Socket listeners were not reliably managed during Vue component lifecycle events

## Solution

### 1. Named Handler Functions
All socket event handlers are now defined as named functions at the component level:

```javascript
// MessengerLayout.vue
function onMessageUpdate(data) {
  // Handle message updates for conversation list
}

function onUnreadUpdate(data) {
  // Handle unread count updates
}

// MessengerDetail.vue  
function onMessageUpdate(data) {
  // Handle message updates for message section
}
```

### 2. Always Clean Up Before Registering
Both components now follow this pattern:

```javascript
function setupSocketListeners() {
  cleanupSocketListeners() // Always clean up first
  $socket.on('messenger:message_update', onMessageUpdate)
  // ... register other listeners
}

function cleanupSocketListeners() {
  $socket.off('messenger:message_update', onMessageUpdate)
  // ... remove other listeners using named handlers
}
```

### 3. Reliable Lifecycle Management
- **MessengerLayout.vue**: Listeners set up in `onMounted`, cleaned up in `onUnmounted`
- **MessengerDetail.vue**: Listeners set up in `onMounted`, cleaned up in `onBeforeUnmount`

## Technical Details

### MessengerLayout.vue Changes
- **Removed**: `socketListenersInitialized` flag and route-based listener toggling
- **Added**: Named handler functions for all socket events
- **Improved**: Always clean up listeners before re-registering
- **Result**: Sidebar socket events work consistently regardless of navigation

### MessengerDetail.vue Changes  
- **Added**: Named handler functions for message-specific socket events
- **Improved**: Consistent cleanup and registration pattern
- **Maintained**: All existing message handling logic
- **Result**: Message section socket events work reliably

### Socket Event Keys
Both components use the same socket event keys (`messenger:message_update`, `messenger:unread_update`, etc.) which is **correct and safe** when using proper listener management.

## Benefits

1. **No More Duplicate Listeners**: Each event has exactly one handler
2. **No Memory Leaks**: All listeners are properly cleaned up
3. **Consistent Real-time Updates**: Socket events work reliably after any number of navigations
4. **Maintainable Code**: Named functions make debugging and maintenance easier

## Usage

No changes required for end users. The improvements are transparent and ensure that:
- Real-time message updates work consistently
- Unread counts update properly in the sidebar
- Conversation list updates when new messages arrive
- No page refreshes are needed to restore functionality

## Developer Notes

- **Socket Connection**: The socket connection itself is managed by Frappe's socket.io integration
- **Event Propagation**: Multiple components can safely listen to the same socket events
- **Performance**: Named handlers allow for efficient listener removal and prevent memory leaks
- **Debugging**: Console logs are maintained for debugging socket event flow

## Testing

To verify the fix works:
1. Navigate to `/crm/messenger`
2. Select a conversation
3. Navigate to another conversation
4. Navigate back to the first conversation
5. Verify that real-time updates (new messages, unread counts) still work without page refresh 