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

## Canned Responses

The Messenger interface now includes support for canned responses, allowing users to quickly insert pre-defined messages into conversations.

### Feature Overview

- **Icon Placement**: Located in the message input area alongside emoji and file upload buttons
- **Visual Design**: Uses a consistent icon style matching the existing UI
- **Accessibility**: Follows Frappe UI button standards for keyboard navigation and screen readers

### Implementation Details

The feature is implemented with the following components:

1. **CannedResponseIcon Component**:
   - SVG-based icon design
   - Consistent with Frappe UI icon system
   - Responsive sizing
   - Accessible color contrast

2. **CannedResponseSelectorModal Component**:
   - Modal dialog for selecting canned responses
   - Search functionality for quick filtering
   - Grid layout for response templates
   - Create new response option
   - Real-time search filtering

3. **UI Integration**:
   - Added to MessengerBox component
   - Positioned in the message input toolbar
   - Maintains existing layout and spacing
   - Preserves all current functionality

### How it Works

1. **Accessing Canned Responses**:
   - Click the canned response icon in the message input area
   - Modal opens with list of available responses
   - Search box for quick filtering
   - Grid view of response templates

2. **Using Canned Responses**:
   - Click on a response to insert it into the message
   - Response text is automatically inserted
   - Modal closes after selection
   - Message can be edited after insertion

3. **Creating New Responses**:
   - "New Canned Response" button in modal
   - Redirects to canned responses management page
   - Create and manage response templates
   - Templates available immediately after creation

### Benefits

1. **Efficiency**: Quick access to common responses
2. **Consistency**: Ensures standardized messaging
3. **User Experience**: Seamless integration with existing UI
4. **Accessibility**: Follows Frappe UI standards
5. **Searchability**: Easy to find specific responses
6. **Management**: Simple creation and organization of responses

### Technical Implementation

1. **Components**:
   - `CannedResponseIcon.vue`: Custom icon component
   - `CannedResponseSelectorModal.vue`: Selection interface
   - Integration in `MessengerBox.vue`

2. **Data Management**:
   - Uses `Messenger Canned Response` DocType
   - Real-time search filtering
   - Efficient data loading
   - Proper state management

3. **User Interface**:
   - Responsive grid layout
   - Search functionality
   - Clear visual hierarchy
   - Consistent styling

### Future Enhancements

1. Canned response management interface
2. Category-based organization
3. Search functionality
4. Custom response creation
5. Response templates with variables
6. Response analytics and usage tracking
7. Team-specific responses
8. Response versioning

## Routing Changes

The messenger component has been split into two separate pages while maintaining the same visual layout:

1. **Messenger List View** (`/messenger`)
   - Shows the list of all conversations
   - Allows filtering and searching conversations
   - Displays unread message counts
   - Shows conversation previews with last message

2. **Individual Conversation View** (`/messenger/:conversationId`)
   - Shows the selected conversation
   - Maintains the conversation list on the left side
   - Allows direct navigation to specific conversations via URL
   - Supports deep linking from other parts of the application

### Key Changes

1. **URL-based Navigation**
   - Conversations can now be accessed directly via URL
   - Example: `/messenger/CONV123` will load conversation with ID CONV123
   - The conversation list remains visible for easy switching between conversations

2. **State Management**
   - Conversation state is now managed through URL parameters
   - Browser back/forward navigation works as expected
   - Conversation selection is preserved on page refresh

3. **Deep Linking**
   - Other parts of the application can now link directly to specific conversations
   - Useful for linking from leads, tasks, or other related items
   - Maintains context by showing the conversation list

4. **Real-time Updates**
   - All real-time features continue to work as before
   - Message updates, status changes, and unread counts are synchronized
   - Conversation list updates in real-time

### Usage Examples

1. **Direct Navigation**
   ```javascript
   router.push({ 
     name: 'Messenger',
     params: { conversationId: 'CONV123' }
   })
   ```

2. **Linking from Lead**
   ```javascript
   router.push({
     name: 'Messenger',
     params: { conversationId: lead.conversation_id }
   })
   ```

3. **Programmatic Navigation**
   ```javascript
   // Navigate to conversation list
   router.push({ name: 'MessengerList' })
   
   // Navigate to specific conversation
   router.push({ 
     name: 'Messenger',
     params: { conversationId: conversation.name }
   })
   ```

