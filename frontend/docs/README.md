# CRM Frontend Docs

## [2024-07-10] Messenger Helpdesk Ticket Type Selection

- The Messenger helpdesk ticket creation modal now requires users to select a Ticket Type.
- Ticket types are fetched from the backend (HD Ticket Type DocType).
- The selected type is set on the new HD Ticket and used for categorization and workflow.
- This change improves ticket classification and reporting.
- No breaking changes; existing features are unaffected.

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

## Important notes or dependencies

- Always use the shared `formatDate` and `timeAgo` utilities from `@/utils` for all date and time formatting in Messenger components. See `messenger-date-time-standardization.md` for details. 