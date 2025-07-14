# MessengerDetail.vue Infinite Scroll & API Pagination Migration

## Problem
Previously, when loading more messages via infinite scroll (scrolling up), the frontend would fetch the latest 100 messages from the backend every time. This caused message duplication, as the same messages were repeatedly prepended to the chat view. The issue became apparent after optimizing the API for faster loading.

## Solution
Both the backend and frontend were updated to support true paginated message loading:

### Backend (`messenger.py`)
- The `get_conversation_details` API now accepts two new parameters:
  - `limit` (default: 20): The number of messages to fetch per request.
  - `before` (optional): A timestamp. If provided, only messages older than this timestamp are returned.
- On initial load, the API returns the latest `limit` messages.
- On subsequent requests (infinite scroll), the API returns the next batch of older messages, enabling efficient pagination.

### Frontend (`MessengerDetail.vue`)
- On initial load, only the latest 20 messages are fetched and displayed.
- When the user scrolls up, the frontend requests the next batch of older messages by passing the timestamp of the oldest loaded message as the `before` parameter.
- Only new (older) messages are prepended to the chat, preventing duplicates.
- The process repeats as the user continues to scroll up, providing a smooth infinite scroll experience.

## Developer Usage
- **API Call Example:**
  ```js
  call('crm.api.messenger.get_conversation_details', {
    conversation_id: 'MSG-CONV-XXXX',
    limit: 20,
    before: '2024-06-01 12:34:56'
  })
  ```
- **Frontend Logic:**
  - On first load: call with no `before` to get the latest messages.
  - On scroll up: call with `before` set to the timestamp of the oldest message currently loaded.
  - Prepend only messages not already present in the chat.

## Benefits
- No more message duplication during infinite scroll.
- Faster initial load and better performance for large conversations.
- No breaking changes to other features or API consumers.

## Migration Notes
- The rest of the conversation details (tags, assignees, status updates, tickets, etc.) are unaffected.
- The new API is backward compatible; if `limit` and `before` are not provided, it defaults to the latest 20 messages.

## Example
- User opens a conversation: sees the latest 20 messages.
- User scrolls up: next 20 older messages are loaded and prepended.
- This continues until all messages are loaded.

---

**This migration ensures a smooth, efficient, and bug-free infinite scroll experience in MessengerDetail.vue.** 