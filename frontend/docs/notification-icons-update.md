# Notification Icons Update

## Overview
Updated the CRM notification system to display appropriate icons based on the notification type for better visual identification and user experience.

## Changes Made

### Files Modified
1. `apps/crm/frontend/src/components/Notifications.vue` - Desktop notification component
2. `apps/crm/frontend/src/pages/MobileNotification.vue` - Mobile notification component

### Icon Mapping
Based on the CRM Notification doctype types, the following icon mapping has been implemented:

| Notification Type | Icon Used | Icon Source |
|------------------|-----------|-------------|
| `WhatsApp` | WhatsAppIcon | `@/components/Icons/WhatsAppIcon.vue` |
| `Messenger` | MessengerIcon | `@/components/Icons/Messenger.vue` |
| `Instagram` | InstagramIcon | `@/components/Icons/InstagramIcon.vue` |
| `Custom` | ChatIcon | `@/components/Icons/ChatIcon.vue` |
| All other types | UserAvatar | Default user avatar |

### Implementation Details

#### Template Changes
Added conditional rendering logic in both components:

```vue
<WhatsAppIcon v-if="n.type == 'WhatsApp'" class="size-7" />
<MessengerIcon v-else-if="n.type == 'Messenger'" class="size-7" />
<InstagramIcon v-else-if="n.type == 'Instagram'" class="size-7" />
<ChatIcon v-else-if="n.type == 'Custom'" class="size-7" />
<UserAvatar v-else :user="n.from_user.name" size="lg" />
```

#### Script Changes
Added necessary icon imports to both components:

```javascript
import MessengerIcon from '@/components/Icons/Messenger.vue'
import InstagramIcon from '@/components/Icons/InstagramIcon.vue'
import ChatIcon from '@/components/Icons/ChatIcon.vue'
```

## Rationale
- **Enhanced User Experience**: Users can quickly identify the source/platform of notifications through visual icons
- **Consistency**: Aligns with the existing WhatsApp notification icon implementation
- **Scalability**: Easy to add more notification types in the future by following the same pattern
- **Platform Recognition**: Icons help users distinguish between different messaging platforms (WhatsApp, Messenger, Instagram)

## Usage Instructions
The notification icons will automatically display based on the `type` field in the CRM Notification doctype. No additional configuration is required.

## Technical Notes
- All icons maintain consistent sizing (`size-7` class)
- Fallback to UserAvatar for any notification types not explicitly handled
- Changes apply to both desktop and mobile notification views
- Icons are sourced from the existing Icons component library

## Future Considerations
- Additional notification types can be easily added by following the same pattern
- Icon styling can be customized by modifying the CSS classes
- Consider adding tooltips for better accessibility 