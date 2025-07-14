# Messenger Routing Refactor

## Nature of the Change

The Messenger module's routing and component structure has been refactored to use a parent layout with nested routes, following Vue.js best practices. The sidebar (conversation list) and all related logic are now centralized in a new `MessengerLayout.vue` component. The right pane is rendered via `<router-view>`, showing either a placeholder (empty state) or the selected conversation's details.

## Rationale

- **Reduce Duplication:** Previously, both `MessengerList.vue` and `Messenger.vue` duplicated sidebar and conversation list logic.
- **Modularity:** Centralizing sidebar logic in a parent layout makes the codebase easier to maintain and extend.
- **Scalability:** Nested routing allows for more flexible UI patterns and future features.
- **Consistency:** Follows Vue Router's recommended layout pattern for master-detail views.

## Usage Instructions

- **Routes:**
  - `/messenger` — Shows the sidebar and an empty state ("No conversation selected").
  - `/messenger/:conversationId` — Shows the sidebar and the selected conversation's messages.
- **Component Structure:**
  - `MessengerLayout.vue`: Parent layout, contains sidebar and `<router-view>`.
  - `MessengerPlaceholder.vue`: Empty state for when no conversation is selected.
  - `MessengerDetail.vue`: Conversation detail view (all features from old Messenger.vue).
- **Navigation:**
  - Use the sidebar to select a conversation. This will route to `/messenger/:conversationId` and display the conversation in the right pane.

## Migration Notes

- The old `MessengerList.vue` and `Messenger.vue` are still present for migration/testing. They can be deleted after confirming the new layout works as expected.
- All sidebar features (filters, unread counts, assignees, tags, etc.) and conversation features (messages, status, ticket modal, real-time updates, etc.) have been preserved in the new structure.
- Update any direct links or navigation to use the new `/messenger` and `/messenger/:conversationId` routes.

## Known Limitations

- During migration, both old and new routes are available. Remove the old routes and components after full migration.

---

**Refactor by: [Your Name/Team]**
**Date:** [YYYY-MM-DD] 