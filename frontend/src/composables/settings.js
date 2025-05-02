import { createResource } from 'frappe-ui'
import { computed, ref } from 'vue'

export const whatsappEnabled = ref(false)
export const isWhatsappInstalled = ref(false)
export const messengerEnabled = ref(false)
export const isMessengerInstalled = ref(false)

// Check if WhatsApp is enabled
createResource({
  url: 'crm.api.whatsapp.is_whatsapp_enabled',
  cache: 'Is Whatsapp Enabled',
  auto: true,
  onSuccess: (data) => {
    whatsappEnabled.value = Boolean(data)
  },
})

// Check if WhatsApp is installed
createResource({
  url: 'crm.api.whatsapp.is_whatsapp_installed',
  cache: 'Is Whatsapp Installed',
  auto: true,
  onSuccess: (data) => {
    isWhatsappInstalled.value = Boolean(data)
  },
})

// Check if Messenger is enabled
createResource({
  url: 'crm.api.messenger.is_messenger_enabled',
  cache: 'Is Messenger Enabled',
  auto: true,
  onSuccess: (data) => {
    messengerEnabled.value = Boolean(data)
  },
})

// Check if Messenger is installed
createResource({
  url: 'crm.api.messenger.is_messenger_installed',
  cache: 'Is Messenger Installed',
  auto: true,
  onSuccess: (data) => {
    isMessengerInstalled.value = Boolean(data)
  },
})

export const callEnabled = ref(false)
export const twilioEnabled = ref(false)
export const exotelEnabled = ref(false)
export const defaultCallingMedium = ref('')
createResource({
  url: 'crm.integrations.api.is_call_integration_enabled',
  cache: 'Is Call Integration Enabled',
  auto: true,
  onSuccess: (data) => {
    twilioEnabled.value = Boolean(data.twilio_enabled)
    exotelEnabled.value = Boolean(data.exotel_enabled)
    defaultCallingMedium.value = data.default_calling_medium
    callEnabled.value = twilioEnabled.value || exotelEnabled.value
  },
})

export const mobileSidebarOpened = ref(false)

export const isMobileView = computed(() => window.innerWidth < 768)

export const showSettings = ref(false)
export const activeSettingsPage = ref('')
