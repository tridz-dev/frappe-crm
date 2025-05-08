# Platform Filter for Messenger Conversations

## Feature Overview
The platform filter allows users to filter conversations based on their messaging platform (Messenger or Instagram).

### Functionality
- Filter options:
  - All Messages (default): Shows conversations from all platforms
  - Messenger: Shows only Facebook Messenger conversations
  - Instagram: Shows only Instagram DM conversations

### Implementation Details
- Added to the header section of conversations list
- Uses Frappe UI's standard select component
- Maintains existing conversation list functionality
- Real-time filtering without page reload

### Technical Notes
- Filter state is managed locally in the component
- Preserves existing conversation sorting and infinite scroll
- Platform information comes from conversation.platform field

### Limitations
- Filter resets to "All Messages" on page refresh
- Only affects conversation list view, not individual messages 