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
  - Visual indicators for unread messages count
  - Automatic marking of messages as read when conversation is opened
  - Real-time unread count updates (30-second polling)

#### Components
- **Unread Badge**:
  - Displays count of unread messages per conversation
  - Located next to conversation timestamp
  - Uses CRM's standard notification badge styling
  - Matches Frappe CRM's sidebar notification design
  
- **Message Separator**:
  - Visual separator for unread messages section
  - Blue highlight to draw attention
  - Only appears when unread messages exist

#### Technical Implementation
- **Backend**:
  - New `is_read` field in Messenger Message DocType
  - Uses Frappe's standard `set_value` API for marking messages as read
  - Efficient single-message update approach
  - Automatic status sync with message reload

- **Frontend**:
  - Reactive unread counts state management
  - Automatic polling for updates
  - Efficient DOM updates for unread indicators
  - Fixed message display using proper array prop passing
  - Consistent styling with CRM notification system

### UI/UX Improvements
1. **Message Display Fix**:
   - Corrected MessengerArea component integration
   - Messages now properly displayed as an array
   - Added message wrapper for better structure

2. **Badge Styling Consistency**:
   - Moved unread badge to timestamp section
   - Aligned with CRM's notification badge design
   - Uses `bg-surface-gray-6` background with white text
   - Improved visibility and placement

3. **Read Status Management**:
   - Improved message read status updating
   - Uses efficient single-message update approach
   - Automatic status sync after conversation selection
   - Proper state management for unread counts

4. **Visual Hierarchy**:
   - Clear distinction between read and unread messages
   - Intuitive placement of unread indicators
   - Consistent with overall CRM design language
   - Better integration with conversation timestamp

### State Management
- Uses Vue 3 Composition API with `ref` and `computed` properties
- Reactive state handling for conversations and messages
- Efficient pagination and data loading
- Real-time unread message tracking
- Improved read status synchronization

### Performance Optimizations
- Lazy loading of messages and conversations
- Scroll position preservation
- Efficient DOM updates
- Debounced scroll handlers
- Optimized unread message counting
- Single-message update strategy

## Dependencies
- Frappe UI components (Button, Avatar, Badge, Input)
- Vue 3 Composition API
- Frappe backend API integration
- Messenger Message DocType with unread tracking

## Limitations and Known Issues
1. Message history limited to 100 messages per load
2. Real-time updates require manual refresh
3. Platform-specific features may be limited
4. Unread count updates every 30 seconds (not instant)
5. Unread status only tracks incoming messages

## Future Improvements
1. Real-time message notifications
2. Enhanced search capabilities
3. Media message support
4. Message status indicators
5. Instant unread status updates using WebSocket
6. Per-user unread message tracking
7. Batch update optimization for multiple unread messages

## Usage Instructions
1. Navigate to the Messenger view in CRM
2. Select a conversation from the left panel
3. Use ESC key to return to conversation list
4. Scroll up to load more messages/conversations
5. Reply to messages using the input box at bottom
6. Unread message counts visible next to conversation timestamps
7. Blue separator indicates start of unread messages

---

*Last Updated: [Current Date]*
*Author: CRM Development Team* 