### Benefits

1. **Better Navigation**
   - Users can bookmark specific conversations
   - Browser history works correctly
   - Direct linking from other parts of the application

2. **Improved UX**
   - Maintains context with conversation list always visible
   - Smooth transitions between conversations
   - No loss of state on page refresh

3. **Enhanced Integration**
   - Better integration with other CRM features
   - Easier to link conversations to leads and other entities
   - More flexible navigation options

## Conversation Status

The messenger system now supports setting and tracking conversation statuses. This feature allows agents to mark conversations with different statuses to better manage and track their workflow.

### Features

1. **Status Selection**
   - A status dropdown is available in the conversation header next to the profile information
   - Statuses are managed through the Messenger Conversation Status doctype
   - Default status is "Open"

2. **Real-time Updates**
   - Status changes are reflected in real-time across all connected clients
   - Status updates are persisted in the database
   - Status history is maintained in the status_log table

3. **UI Integration**
   - Status selection is available in the conversation header
   - Current status is displayed prominently
   - Status changes are confirmed with toast notifications

### Technical Implementation

1. **Frontend Changes**
   - Added status dropdown in Messenger.vue
   - Implemented status change handler
   - Added real-time socket event listener for status updates
   - Integrated with existing conversation management

2. **Backend Changes**
   - Enhanced on_conversation_update hook to handle status changes
   - Added real-time event emission for status updates
   - Utilized existing Messenger Conversation Status doctype

3. **Data Structure**
   - Status field in Messenger Conversation doctype
   - Status options managed through Messenger Conversation Status doctype
   - Status history tracked in status_log table

### Usage

1. Select a conversation to view its details
2. Click the status dropdown in the conversation header
3. Choose a status from the available options
4. The status will be updated immediately and reflected across all clients

## Status Update Timeline

The messenger system now displays status updates within the conversation timeline, integrated with messages in chronological order. This feature provides a clear view of both conversation messages and status changes.

### Features

1. **Integrated Timeline**
   - Status updates appear between messages in chronological order
   - Maintains existing message grouping by date
   - Shows status changes with distinct styling
   - Preserves all existing message functionality

2. **Status Update Display**
   - Shows status change details in a centered notification
   - Displays who changed the status
   - Shows when the status was changed
   - Uses a distinct visual style to differentiate from messages

3. **Real-time Updates**
   - Status changes appear immediately in the timeline
   - Updates are synchronized across all clients
   - Maintains chronological order with messages
   - Preserves existing real-time message updates

### Technical Implementation

1. **Frontend Changes**
   - Added status log fetching and management
   - Created combined timeline of messages and status updates
   - Implemented chronological sorting
   - Added distinct styling for status updates
   - Preserved existing message grouping

2. **Data Structure**
   - Utilizes Messenger Conversation Status Log child table
   - Combines message and status data
   - Maintains timestamp-based ordering
   - Preserves existing message structure

3. **UI Components**
   - Status update notifications
   - Date grouping headers
   - Message components
   - Empty state handling

### Visual Design

1. **Status Update Notifications**
   - Centered in the chat timeline
   - Light blue background with border
   - Clear status and user information
   - Relative time display
   - Distinct from message styling

2. **Date Headers**
   - Maintains existing date grouping
   - Shows "Today", "Yesterday", or date
   - Consistent with existing design
   - Clear visual separation

### Usage

1. Status updates appear automatically in the chat timeline
2. Each status update shows:
   - The new status
   - Who changed it
   - When it was changed (in relative time)
3. Updates appear in chronological order with messages
4. Date grouping is maintained
5. All existing message functionality is preserved

## Tag Selection Dropdown Positioning

- The tag selection dropdown (when clicking the "+" button) now appears directly below the plus button, rather than overlapping the profile name.
- The dropdown is absolutely positioned with a shadow and border for clarity.
- This improves usability and visual clarity, especially when there are multiple tags or long profile names.
- No other features are affected by this change.

## Tag Management Backend Integration

- Tag selection and removal now persist to the backend using custom API endpoints (`get_conversation_tags` and `set_conversation_tags`).
- When a conversation is selected, tags are fetched from the backend and displayed.
- When tags are added or removed, the updated tag list is saved to the backend and immediately reflected in the UI.
- This ensures tags are always in sync and persist across sessions and devices.

