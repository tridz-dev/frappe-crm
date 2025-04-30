<template>
  <div class="h-full flex">
    <!-- Left Column: Conversations List -->
    <div class="w-80 border-r border-gray-200 flex flex-col">
      <div class="p-4 border-b border-gray-200">
        <h2 class="text-lg font-medium">Messages</h2>
      </div>
      
      <!-- Conversations List -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-for="i in 10"
          :key="i"
          class="p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100"
        >
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-full bg-gray-200"></div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between">
                <p class="text-sm font-medium truncate">Contact Name</p>
                <p class="text-xs text-gray-500">3m ago</p>
              </div>
              <p class="text-sm text-gray-500 truncate">
                Latest message preview...
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Column: Chat View -->
    <div class="flex-1 flex flex-col">
      <!-- Chat Header -->
      <div class="p-4 border-b border-gray-200 flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full bg-gray-200"></div>
        <div>
          <h3 class="font-medium">Contact Name</h3>
          <p class="text-sm text-gray-500">Active now</p>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 overflow-y-auto p-4 space-y-4">
        <!-- Sample messages -->
        <div v-for="i in 5" :key="i">
          <!-- Received message -->
          <div class="flex items-end mb-4">
            <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 mr-2"></div>
            <div class="bg-gray-100 rounded-lg rounded-bl-none px-4 py-2 max-w-[70%]">
              <p class="text-sm">This is a received message.</p>
            </div>
          </div>

          <!-- Sent message -->
          <div class="flex items-end justify-end mb-4">
            <div class="bg-blue-500 text-white rounded-lg rounded-br-none px-4 py-2 max-w-[70%]">
              <p class="text-sm">This is a sent message.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Input -->
      <div class="p-4 border-t border-gray-200">
        <div class="flex items-center space-x-2">
          <button class="p-2 hover:bg-gray-100 rounded-full">
            <span class="text-gray-500">
              <!-- Emoji icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </span>
          </button>
          <input
            type="text"
            placeholder="Type a message..."
            class="flex-1 border border-gray-200 rounded-full px-4 py-2 focus:outline-none focus:border-blue-500"
          />
          <button class="p-2 hover:bg-gray-100 rounded-full">
            <span class="text-blue-500">
              <!-- Send icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Component logic will be added later
</script> 