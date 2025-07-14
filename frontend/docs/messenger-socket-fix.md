# Messenger Socket Event Listener Fix

## Issue Description

The socket event listeners in the conversation list section were not working after selecting a conversation and then navigating back to the conversation list. Additionally, the last message and real-time updates were not working properly. The issues were:

1. Socket events for conversation updates, unread counts, and block status updates were only working when the page was first loaded
2. Last message updates were not happening in real-time
3. Real-time updates when sending outgoing messages were not working
4. Conversation list was not updating immediately after sending messages
5. Unread count was not updating when messages were marked as read
6. Outgoing message updates were not reflected in the conversation list
7. **NEW ISSUE**: When switching between conversations, socket events were not working properly because conversation ID tracking was not updating correctly

## Root Cause Analysis

### 1. Router Structure
- `MessengerLayout.vue` is the parent component that contains the conversation list
- `MessengerDetail.vue` is a child component that shows conversation details
- `MessengerPlaceholder.vue` is shown when no conversation is selected

### 2. Component Lifecycle Problem
- `MessengerLayout.vue` stays mounted when navigating to conversation details, but its socket event listeners were being set up in `onMounted()` without proper cleanup
- When navigating back to the conversation list, the `onMounted()` would run again, adding duplicate socket event listeners, which caused conflicts

### 3. Conversation ID Tracking Issue
- The `selectedConversation` ref was not properly synchronized between parent and child components
- When switching between conversations, the socket events were not being applied to the correct conversation because the conversation ID tracking was not updating properly

### 4. Missing Socket Event Listeners
- The `messenger:message_update` listener was missing in `MessengerLayout.vue`
- The `messenger:message_sent` listener was missing for outgoing message updates
- The `messenger:message_status_update` listener was missing for message status updates

## Solutions Implemented

### 1. **Fixed Socket Event Listener Management**
- Added proper tracking of socket listener initialization with `socketListenersInitialized` ref
- Added `setupSocketListeners()` and `cleanupSocketListeners()` functions
- Prevented duplicate listeners by checking if already initialized

### 2. **Added Missing Socket Event Listeners**
- Added `messenger:message_update` listener in `MessengerLayout.vue` for real-time message updates
- Added `messenger:message_sent` listener for outgoing message updates
- Added `messenger:message_status_update` listener for message status updates
- Added `messenger:conversation_status_update` listener for conversation status updates

### 3. **Fixed Conversation ID Tracking**
- Added watcher to track current conversation from route in `MessengerLayout.vue`
- Added watcher to track `selectedConversation` changes in `MessengerDetail.vue`
- Ensured proper synchronization between parent and child components

### 4. **Improved Conversation List Updates**
- Added proper conversation sorting after updates
- Added user profile fetching for new conversations
- Added proper handling of new conversations in the list

### 5. **Added Real-time Message Sending**
- Updated `handleSendMessage` function to emit socket events
- Added immediate conversation list updates when sending messages
- Added proper message status tracking

### 6. **Added Unread Count Handling**
- Added `messenger:unread_update` listener for real-time unread count updates
- Added proper unread count tracking for all conversations
- Added unread count updates when messages are marked as read

### 7. **Added Conversation Switching Support**
- Added `refreshConversationList()` function to refresh data when switching conversations
- Added proper conversation ID tracking with route watchers
- Added debugging logs to track conversation switching

## Backend Changes

### 1. **Added New Socket Events**
- Added `messenger:message_sent` event for outgoing messages
- Added `messenger:message_status_update` event for message status updates
- Added `messenger:conversation_status_update` event for conversation status updates

### 2. **Added New API Functions**
- Added `mark_messages_as_read()` function for marking messages as read
- Added `handle_incoming_message()` function for handling incoming messages
- Added `test_socket_events()` function for testing socket events

## Testing

### 1. **Test Conversation Switching**
1. Navigate to `/messenger`
2. Select a conversation
3. Switch to another conversation
4. Verify that socket events work for the new conversation
5. Switch back to the first conversation
6. Verify that socket events still work

### 2. **Test Real-time Updates**
1. Open a conversation
2. Send a message from another device/user
3. Verify that the message appears in real-time
4. Verify that the conversation list updates with the new last message

### 3. **Test Unread Count Updates**
1. Have unread messages in a conversation
2. Open the conversation
3. Verify that unread count decreases
4. Verify that unread count updates in real-time

### 4. **Test Message Status Updates**
1. Send a message
2. Verify that message status updates in real-time
3. Verify that status updates appear in the conversation

## Files Modified

### Frontend Files
- `apps/crm/frontend/src/pages/MessengerLayout.vue`
- `apps/crm/frontend/src/pages/MessengerDetail.vue`
- `apps/crm/frontend/src/pages/MessengerPlaceholder.vue`

### Backend Files
- `apps/crm/crm/api/messenger.py`

## Key Changes Made

### MessengerLayout.vue
1. Added socket listener tracking with `socketListenersInitialized` ref
2. Added `setupSocketListeners()` and `cleanupSocketListeners()` functions
3. Added missing socket event listeners for message updates
4. Added conversation ID tracking with route watchers
5. Added `refreshConversationList()` function
6. Added proper conversation sorting and user profile handling
7. Added debugging logs for better troubleshooting

### MessengerDetail.vue
1. Added conversation ID tracking with route watchers
2. Added debugging logs for socket events
3. Improved socket event handling for conversation switching
4. Added proper conversation ID synchronization

### messenger.py
1. Added new socket events for outgoing messages
2. Added new API functions for message handling
3. Added test functions for debugging

## Benefits

1. **Real-time Updates**: All socket events now work in real-time
2. **Proper Conversation Switching**: Socket events work correctly when switching between conversations
3. **No Duplicate Listeners**: Proper cleanup prevents duplicate socket listeners
4. **Better Debugging**: Added comprehensive logging for troubleshooting
5. **Improved Performance**: Proper conversation list updates and sorting
6. **Better User Experience**: Real-time updates for all messenger features

## Future Improvements

1. **Add Error Handling**: Add proper error handling for socket events
2. **Add Retry Logic**: Add retry logic for failed socket connections
3. **Add Connection Status**: Add visual indicators for socket connection status
4. **Add Message Queuing**: Add message queuing for offline scenarios
5. **Add Typing Indicators**: Add real-time typing indicators
6. **Add Read Receipts**: Add real-time read receipts 