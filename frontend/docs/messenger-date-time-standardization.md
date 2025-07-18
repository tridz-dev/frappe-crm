# Messenger Date & Time Standardization

## Nature of the Change

All date and time formatting in the CRM Messenger frontend (MessengerLayout.vue and MessengerDetail.vue) has been standardized to use the Frappe UI standard, as implemented in the shared utility functions in `@/utils` (`formatDate` and `timeAgo`).

## Rationale

Previously, MessengerLayout.vue and MessengerDetail.vue used custom, local date/time formatting functions. This led to inconsistencies and timezone issues, especially when server and client were in different timezones (e.g., server in Asia/Kolkata, client in Qatar). The only component that handled time correctly according to user settings was MessengerArea.vue, which used the Frappe standard utility.

## What Was Changed

- **MessengerLayout.vue**
  - Replaced the local `formatTimeAgo` function with the shared `timeAgo` utility from `@/utils` for conversation list timestamps (e.g., 'just now', '1 minute ago', etc.).
  - Removed the local implementation of `formatTimeAgo`.
  - Ensured all time displays in the conversation list use the correct utility.

- **MessengerDetail.vue**
  - Replaced the local `formatDate` and `formatTimeAgo` functions with the shared `formatDate` and `timeAgo` utilities from `@/utils`.
  - All date separators, status logs, and helpdesk ticket creation times now use the Frappe standard.
  - Removed the local implementations of these functions.

- **Imports**
  - Both files now import `formatDate` and `timeAgo` from `@/utils`.

## Usage Instructions

- For displaying a formatted date (e.g., date separator):
  ```js
  import { formatDate } from '@/utils'
  formatDate(date, 'ddd, MMM D, YYYY')
  ```
- For displaying relative time (e.g., 'just now', '2 hours ago'):
  ```js
  import { timeAgo } from '@/utils'
  timeAgo(date)
  ```
- These utilities automatically respect the user's timezone and Frappe system settings.

## Important Notes

- This change ensures all Messenger date/times are consistent and timezone-correct, matching the behavior of MessengerArea.vue.
- No other functionality was changed or broken.
- If you add new date/time displays in Messenger, always use these shared utilities.

## Known Limitations

- If system defaults (date/time format) are not set in Frappe, fallback formats will be used.
- If you encounter any timezone issues, verify the user's timezone in Frappe settings and that the browser has the correct local time. 

## 2024-06-25: Frappe-style Time Ago Utility

### What Was Changed

- Implemented a new `frappeTimeAgo` utility in `@/utils/index.js`.
- All Messenger components (`MessengerLayout.vue`, `MessengerDetail.vue`, helpdesk ticket lists, etc.) now use `frappeTimeAgo` for relative time displays (e.g., '2 hours ago', 'Today', 'Yesterday').
- This utility ensures all times are shown in the user's timezone and match Frappe's conventions for 'Today', 'Yesterday', and relative times.

### Rationale

- The previous implementation used `timeAgo` from `@vueuse/core`, which did not respect the user's timezone or Frappe system settings, causing incorrect 'x hours ago' and date labels when server and client were in different timezones.
- The new utility uses `dayjsLocal` (from Frappe UI) to convert all times to the user's timezone before calculating differences.
- This matches the behavior of Frappe's backend and frontend utilities, and ensures consistency across all Messenger views.

### Usage Instructions

- To display a relative time (e.g., in conversation lists, ticket lists):
  ```js
  import { frappeTimeAgo } from '@/utils'
  frappeTimeAgo(date)
  ```
- This will return:
  - 'Just now' (within 1 minute)
  - 'x minutes ago', 'x hours ago' (if today)
  - 'Today', 'Yesterday' (if applicable)
  - 'x days ago' (within a week)
  - Otherwise, a formatted date string

### Important Notes

- Always use `frappeTimeAgo` for any new relative time displays in Messenger.
- This utility automatically respects the user's timezone and Frappe system settings.
- No other functionality was changed or broken. 