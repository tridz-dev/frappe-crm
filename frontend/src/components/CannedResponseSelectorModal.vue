<template>
  <Dialog
    v-model="show"
    :options="{
      title: __('Canned Responses'),
      size: '4xl',
    }"
  >
    <template #body-content>
      <TextInput
        ref="searchInput"
        v-model="search"
        type="text"
        :placeholder="__('Search canned responses...')"
      >
        <template #prefix>
          <FeatherIcon name="search" class="h-4 w-4 text-gray-500" />
        </template>
      </TextInput>
      <div
        v-if="filteredTemplates.length"
        class="mt-2 grid max-h-[560px] grid-cols-1 md:grid-cols-3 gap-2 overflow-y-auto"
      >
        <div
          v-for="template in filteredTemplates"
          :key="template.name"
          class="flex h-56 cursor-pointer flex-col gap-2 rounded-lg border p-3 hover:bg-gray-100"
          @click="handleTemplateSelect(template)"
        >
          <div class="border-b pb-2 text-base font-semibold">
            {{ template.title }}
          </div>
          <div 
            class="flex-1 overflow-hidden text-sm text-gray-600 prose prose-sm max-w-none"
            v-html="formatMessage(template.message)"
          />
        </div>
      </div>
      <div v-else class="mt-2">
        <div class="flex h-56 flex-col items-center justify-center">
          <div class="text-lg text-gray-500">
            {{ __('No canned responses found') }}
          </div>
        </div>
      </div>
      <!-- <div class="flex justify-end mt-4">
        <Button
          :label="__('New Canned Response')"
          @click="
            () => {
              $router.push('/canned-responses#new');
              templates.data = null;
            }
          "
        />
      </div> -->
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { createListResource, Dialog, TextInput, Button, FeatherIcon } from 'frappe-ui'

const props = defineProps({
  doctype: {
    type: String,
    default: 'Messenger Canned Response'
  }
})

const show = defineModel()
const searchInput = ref('')
const emit = defineEmits(['apply'])
const search = ref('')

const templates = createListResource({
  type: 'list',
  doctype: 'Messenger Canned Response',
  cache: ['cannedResponses', props.doctype],
  fields: ['title', 'message', 'modified'],
  orderBy: 'modified desc',
  pageLength: 99999
})

onMounted(() => {
  if (templates.data == null) {
    templates.fetch()
  }
})

const filteredTemplates = computed(() => {
  return templates.data?.filter((template) => {
    return template.title.toLowerCase().includes(search.value.toLowerCase())
  }) ?? []
})

// Function to format message for display
function formatMessage(message) {
  if (!message) return ''
  
  // Convert markdown-style formatting to HTML
  message = message.replace(/_(.*?)_/g, '<i>$1</i>')
  message = message.replace(/\*(.*?)\*/g, '<b>$1</b>')
  message = message.replace(/~(.*?)~/g, '<s>$1</s>')
  message = message.replace(/```(.*?)```/g, '<code>$1</code>')
  message = message.replace(/`(.*?)`/g, '<code>$1</code>')
  message = message.replace(/^> (.*)$/gm, '<blockquote>$1</blockquote>')
  message = message.replace(/\n/g, '<br>')
  
  return message
}

// Function to strip HTML tags when applying the template
function stripHtmlTags(html) {
  const tmp = document.createElement('DIV')
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ''
}

// Function to handle template selection
function handleTemplateSelect(template) {
  // Strip HTML tags when applying the template
  const cleanMessage = stripHtmlTags(template.message)
  emit('apply', {
    ...template,
    message: cleanMessage
  })
}

watch(show, (value) => value && nextTick(() => searchInput.value?.el?.focus()))
</script>

<style>
.prose {
  @apply text-gray-600;
}
.prose :where(p, span, a) {
  @apply !text-gray-600;
}
.prose :where(code) {
  @apply !bg-gray-100 !text-gray-800 !px-1 !py-0.5 !rounded;
}
.prose :where(blockquote) {
  @apply !border-l-2 !border-gray-300 !pl-2 !italic;
}
</style> 