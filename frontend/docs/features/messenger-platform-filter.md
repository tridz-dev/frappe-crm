# Messenger Platform Filter Feature

## Overview
The Messenger Platform Filter is a feature that allows users to filter conversations in the CRM messenger based on the platform they originated from (e.g., Facebook Messenger, Instagram, etc.).

## Implementation Details

### Components
- Located in: `crm/frontend/src/pages/Messenger.vue`
- Uses Frappe UI's `Dropdown` component for the filter interface

### Features
1. **Platform Filtering**
   - Users can filter conversations by platform (All, Messenger, Instagram)
   - Filter updates the conversation list in real-time
   - Maintains scroll position and pagination state

2. **Filter Options**
   - All: Shows conversations from all platforms
   - Messenger: Shows only Facebook Messenger conversations
   - Instagram: Shows only Instagram conversations

### Technical Implementation
- Uses Vue's computed properties for reactive filtering
- Case-insensitive platform matching
- Resets conversation list and pagination when filter changes
- Maintains existing conversation loading and infinite scroll functionality

## Usage
1. Click the platform filter dropdown in the messenger header
2. Select desired platform from the options
3. Conversation list updates automatically to show only conversations from selected platform

## Dependencies
- Frappe UI Components
- Vue.js Reactive System
- Existing Messenger Conversation Data Structure

## Notes
- Filter state is maintained during the session
- Filter changes trigger a reload of conversations to ensure data consistency
- Platform icons are displayed next to each conversation for visual identification 