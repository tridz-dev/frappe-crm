# Messenger Continuous API Calls Fix

## Issue Description

The messenger components were experiencing continuous API calls, particularly for fetching unread counts, which was causing performance issues and unnecessary server load.

### Symptoms
- Continuous network activity in browser dev tools
- Multiple `fetchUnreadCounts()` API calls happening repeatedly
- Performance degradation in messenger interface
- Unnecessary server load

## Root Causes Identified

### 1. **Problematic Deep Watcher**
```javascript
// MessengerLayout.vue - Line 496-498
watch(() => conversationsResource.data, async () => {
  await fetchUnreadCounts()
}, { deep: true })
```

**Problem**: This watcher was triggering `fetchUnreadCounts()` every time the conversations data changed, which happened frequently due to real-time socket updates.

### 2. **Redundant API Calls**
- `fetchUnreadCounts()` was being called even though `get_conversations_with_details` API already returns unread counts
- Multiple calls in socket event handlers
- Route watchers triggering unnecessary refreshes

### 3. **Multiple Trigger Points**
- Socket event handlers calling `fetchUnreadCounts()`
- Route change watchers calling `refreshConversationList()`
- Deep watchers on conversation data

## Solution Implemented

### 1. **Removed Problematic Deep Watcher**
```javascript
// Before
watch(() => conversationsResource.data, async () => {
  await fetchUnreadCounts()
}, { deep: true })

// After
watch(() => conversationsResource.data, async () => {
  // Remove this watcher as it causes continuous API calls
  // Unread counts are already fetched by get_conversations_with_details API
}, { deep: true })
```

### 2. **Added API Call Prevention**
```javascript
const isFetchingUnreadCounts = ref(false)

async function fetchUnreadCounts() {
  // Prevent multiple simultaneous calls
  if (isFetchingUnreadCounts.value) {
    console.log('fetchUnreadCounts already running, skipping...')
    return
  }
  
  isFetchingUnreadCounts.value = true
  
  try {
    // API call logic
  } finally {
    isFetchingUnreadCounts.value = false
  }
}
```

### 3. **Optimized Socket Event Handlers**
- Removed `fetchUnreadCounts()` calls from socket events
- Unread counts are now handled by the `messenger:unread_update` socket event
- Socket events directly update the unread counts without additional API calls

### 4. **Optimized Route Watchers**
```javascript
// Before
watch(() => router.currentRoute.value.params.conversationId, (newConversationId) => {
  if (newConversationId) {
    refreshConversationList() // This called fetchUnreadCounts()
  }
}, { immediate: true })

// After
watch(() => router.currentRoute.value.params.conversationId, (newConversationId) => {
  if (newConversationId) {
    // Don't refresh conversation list for every conversation selection
    // The conversation details are handled by MessengerDetail.vue
    console.log('Conversation selected, details will be loaded by MessengerDetail.vue')
  }
}, { immediate: true })
```

### 5. **Removed Redundant API Calls**
- Removed `fetchUnreadCounts()` from `refreshConversationList()`
- Removed `fetchUnreadCounts()` from route path watchers
- Removed `fetchUnreadCounts()` from socket event handlers

## Benefits of the Fix

### 1. **Performance Improvement**
- Eliminated continuous API calls
- Reduced server load
- Faster messenger interface response

### 2. **Better Resource Management**
- Prevents multiple simultaneous API calls
- Uses existing data from main API responses
- Leverages real-time socket updates

### 3. **Maintained Functionality**
- Unread counts still update in real-time via socket events
- Conversation list still refreshes when needed
- All existing features remain functional

## Technical Details

### API Call Flow (Before Fix)
1. `conversationsResource` loads data
2. Deep watcher triggers `fetchUnreadCounts()`
3. Socket events trigger additional `fetchUnreadCounts()` calls
4. Route changes trigger `refreshConversationList()`
5. Multiple simultaneous API calls occur

### API Call Flow (After Fix)
1. `conversationsResource` loads data with unread counts included
2. Socket events directly update unread counts without API calls
3. Route changes only reload when necessary
4. Single API call per conversation list load

### Socket Event Handling
- `messenger:unread_update` directly updates `unreadMessageCounts.value`
- No additional API calls needed for real-time updates
- Efficient state management

## Testing

### Verification Steps
1. Open browser dev tools Network tab
2. Navigate to messenger page
3. Verify no continuous API calls for unread counts
4. Test real-time message updates
5. Verify unread counts still update correctly
6. Test conversation switching
7. Verify performance improvement

### Expected Behavior
- No continuous API calls in Network tab
- Unread counts update in real-time via socket events
- Conversation list loads once per page visit
- Smooth performance without lag

## Files Modified

- `apps/crm/frontend/src/pages/MessengerLayout.vue`
  - Removed problematic deep watcher
  - Added API call prevention logic
  - Optimized socket event handlers
  - Updated route watchers

## Backward Compatibility

- All existing functionality remains intact
- Real-time updates still work
- Unread counts still display correctly
- No breaking changes to user interface

## Future Considerations

1. **Monitor Performance**: Keep an eye on network activity to ensure the fix is effective
2. **Socket Reliability**: Ensure socket events are reliable for real-time updates
3. **Caching Strategy**: Consider implementing more aggressive caching if needed
4. **Error Handling**: Add better error handling for socket disconnections 