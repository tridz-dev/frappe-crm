# Message Status Feature

## Overview
The message status feature provides visual feedback about the delivery and read status of outgoing messages in the CRM messenger, now using the same double tick icon and color logic as WhatsApp for visual consistency.

## Status Types
1. **Sent** (Single Tick)
   - Initial status when a message is sent
   - Shows a single gray tick mark (CheckIcon)

2. **Delivered** (Double Tick)
   - Status when the message is delivered to the recipient
   - Shows two gray tick marks (DoubleCheckIcon, no gap)

3. **Read** (Blue Double Tick)
   - Status when the recipient has read the message
   - Shows two blue tick marks (DoubleCheckIcon with blue color, no gap)

## Implementation Details
- The status is stored in the `status` field of the `Messenger Message` doctype
- Status updates are handled through socket events in real time, including read marking
- The UI now uses the same DoubleCheckIcon as WhatsApp, ensuring no gap between ticks and matching color logic
- The icon logic is implemented in `MessageStatusIcon.vue` and matches the WhatsApp message area

## Socket Events
- `messenger:message_status_update`: Emitted when a message's status changes
  - Payload: `{ message_id: string, status: 'Sent' | 'Delivered' | 'Read' }`

## Components
- `MessageStatusIcon.vue`: Reusable component for displaying message status, now using DoubleCheckIcon for double tick states
- Integrated into `MessengerArea.vue` for message display
- Status updates handled in `Messenger.vue`

## Usage
The feature works automatically for all outgoing messages. No additional configuration is required.

## Technical Details
1. **Message Status Flow**:
   - When a message is sent, it starts with "Sent" status
   - When the message is delivered to the recipient, status changes to "Delivered"
   - When the recipient reads the message, status changes to "Read" (real-time via socket)

2. **Socket Integration**:
   - The frontend listens for `messenger:message_status_update` events
   - When received, it updates the message status in the UI
   - The status icon updates automatically to reflect the new state

3. **UI Components**:
   - `MessageStatusIcon.vue`: Handles the display of different status icons
   - Uses Tailwind CSS for styling
   - Maintains consistent sizing and spacing with existing UI
   - Uses DoubleCheckIcon for double tick, matching WhatsApp

## Backend Requirements
The backend should emit the following socket events:
1. When a message is delivered:
   ```javascript
   socket.emit('messenger:message_status_update', {
     message_id: message.name,
     status: 'Delivered'
   })
   ```

2. When a message is read:
   ```javascript
   socket.emit('messenger:message_status_update', {
     message_id: message.name,
     status: 'Read'
   })
   ``` 