# Messenger Profile Pictures

## Overview
The Messenger module now supports displaying user profile pictures in both the conversation list and chat view. Profile pictures are fetched from the Messenger User doctype and displayed alongside messages.

## Features
- Profile pictures in conversation list
- Profile pictures in chat messages
- Fallback to user initials when no profile picture is available
- Real-time profile picture updates

## Implementation Details

### Data Flow
1. Conversation/Messages contain `sender_id`
2. `sender_id` is used to fetch user details from Messenger User doctype
3. Profile picture is displayed from the `profile` field of Messenger User

### Components Modified
- `Messenger.vue`: Main messenger interface
- `MessengerArea.vue`: Chat message display
- `MessengerBox.vue`: Message input area

### Technical Notes
- Profile pictures are cached to reduce database queries
- Fallback to user initials when profile picture is not available
- Profile pictures are displayed in a circular format
- Real-time updates when user profile is modified

## Usage
Profile pictures are automatically displayed in:
1. Conversation list next to each conversation
2. Chat messages for both incoming and outgoing messages
3. Reply previews in the message input area

## Dependencies
- Messenger User doctype
- Messenger Conversation doctype
- Messenger Message doctype 