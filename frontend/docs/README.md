## Helpdesk Ticket Creation from Messenger

### Purpose
Allows CRM users to create a Helpdesk (HD) Ticket directly from a Messenger conversation, streamlining support and escalation workflows.

### Usage
- In the Messenger chat profile (3-dot menu), a new option 'Create Helpdesk Ticket' appears if the `enable_helpdesk_ticket_creation` flag is enabled in settings.
- Clicking this option opens a modal where the user can enter a subject (short description) and a detailed explanation.
- On submit, the modal closes and a success toast is shown. (Backend integration to actually create the ticket will be added later.)

### Notes
- The option is only visible if the feature flag is enabled in Messenger settings.
- The modal UI is consistent with Helpdesk ticket creation standards.
- No backend changes are included in this update.
- Existing Messenger features and menu actions are unaffected. 