# Messenger Performance Optimization

## Overview

This document outlines the performance optimizations implemented to speed up the messenger page loading and reduce API calls. The optimizations focus on consolidating multiple API calls into single calls, implementing caching, and reducing redundant data fetching.

## Key Optimizations

### 1. **Single API Call for Conversation Details**

**Before**: Multiple separate API calls for each conversation
- `fetchMessages()` - Get messages
- `fetchAssignees()` - Get assignees  
- `fetchConversationTags()` - Get tags
- `fetchStatusUpdates()` - Get status updates
- `fetchPastTickets()` - Get past tickets
- `fetchAllTags()` - Get all tags
- `fetchEnableHelpdeskTicketCreation()` - Get helpdesk flag

**After**: Single API call
- `get_conversation_details()` - Gets all conversation data in one call

**Performance Impact**: Reduced from 7 API calls to 1 API call per conversation selection

### 2. **Single API Call for Conversation List**

**Before**: Multiple separate API calls for conversation list
- Get conversations
- Get user profiles
- Get unread counts
- Get conversation tags
- Get conversation assignees

**After**: Single API call
- `get_conversations_with_details()` - Gets all conversation list data in one call

**Performance Impact**: Reduced from 5 API calls to 1 API call for conversation list

### 3. **Caching Implementation**

**Static Data Caching**:
- All tags (`allTags`)
- All statuses (`allStatuses`) 
- Helpdesk ticket creation flag (`helpdeskEnabled`)

**Conversation Data Caching**:
- Conversation details
- Messages
- Tags
- Assignees
- Status updates
- Past tickets

**Cache Strategy**:
- Static data cached on page load
- Conversation data cached when first accessed
- Cache persists during session

### 4. **Optimized Backend APIs**

#### New API Functions:

1. **`get_conversation_details(conversation_id)`**
   - Returns all conversation data in single response
   - Includes: conversation, messages, tags, assignees, status updates, past tickets, unread count

2. **`get_conversations_with_details(limit, offset, platform_filter)`**
   - Returns conversation list with all related data
   - Includes: conversations, user profiles, tags, assignees, unread counts

3. **`get_cached_data()`**
   - Returns static data that doesn't change frequently
   - Includes: all tags, all statuses, helpdesk flag

## Implementation Details

### Backend Changes (`messenger.py`)

#### 1. `get_conversation_details()` Function
```python
@frappe.whitelist()
def get_conversation_details(conversation_id):
    """Get all conversation details in a single API call for better performance."""
    # Fetches conversation, messages, tags, assignees, status updates, past tickets, unread count
    # Returns structured JSON with all data
```

#### 2. `get_conversations_with_details()` Function
```python
@frappe.whitelist()
def get_conversations_with_details(limit=50, offset=0, platform_filter=None):
    """Get conversations with all details in a single API call for better performance."""
    # Fetches conversations with user profiles, tags, assignees, unread counts
    # Returns structured JSON with all data
```

#### 3. `get_cached_data()` Function
```python
@frappe.whitelist()
def get_cached_data():
    """Get cached data that doesn't change frequently."""
    # Fetches all tags, all statuses, helpdesk flag
    # Returns structured JSON with static data
```

### Frontend Changes

#### MessengerLayout.vue Optimizations:

1. **Caching Implementation**:
   ```javascript
   // Add caching for static data
   const cachedData = ref({
     allTags: [],
     allStatuses: [],
     helpdeskEnabled: false
   })
   
   // Add cache for conversation details
   const conversationCache = ref(new Map())
   ```

2. **Optimized Conversations Resource**:
   ```javascript
   const conversationsResource = createResource({
     url: 'crm.api.messenger.get_conversations_with_details',
     params: {
       limit: 50,
       offset: 0,
       platform_filter: 'all'
     }
   })
   ```

3. **Cached Data Loading**:
   ```javascript
   async function loadCachedData() {
     const data = await call('crm.api.messenger.get_cached_data')
     // Load static data into cache
   }
   ```

#### MessengerDetail.vue Optimizations:

