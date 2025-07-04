# Messenger Ticket Menu Options Fix

## Nature of the Change
This update ensures that the Messenger conversation dropdown menu ("Create Ticket" / "View Tickets" / "View Lead") displays the correct options immediately after a conversation is selected, even when navigating within the Messenger module (e.g., from MessengerList.vue or sidebar), without requiring a page reload.

## Rationale
Previously, when navigating to the Messenger page and selecting a conversation, the menu options for tickets and leads would not appear until the page was reloaded. This was due to two issues:
- The menu was rendered before the ticket data (`pastTickets`) and the helpdesk ticket creation flag (`enableHelpdeskTicketCreation`) were fetched.
- More importantly, Messenger.vue did not react to changes in the route parameter (`route.params.conversationId`) after the initial mount. As a result, selecting a conversation from the sidebar or MessengerList.vue did not update the selected conversation or menu options unless the page was reloaded.

The fix ensures that Messenger.vue now watches for changes in `route.params.conversationId` and always selects the correct conversation and updates menu options accordingly.

## Implementation Details
- The `onMounted` hook still awaits the API call for the helpdesk ticket creation flag before fetching conversations or handling initial conversation selection.
- A new watcher on `route.params.conversationId` ensures that every time the route param changes, the correct conversation is selected and all menu logic is updated.
- The `handleConversationSelect` function still calls `await fetchPastTickets()` to ensure ticket data is loaded.
- The watcher on `selectedConversation` remains for other programmatic changes.

## Usage Instructions
No user-facing changes or new features. The menu will now always show the correct ticket/lead options immediately after selecting a conversation, even when navigating within the Messenger module.

## Impact
- No breaking changes.
- No effect on other Messenger features.
- No new dependencies or configuration required.

---
**Date:** [YYYY-MM-DD]
**Author:** AI Assistant 