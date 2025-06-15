# Messenger Component Features Documentation

## Overview
This document details the major features and changes implemented in the CRM Messenger component (`Messenger.vue`). The component provides a modern messaging interface with real-time communication capabilities, following Frappe UI standards and design patterns.

## Recent Feature Implementations

### 1. Infinite Scrolling
#### Conversations List
- **Feature**: Dynamic loading of conversation history
- **Implementation**: 
  - Triggers when user scrolls to top of conversations list
  - Uses pagination with configurable limit (20 conversations per load)
  - Maintains scroll position while loading
- **Function**: `loadMoreConversations()`
- **Usage**: Automatically triggered when user scrolls to top (threshold: 50px)

#### Messages View
- **Feature**: Infinite scroll for message history
- **Implementation**:
  - Loads older messages when scrolling up
  - Preserves scroll position after loading
  - Uses timestamp-based pagination
- **Function**: `loadMoreMessages()`
- **Usage**: Triggers when scrolled near top (threshold: 100px)

### 2. ESC Key Navigation
- **Feature**: Quick navigation back to conversation list
- **Implementation**:
  - Global keyboard event listener for 'Escape' key
  - Clears selected conversation and reply state
- **Function**: `handleEscKey()`
- **Usage**: Press ESC key while in a conversation to return to conversation list
- **Cleanup**: Event listeners properly managed with Vue lifecycle hooks

### 3. Real-time Message Updates
- **Feature**: Immediate message display and conversation updates
- **Implementation**:
  - Messages appear instantly after sending
  - Conversations list auto-updates with latest message
  - Auto-scrolls to latest message
- **Functions**: 
  - `handleSendMessage()`
  - `getCurrentConversation()`

### 4. Platform Integration
- **Feature**: Support for multiple messaging platforms
- **Implementation**:
  - Unified interface for Facebook Messenger and Instagram DM
  - Platform-specific icons and identifiers
  - Consistent message handling across platforms

### 5. Message Threading
- **Feature**: Support for message replies and threading
- **Implementation**:
  - Reply functionality with message context
  - Thread visualization in message area
- **Component**: `MessengerBox` for message input and replies

### 6. Unread Messages Tracking
#### Feature Overview
- **Functionality**: Tracks and displays unread incoming messages
- **Implementation**:
  - Backend storage using `is_read` field in Messenger Message DocType
  - Bulk update functionality for marking messages as read
  - Visual indicators for unread messages count
  - Real-time unread count updates with refresh sync

#### Components
- **Unread Badge**:
  - Displays count of unread messages per conversation
  - Located under conversation timestamp
  - Uses CRM's standard notification badge styling
  - Updates in real-time with conversation refresh
  
#### Technical Implementation
- **Backend**:
  - New `is_read` field in Messenger Message DocType
  - Custom API endpoint for bulk message updates
  - Efficient SQL-based status updates
  - Automatic count synchronization

- **Frontend**:
  - Reactive unread counts state management
  - Automatic polling for updates (30-second intervals)
  - Refresh button sync support
  - Efficient bulk status updates
  - Proper infinite scroll handling

### State Management Improvements
1. **Unread Count Sync**:
   - Reset counts on refresh
   - Update on conversation selection
   - Sync with infinite scroll
   - Handle bulk updates efficiently

2. **Message Status Updates**:
   - Bulk update all unread messages
   - Proper state management
   - Efficient SQL updates
   - Real-time count updates

3. **Refresh Handling**:
   - Proper count sync on refresh
   - Automatic state updates
   - Efficient data fetching
   - Consistent state management

### Performance Optimizations
- Bulk SQL updates for message status
- Efficient count queries
- Optimized state management
- Proper infinite scroll handling
- Reduced API calls

## Dependencies
- Frappe UI components (Button, Avatar, Input)
- Vue 3 Composition API
- Frappe backend API integration
- Custom Messenger Message DocType methods

## Limitations and Known Issues
1. Message history limited to 100 messages per load
2. 30-second polling interval for unread counts
3. Requires page refresh for immediate count updates
4. Bulk updates limited to single conversation

## Future Improvements
1. Real-time WebSocket updates
2. Per-user read status
3. Optimized bulk operations
4. Enhanced state management
5. Improved refresh handling

## Usage Instructions
1. Navigate to the Messenger view in CRM
2. Select a conversation to mark its messages as read
3. Use refresh button to sync unread counts
4. Scroll up to load more messages
5. Unread counts update automatically every 30 seconds

## Time Ago Display

The Messenger interface now shows relative time for message timestamps in the conversation list. This feature provides a more user-friendly way to understand when the last message was received.

### How it Works

The time ago display shows relative time in the following format:
- Just now (for messages less than a minute old)
- X minutes ago (for messages less than an hour old)
- X hours ago (for messages less than a day old)
- X days ago (for messages less than a week old)
- X weeks ago (for messages less than a month old)
- X months ago (for messages less than a year old)
- X years ago (for messages older than a year)

### Implementation Details

The feature uses a `formatTimeAgo` function that:
1. Takes a timestamp as input
2. Calculates the time difference between now and the message time
3. Returns the appropriate relative time string
4. Handles all time ranges from seconds to years
5. Uses proper pluralization for time units

### Benefits

1. **User-Friendly**: Makes it easier to understand message timing at a glance
2. **Dynamic Updates**: Shows real-time relative time
3. **Consistent Format**: Maintains a standard format across all conversations
4. **Internationalization**: Supports multiple languages through the translation system

### Example Output

```
Just now
1 minute ago
5 minutes ago
1 hour ago
2 hours ago
1 day ago
2 days ago
1 week ago
2 weeks ago
1 month ago
6 months ago
1 year ago
2 years ago
```

---

*Last Updated: [Current Date]*
*Author: CRM Development Team* 