## Conversation List Tag Display

- Selected tags for each conversation are now shown as colored pill badges in the conversation list, without opening the conversation.
- Up to 2 tags are shown as pills; if more, a '+N' pill is displayed.
- Tag colors match the tag color logic in the chat header.
- This feature is available in both Messenger.vue and MessengerList.vue.
- Tags are fetched from the backend for all conversations and kept in sync.

## Assigned User Avatars in Conversation List (2024-06)

### Feature
- The conversation list now displays avatars of assigned users (assignees) for each conversation, below the tags.
- Hovering over an avatar shows the full name of the assignee.
- The avatar size is reduced for compactness.

### UI/UX Changes
- **First row:** Profile name (left), timestamp (right).
- **Second row:** Last message (left), unread count (right).
- **Third row:** Tags (smaller), then assigned user avatars (right after tags).
- Tag size is reduced for a more compact look.

### Technical Details
- Assignees are fetched for all conversations in the list, not just the selected one.
- The avatars use the `Avatar` component with `size="xs"` and a tooltip for the full name.
- No existing features were broken; all previous functionality remains.

### Files Changed
- `Messenger.vue`: Conversation list template and logic updated to show assignees, fix alignment, and reduce tag size.
- `MessengerList.vue`: Same changes as above for the conversation list.

---

### Changelog (2024-06)
- Added assigned user avatars to conversation list (with tooltip, compact size)
- Improved alignment: profile/timestamp, last message/unread, tags/assignees
- Reduced tag size for better fit
- No breaking changes to existing features

*Last Updated: [Current Date]*
*Author: CRM Development Team*

## [2024-06-09] Helpdesk Ticket Creation from Messenger

### What was added
- A new option 'Create Helpdesk Ticket' in the Messenger chat profile's 3-dot menu (conversation actions).
- When enabled via the `enable_helpdesk_ticket_creation` flag in Messenger settings, this option appears for each conversation.
- Clicking it opens a modal to input a subject and detailed explanation for the ticket.
- Submitting the modal currently just closes it and shows a success toast (backend integration pending).

### Rationale
- Streamlines the process for CRM users to escalate or log support issues directly from a Messenger conversation.
- Reduces context switching and improves support workflow efficiency.

### Usage Instructions
1. Ensure the `enable_helpdesk_ticket_creation` flag is enabled in Messenger settings.
2. In any Messenger conversation, click the 3-dot menu (top right of chat profile section).
3. Select 'Create Helpdesk Ticket'.
4. Fill in the subject and detailed explanation in the modal.
5. Click 'Submit'.
6. (Future) The ticket will be created in Helpdesk; for now, only a success message is shown.

### Notes
- The modal and menu option are only visible if the feature flag is enabled.
- No backend or data model changes are included in this update.
- Existing Messenger features are unaffected.

## [2024-07-09] Backend API: Create Helpdesk Ticket from Messenger

### Purpose
Allows Messenger users to create a Helpdesk (HD) Ticket directly from a Messenger conversation. The ticket is linked to the conversation and visible in the Messenger Conversation's HD Tickets child table.

### API Endpoint
- `crm.api.messenger.create_helpdesk_ticket_from_messenger`
- **Method:** POST (frappe.call)
- **Params:**
  - `subject` (str): Ticket subject
  - `description` (str): Ticket description
  - `conversation_id` (str): Messenger Conversation name (primary key)

### Data Flow
1. Creates a new `HD Ticket` (with `custom_messenger_conversation` set to the Messenger Conversation name).
2. Appends a row to the Messenger Conversation's `hd_tickets` child table (Link to HD Ticket, status).
3. Returns the new ticket name and status.

### Example Usage
```js
frappe.call('crm.api.messenger.create_helpdesk_ticket_from_messenger', {
  subject: 'Subject here',
  description: 'Details here',
  conversation_id: 'MSG-CONV-xxxxxx'
}).then(r => {
  // r.message = { ticket: ..., status: ... }
})
```

### Notes
- No changes to existing Messenger or Helpdesk features.
- All permissions and validations are handled by Frappe's standard DocType logic.
- The HD Ticket will be visible in the Messenger Conversation's "HD Tickets" tab/child table.

