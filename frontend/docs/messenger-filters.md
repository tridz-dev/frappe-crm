# Messenger Conversation Filters

## Overview
The Messenger module now includes a filtering system similar to the CRM list views, allowing users to filter conversations based on various fields.

## Features
- Filter conversations by any field in the Messenger Conversation doctype
- Combine multiple filters using AND logic
- Clear individual filters or all filters at once
- Filter options include:
  - Platform
  - Sender ID
  - Last Message
  - Last Message Time
  - Status
  - Conversation ID
  - Participants

## Usage
1. Click the Filter button next to the platform dropdown
2. Select a field to filter by
3. Choose an operator (equals, contains, etc.)
4. Enter the filter value
5. Add more filters as needed
6. Click outside the filter popover to apply filters

## Technical Implementation
The filter feature is implemented using the same Filter component used in CRM list views. The component is integrated into the Messenger.vue file and communicates with the backend through the conversationsResource.

### Key Components
- `Filter.vue`: Reused from CRM for consistent filtering UI
- `Messenger.vue`: Added filter button and integration
- `messenger_conversation.json`: Defines available fields for filtering

### Filter Logic
Filters are applied by updating the conversationsResource parameters and triggering a reload. The backend handles the actual filtering of conversations based on the provided criteria.

#### Implementation Details
1. List Model Initialization:
   ```javascript
   const list = ref({
     data: {
       params: {
         filters: {}
       }
     }
   })
   ```

2. Filter Update Handler:
   ```javascript
   function updateFilter(filters) {
     conversationsResource.params = {
       ...conversationsResource.params,
       filters: {
         ...filters
       }
     }
     conversationsResource.reload()
   }
   ```

3. Resource Success Handler:
   ```javascript
   onSuccess: async (data) => {
     // Process data...
     // Update list model with current filters
     list.value.data.params.filters = conversationsResource.params.filters
   }
   ```

### Error Handling
- The filter component now properly initializes with an empty filters object
- Filter updates are handled through a dedicated updateFilter function
- The list model is kept in sync with the conversationsResource filters

## Dependencies
- Frappe UI components
- CRM Filter component
- Messenger Conversation doctype fields

## Future Enhancements
- Add saved filter presets
- Support OR logic between filters
- Add date range filters for message timestamps
- Add quick filters for common filter combinations

## Recent Fixes
- Fixed filter initialization issue causing null reference errors
- Improved filter state management
- Added proper synchronization between list model and resource filters
- Removed debug console logs
- Optimized filter update logic 