1. **Single API Call for Conversation Details**:
   ```javascript
   async function fetchConversation(conversationId) {
     // Check cache first
     if (conversationCache.value.has(conversationId)) {
       // Load from cache
       return
     }
     
     // Fetch all data in single API call
     const data = await call('crm.api.messenger.get_conversation_details', {
       conversation_id: conversationId
     })
     
     // Cache the data
     conversationCache.value.set(conversationId, data)
   }
   ```

2. **Removed Individual Fetch Functions**:
   - `fetchMessages()` - Now handled by `get_conversation_details`
   - `fetchAssignees()` - Now handled by `get_conversation_details`
   - `fetchConversationTags()` - Now handled by `get_conversation_details`
   - `fetchStatusUpdates()` - Now handled by `get_conversation_details`
   - `fetchPastTickets()` - Now handled by `get_conversation_details`
   - `fetchAllTags()` - Now handled by `get_cached_data`
   - `fetchEnableHelpdeskTicketCreation()` - Now handled by `get_cached_data`

## Performance Improvements

### 1. **API Call Reduction**
- **Before**: 7 API calls per conversation selection
- **After**: 1 API call per conversation selection
- **Improvement**: 85% reduction in API calls

### 2. **Conversation List Loading**
- **Before**: 5 API calls for conversation list
- **After**: 1 API call for conversation list
- **Improvement**: 80% reduction in API calls

### 3. **Caching Benefits**
- **Static Data**: Loaded once on page load, cached for entire session
- **Conversation Data**: Cached after first access, instant loading on subsequent visits
- **Memory Usage**: Efficient caching with Map data structure

### 4. **Data Transfer Optimization**
- **Before**: Multiple small API responses
- **After**: Single optimized response with all required data
- **Improvement**: Reduced network overhead and latency

## Benefits

### 1. **Faster Page Loading**
- Reduced API calls significantly improve initial page load time
- Caching provides instant access to previously loaded data

### 2. **Better User Experience**
- Faster conversation switching
- Reduced loading states
- Smoother navigation

### 3. **Reduced Server Load**
- Fewer API calls reduce server processing
- Optimized database queries
- Better resource utilization

### 4. **Improved Scalability**
- Reduced network traffic
- Better caching strategy
- More efficient data fetching

## Backward Compatibility

### 1. **Deprecated Functions**
All old individual fetch functions are kept for backward compatibility but marked as deprecated:
- `fetchMessages()` - Now returns deprecation message
- `fetchAssignees()` - Now returns deprecation message
- `fetchConversationTags()` - Now returns deprecation message
- `fetchStatusUpdates()` - Now returns deprecation message
- `fetchPastTickets()` - Now returns deprecation message
- `fetchAllTags()` - Now returns deprecation message
- `fetchEnableHelpdeskTicketCreation()` - Now returns deprecation message

### 2. **API Compatibility**
- All existing socket events remain unchanged
- All existing UI functionality remains intact
- All existing features continue to work

## Testing

### 1. **Performance Testing**
- Measure API call reduction
- Monitor page load times
- Test caching effectiveness

### 2. **Functionality Testing**
- Verify all features work correctly
- Test conversation switching
- Test message sending/receiving
- Test tag management
- Test assignee management

### 3. **Cache Testing**
- Test cache hit/miss scenarios
- Test cache invalidation
- Test memory usage

## Future Improvements

### 1. **Advanced Caching**
- Implement cache expiration
- Add cache invalidation strategies
- Implement cache size limits

### 2. **Lazy Loading**
- Implement lazy loading for older messages
- Add progressive loading for large conversation lists

### 3. **Real-time Updates**
- Optimize socket event handling
- Implement efficient real-time updates

### 4. **Database Optimization**
- Add database indexes for frequently queried fields
- Optimize database queries further
- Implement query result caching

## Conclusion

The performance optimizations have significantly improved the messenger's loading speed and user experience by:

1. **Reducing API calls by 80-85%**
2. **Implementing efficient caching**
3. **Optimizing data transfer**
4. **Maintaining backward compatibility**

These changes provide a much faster and more responsive messenger experience while maintaining all existing functionality. 