## [2024-07-09] Frontend Integration: Create Helpdesk Ticket from Messenger

### UI Flow
- User opens the 3-dot menu in a Messenger conversation and selects "Create Helpdesk Ticket" (if enabled).
- A modal appears with fields for Subject and Detailed Explanation.
- On submit, the frontend calls the backend API (`crm.api.messenger.create_helpdesk_ticket_from_messenger`) with the subject, description, and conversation ID.
- The modal shows loading state and disables the submit button until the request completes.
- On success, a toast is shown and the modal closes. On error, an error toast is shown.

### Code Reference
- See `submitHelpdeskTicket` in `Messenger.vue` for the integration logic.
- Uses `frappe.call` to invoke the backend API.

### Notes
- The submit button is only enabled if both fields are filled and not loading.
- No impact on existing Messenger or Helpdesk features.

## [2024-07-09] UI: Show Latest Helpdesk Ticket Status in Messenger Conversation Profile

### Purpose
- Shows the latest linked Helpdesk Ticket status for the conversation, making it easy for agents to see ticket progress at a glance.

### UI Placement
- Displayed in the conversation profile section, to the left of the conversation status select box.
- Includes a ticket icon and a distinct yellow style to differentiate it from the conversation status.
- Only shown if a latest ticket status exists for the conversation.

### Notes
- Uses the `latest_ticket_status` field from the Messenger Conversation DocType.
- Does not affect any existing Messenger or Helpdesk features.
- Responsive and visually distinct from the main conversation status.

## [2024-07-09] UI: View Past Helpdesk Tickets in Messenger Conversation Modal

### What was added
- If a conversation has any tickets in the `hd_tickets` child table, the Messenger menu now shows "View Tickets" with a ticket icon (instead of "Create Ticket" with a plus icon).
- When the modal opens, the last 3 tickets (ID, subject, status, created time) are shown at the top.
- A button at the bottom allows users to create a new ticket; clicking it reveals the ticket creation fields.
- All ticket data is fetched from the backend using a new API (`get_last_tickets_for_conversation`).
- Real-time updates: when a new ticket is created, the ticket list and latest status update immediately.

### UI Flow
- Open the 3-dot menu: if tickets exist, see "View Tickets"; otherwise, see "Create Ticket".
- In the modal: see the last 3 tickets, then the option to create a new one.
- Creating a ticket updates the list and status in real time.

### Backend
- New API: `get_last_tickets_for_conversation` returns the last N tickets for a conversation.

### Notes
- Only the last 3 tickets are shown for brevity.
- No impact on existing features or workflows.

## [2024-07-09] Improvements: Ticket List Loading, Icon Consistency, and Clickable Tickets

### What was improved
- **Ticket List Loading:** The last 3 tickets (pastTickets) now load as soon as a conversation is selected, ensuring the menu and modal always reflect the correct state.
- **Menu Icon Consistency:** The TicketIcon in the menu dropdown now matches the size and alignment of other icons.
- **TicketIcon Visual Update:** The TicketIcon SVG was updated to look more like a real ticket, with notched sides and a dotted line.
- **Clickable Tickets:** Tickets in the modal are now clickable; clicking a ticket opens the Helpdesk ticket in a new tab (`/helpdesk/tickets/<ticket-id>`).

### Notes
- No impact on existing features or workflows.
- All changes are modular and maintain UI/UX consistency.

*Last Updated: [Current Date]*
*Author: CRM Development Team*

## [2024-07-09] Improvements: Ticket Status Colors in Menu and Modal

### What was improved
- **Colored Ticket Icons:** The TicketIcon in the menu dropdown and in the modal now uses color to indicate ticket status:
  - Yellow for Open
  - Blue for Replied
  - Green for Resolved
  - Gray for Closed
- **Status Text and Badge:** The status text and badge in the modal and conversation profile also use the same color scheme for consistency.
- **UI Consistency:** All changes maintain the look and feel of the CRM and do not affect existing features.

### Notes
- Status color mapping matches the system status dropdown for clarity.
- No impact on existing workflows or features.

*Last Updated: [Current Date]*
*Author: CRM Development Team* 