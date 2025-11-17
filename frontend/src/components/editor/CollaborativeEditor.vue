<template>
  <div class="collaborative-editor">
    <!-- Header with session info -->
    <div class="editor-header bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <!-- Session status indicator -->
          <div class="flex items-center space-x-2">
            <div
              :class="sessionStatusIndicatorClass"
              class="w-2 h-2 rounded-full"
            ></div>
            <span class="text-sm font-medium">{{ sessionStatusText }}</span>
          </div>

          <!-- Participant count -->
          <div v-if="sessionInfo" class="flex items-center space-x-1 text-sm text-gray-600">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
            </svg>
            <span>{{ sessionInfo.participant_count || 0 }} participant(s)</span>
          </div>
        </div>

        <!-- Controls -->
        <div class="flex items-center space-x-2">
          <button
            @click="toggleCollaborativeMode"
            :class="collaborativeMode ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'"
            class="px-3 py-1 rounded-md text-sm font-medium hover:bg-opacity-80 transition-colors"
          >
            {{ collaborativeMode ? 'Exit Collaborative Mode' : 'Start Collaborative Editing' }}
          </button>

          <button
            v-if="collaborativeMode"
            @click="showSessionInfo = !showSessionInfo"
            class="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            title="Session Information"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Session info panel -->
      <div v-if="showSessionInfo && sessionInfo" class="mt-3 p-3 bg-blue-50 rounded-md border border-blue-200">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span class="font-medium text-gray-700">Session ID:</span>
            <span class="text-gray-600 ml-1">{{ sessionInfo.id?.substring(0, 8) }}...</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Created:</span>
            <span class="text-gray-600 ml-1">{{ formatDate(sessionInfo.created_at) }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Status:</span>
            <span class="text-gray-600 ml-1 capitalize">{{ sessionInfo.status }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700">Last Activity:</span>
            <span class="text-gray-600 ml-1">{{ formatDate(sessionInfo.last_activity) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Main editor area -->
    <div class="flex flex-1">
      <!-- Editor panel -->
      <div class="flex-1 relative">
        <RichTextEditor
          v-model="localContent"
          :placeholder="placeholder"
          :editable="true"
          @autoSave="enhancedHandleContentChange"
          ref="editorRef"
          class="h-full"
        />

        <!-- User cursors overlay -->
        <div v-if="collaborativeMode" class="absolute inset-0 pointer-events-none">
          <!-- Current user cursor -->
          <div
            v-if="currentUserCursor.visible"
            :style="{ left: currentUserCursor.x + 'px', top: currentUserCursor.y + 'px' }"
            class="absolute pointer-events-none"
          >
            <div class="w-0.5 h-4 bg-blue-500 rounded-sm"></div>
            <div class="text-xs bg-blue-500 text-white px-1 py-0.5 rounded whitespace-nowrap ml-1">
              You
            </div>
          </div>

          <!-- Other users' cursors -->
          <div
            v-for="cursor in otherUserCursors"
            :key="cursor.participant_id"
            :style="{ left: cursor.x + 'px', top: cursor.y + 'px' }"
            class="absolute pointer-events-none"
          >
            <div :style="{ backgroundColor: cursor.color }" class="w-0.5 h-4 rounded-sm"></div>
            <div class="text-xs text-white px-1 py-0.5 rounded whitespace-nowrap ml-1"
                 :style="{ backgroundColor: cursor.color }">
              {{ cursor.username }}
            </div>
          </div>
        </div>
      </div>

      <!-- Participants sidebar -->
      <div v-if="collaborativeMode && participants.length > 0" class="w-64 bg-white border-l border-gray-200">
        <div class="p-4">
          <h3 class="text-sm font-medium text-gray-900 mb-3">Participants</h3>
          <div class="space-y-3">
            <div
              v-for="participant in participants"
              :key="participant.participant_id"
              class="flex items-center space-x-3"
            >
              <div class="relative">
                <div
                  :style="{ backgroundColor: participant.user_color }"
                  class="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
                >
                  {{ getInitials(participant.username) }}
                </div>
                <div
                  :class="participant.is_active ? 'bg-green-400' : 'bg-gray-400'"
                  class="absolute -bottom-0.5 -right-0.5 w-3 h-3 border-2 border-white rounded-full"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ participant.full_name || participant.username }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ participant.is_active ? 'Active' : 'Away' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Connection status overlay -->
    <div
      v-if="showConnectionStatus"
      class="absolute bottom-4 right-4 bg-black bg-opacity-75 text-white px-3 py-2 rounded-md text-sm"
    >
      <div class="flex items-center space-x-2">
        <div
          :class="connectionStatus.iconClass"
          class="w-4 h-4"
        ></div>
        <span>{{ connectionStatus.message }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { diff_match_patch } from 'diff-match-patch'
import RichTextEditor from './RichTextEditor.vue'

// Props
interface Props {
  modelValue: string
  articleId: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Start writing...',
})

// Emits
interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'sessionStarted', sessionInfo: any): void
  (e: 'sessionEnded'): void
  (e: 'participantJoined', participant: any): void
  (e: 'participantLeft', participantId: string): void
}

const emit = defineEmits<Emits>()

// Reactive state
const collaborativeMode = ref(false)
const showSessionInfo = ref(false)
const showConnectionStatus = ref(false)
const editorRef = ref()
const websocket = ref<WebSocket | null>(null)

// Session state
const sessionInfo = ref<any>(null)
const participants = ref<any[]>([])
const localContent = ref(props.modelValue)

// Operational Transform state
const lastContent = ref(props.modelValue) // Track last content for diff calculation
const pendingOperations = ref<any[]>([]) // Queue for local operations waiting to be sent
const operationSequence = ref(0) // Local operation sequence counter
const baseVersion = ref(0) // Base version this client is working from

// Offline synchronization
const offlineChanges = ref<any[]>([]) // Store changes made while offline
const isOnline = ref(navigator.onLine)
const lastSyncedContent = ref(props.modelValue)

// Cursor tracking
const currentUserCursor = ref({
  visible: false,
  x: 0,
  y: 0,
  position: 0,
  selectionStart: 0,
  selectionEnd: 0
})

const otherUserCursors = ref<any[]>([])

// Typing indicators
const userTypingTimers = ref<Map<string, number>>(new Map())
const typingUsers = ref<Map<string, { username: string, color: string, timestamp: number }>>(new Map())

// Connection status
const connectionStatus = ref({
  status: 'disconnected',
  message: 'Disconnected',
  iconClass: 'text-red-400'
})

// Computed properties
const sessionStatusIndicatorClass = computed(() => {
  if (!collaborativeMode.value) return 'bg-gray-400'
  if (connectionStatus.value.status === 'connected') return 'bg-green-400'
  if (connectionStatus.value.status === 'connecting') return 'bg-yellow-400'
  return 'bg-red-400'
})

const sessionStatusText = computed(() => {
  if (!collaborativeMode.value) return 'Single User Mode'
  if (connectionStatus.value.status === 'connected') return 'Collaborative Mode'
  if (connectionStatus.value.status === 'connecting') return 'Connecting...'
  return 'Connection Lost'
})

// WebSocket management (original simple version for reference)
const originalConnectWebSocket = () => {
  if (!props.articleId) {
    console.error('No article ID provided for collaborative editing')
    return
  }

  showConnectionStatus.value = true
  connectionStatus.value = {
    status: 'connecting',
    message: 'Connecting to collaborative session...',
    iconClass: 'text-yellow-400 animate-pulse'
  }

  try {
    // Connect to Django Channels WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/articles/${props.articleId}/collaborate/`

    websocket.value = new WebSocket(wsUrl)

    websocket.value.onopen = () => {
      connectionStatus.value = {
        status: 'connected',
        message: 'Connected to collaborative session',
        iconClass: 'text-green-400'
      }

      // Auto-hide status after 3 seconds
      setTimeout(() => {
        showConnectionStatus.value = false
      }, 3000)

      console.log('WebSocket connected successfully')
    }

    websocket.value.onmessage = handleWebSocketMessage

    websocket.value.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)

      connectionStatus.value = {
        status: 'disconnected',
        message: event.code === 1000 ? 'Session ended' : 'Connection lost',
        iconClass: 'text-red-400'
      }

      showConnectionStatus.value = true

      // Attempt reconnection if it wasn't a deliberate close
      if (event.code !== 1000 && collaborativeMode.value) {
        setTimeout(() => {
          if (collaborativeMode.value) {
            console.log('Attempting to reconnect...')
            enhancedConnectWebSocket()
          }
        }, 3000)
      }
    }

    websocket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      connectionStatus.value = {
        status: 'error',
        message: 'Connection error',
        iconClass: 'text-red-400'
      }
      showConnectionStatus.value = true
    }

  } catch (error) {
    console.error('Failed to connect to WebSocket:', error)
    connectionStatus.value = {
      status: 'error',
      message: 'Failed to connect',
      iconClass: 'text-red-400'
    }
    showConnectionStatus.value = true
  }
}

const disconnectWebSocket = () => {
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
  }

  connectionStatus.value = {
    status: 'disconnected',
    message: 'Disconnected from collaborative session',
    iconClass: 'text-red-400'
  }

  sessionInfo.value = null
  participants.value = []
  otherUserCursors.value = []

  emit('sessionEnded')
}

// Mode toggling
const toggleCollaborativeMode = () => {
  if (collaborativeMode.value) {
    // Exit collaborative mode
    collaborativeMode.value = false
    disconnectWebSocket()
  } else {
    // Enter collaborative mode
    collaborativeMode.value = true
    enhancedConnectWebSocket()
  }
}

// Operational Transform utilities
const dmp = new diff_match_patch()
dmp.Diff_Timeout = 1.0 // 1 second timeout
dmp.Diff_EditCost = 4   // Make edits more expensive than matches

const createOperationFromDiff = (oldContent: string, newContent: string): any[] => {
  // Create fine-grained operations from diff using diff-match-patch
  if (oldContent === newContent) return []

  const diffs = dmp.diff_main(oldContent, newContent)

  // Clean up diffs for better performance
  dmp.diff_cleanupSemantic(diffs)
  dmp.diff_cleanupEfficiency(diffs)

  const operations = []
  let currentPosition = 0

  for (const [diffType, text] of diffs) {
    if (diffType === 0) { // EQUAL - advance position
      currentPosition += text.length
    } else if (diffType === 1) { // INSERT
      operations.push({
        type: 'insert',
        position: currentPosition,
        text: text,
        timestamp: new Date().toISOString()
      })
      currentPosition += text.length
    } else if (diffType === -1) { // DELETE
      operations.push({
        type: 'delete',
        position: currentPosition,
        length: text.length,
        timestamp: new Date().toISOString()
      })
      // Don't advance position for deletes
    }
  }

  return operations.length === 1 ? [operations[0]] : operations
}

const createSingleOperation = (oldContent: string, newContent: string) => {
  // Create a single comprehensive operation for simple cases
  if (oldContent === newContent) return null

  const operations = createOperationFromDiff(oldContent, newContent)

  // If we have a single atomic operation, return it
  if (operations.length === 1) {
    return operations[0]
  }

  // For complex changes, fall back to replace operation
  return {
    type: 'replace',
    position: 0,
    old_text: oldContent,
    new_text: newContent,
    timestamp: new Date().toISOString()
  }
}

const applyOperationToContent = (content: string, operation: any) => {
  // Apply an operation to content
  const opType = operation.type
  const position = operation.position || 0

  if (opType === 'replace') {
    // Replace operation - in OT terms this represents the full content state
    return operation.new_text || content
  } else if (opType === 'insert') {
    const text = operation.text || ''
    return content.slice(0, position) + text + content.slice(position)
  } else if (opType === 'delete') {
    const length = operation.length || 0
    return content.slice(0, position) + content.slice(position + length)
  }

  return content
}

// Content change handling with OT
const handleContentChange = (content: string) => {
  if (!collaborativeMode.value) {
    lastContent.value = content
    localContent.value = content
    emit('update:modelValue', content)
    return
  }

  // Create operations from diff
  const operations = createOperationFromDiff(lastContent.value, content)
  if (operations.length === 0) return

  // For multiple operations, send them as a batch
  if (operations.length > 1) {
    // Apply all operations locally
    let currentContent = lastContent.value
    for (const op of operations) {
      currentContent = applyOperationToContent(currentContent, op)
    }

    localContent.value = currentContent
    lastContent.value = currentContent
    emit('update:modelValue', currentContent)

    // Send batch operation
    const sequenceNumber = ++operationSequence.value
    const operationMessage = {
      type: 'operation',
      operation: {
        type: 'batch',
        operations: operations
      },
      sequence_number: sequenceNumber,
      client_id: `client_${Date.now()}`
    }

    pendingOperations.value.push(operationMessage)

    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.send(JSON.stringify(operationMessage))
    }
  } else {
    // Single operation
    const operation = operations[0]

    // Apply operation locally (optimistic update)
    localContent.value = applyOperationToContent(localContent.value, operation)
    lastContent.value = localContent.value
    emit('update:modelValue', localContent.value)

    // Send operation
    const sequenceNumber = ++operationSequence.value
    const operationMessage = {
      type: 'operation',
      operation: operation,
      sequence_number: sequenceNumber,
      client_id: `client_${Date.now()}`
    }

    pendingOperations.value.push(operationMessage)

    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      websocket.value.send(JSON.stringify(operationMessage))
    }
  }
}

// Cursor tracking - text-based position tracking
const updateCursorPosition = (event?: MouseEvent) => {
  if (!editorRef.value || !editorRef.value.editor || !collaborativeMode.value) return

  try {
    // Get text position from editor
    const editor = editorRef.value.editor
    const { from, to } = editor.state.selection.main

    // Get screen coordinates for cursor display
    const coords = editor.view.coordsAtPos(from)

    currentUserCursor.value = {
      visible: true,
      x: coords?.left || 0,
      y: coords?.top || 0,
      position: from,
      selectionStart: from,
      selectionEnd: to
    }

    // Send cursor update via WebSocket
    if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
      const cursorUpdate = {
        type: 'cursor_update',
        cursor: {
          position: from,
          selection_start: from,
          selection_end: to,
          x: currentUserCursor.value.x,
          y: currentUserCursor.value.y
        }
      }

      websocket.value.send(JSON.stringify(cursorUpdate))
    }
  } catch (error) {
    console.error('Error updating cursor position:', error)
    // Fallback to mouse-based tracking if text-based fails
    if (event) {
      updateCursorPositionFallback(event)
    }
  }
}

const updateCursorPositionFallback = (event: MouseEvent) => {
  // Fallback cursor tracking using mouse position
  if (!editorRef.value || !collaborativeMode.value) return

  const editorBounds = editorRef.value.$el.getBoundingClientRect()
  const relativeX = event.clientX - editorBounds.left
  const relativeY = event.clientY - editorBounds.top

  currentUserCursor.value = {
    visible: true,
    x: Math.max(0, Math.min(relativeX, editorBounds.width)),
    y: Math.max(0, Math.min(relativeY, editorBounds.height)),
    position: 0,
    selectionStart: 0,
    selectionEnd: 0
  }

  // Send simplified cursor update
  if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
    const cursorUpdate = {
      type: 'cursor_update',
      cursor: {
        position: 0,
        selection_start: 0,
        selection_end: 0,
        x: currentUserCursor.value.x,
        y: currentUserCursor.value.y
      }
    }

    websocket.value.send(JSON.stringify(cursorUpdate))
  }
}

// Helper functions
const getInitials = (name: string): string => {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleString()
  } catch {
    return dateString
  }
}

// WebSocket message handlers
const handleWebSocketMessage = (event: any) => {
  const data = JSON.parse(event.data)

  switch (data.type) {
    case 'initial_state':
      handleInitialState(data)
      break

    case 'user_joined':
      handleUserJoined(data)
      break

    case 'user_left':
      handleUserLeft(data)
      break

    case 'operation_applied':
      handleOperationApplied(data)
      break

    case 'cursor_updated':
      handleCursorUpdated(data)
      break

    case 'operation_ack':
      handleOperationAck(data)
      break

    case 'operation_rejected':
      handleOperationRejected(data)
      break

    case 'user_typing':
      handleUserTyping(data)
      break

    case 'user_stopped_typing':
      handleUserStoppedTyping(data)
      break

    default:
      console.log('Unknown message type:', data.type)
  }
}

// Message handlers
const handleInitialState = (data: any) => {
  sessionInfo.value = data.session
  participants.value = data.participants

  // Set initial content and base version
  if (data.article) {
    localContent.value = data.article.content || data.article.current_content || ''
    lastContent.value = localContent.value
    emit('update:modelValue', localContent.value)
  }

  baseVersion.value = data.session?.base_version || 0
  operationSequence.value = data.session?.operation_sequence || 0

  emit('sessionStarted', sessionInfo.value)
}

const handleUserJoined = (data: any) => {
  // Update participants list
  const existingIndex = participants.value.findIndex(p => p.participant_id === data.participant_id)
  if (existingIndex >= 0) {
    participants.value[existingIndex] = { ...participants.value[existingIndex], ...data.user, is_active: true }
  } else {
    participants.value.push({ ...data.user, is_active: true })
  }

  emit('participantJoined', data.user)
}

const handleUserLeft = (data: any) => {
  // Remove or mark participant as inactive
  const index = participants.value.findIndex(p => p.participant_id === data.participant_id)
  if (index >= 0) {
    participants.value[index].is_active = false
  }

  // Remove from cursors
  const cursorIndex = otherUserCursors.value.findIndex(c => c.participant_id === data.participant_id)
  if (cursorIndex >= 0) {
    otherUserCursors.value.splice(cursorIndex, 1)
  }

  emit('participantLeft', data.participant_id)
}

const handleOperationApplied = (data: any) => {
  const remoteOperation = data.operation

  if (!remoteOperation) return

  // Apply the remote operation to our local content
  const newContent = applyOperationToContent(localContent.value, remoteOperation.operation)
  localContent.value = newContent
  lastContent.value = newContent

  // Update the editor (this will trigger the v-model update)
  emit('update:modelValue', newContent)

  console.log('Applied remote operation:', remoteOperation)
}

const handleCursorUpdated = (data: any) => {
  // Update other users' cursors
  const cursorIndex = otherUserCursors.value.findIndex(
    c => c.participant_id === data.participant_id
  )

  if (cursorIndex >= 0) {
    otherUserCursors.value[cursorIndex] = {
      ...otherUserCursors.value[cursorIndex],
      x: data.cursor?.x || 0,
      y: data.cursor?.y || 0
    }
  } else {
    // Add new cursor - get participant info
    const participant = participants.value.find(p => p.id === data.user_id)
    otherUserCursors.value.push({
      participant_id: data.participant_id,
      username: participant?.username || 'User',
      color: participant?.user_color || '#10B981',
      x: data.cursor?.x || 0,
      y: data.cursor?.y || 0
    })
  }
}

const handleOperationAck = (data: any) => {
  // Remove acknowledged operation from pending queue
  const ackedIndex = pendingOperations.value.findIndex(
    op => op.sequence_number === data.sequence_number
  )
  if (ackedIndex >= 0) {
    pendingOperations.value.splice(ackedIndex, 1)
  }
}

const handleOperationRejected = (data: any) => {
  console.warn('Operation rejected:', data.reason)

  // Handle rejection - potentially revert local changes
  // For now, just log the rejection
  // In a production implementation, you might need to handle conflicts
}

// Typing indicator handlers
const handleUserTyping = (data: any) => {
  const participantId = data.participant_id || data.user_id
  const participant = participants.value.find(p => p.participant_id === participantId || p.id === participantId)

  if (participant) {
    // Clear existing timer for this user
    const existingTimer = userTypingTimers.value.get(participantId)
    if (existingTimer) {
      clearTimeout(existingTimer)
    }

    // Add or update typing user
    typingUsers.value.set(participantId, {
      username: participant.username,
      color: participant.user_color || '#10B981',
      timestamp: Date.now()
    })

    // Set timer to remove typing indicator after 3 seconds
    const timer = setTimeout(() => {
      typingUsers.value.delete(participantId)
      userTypingTimers.value.delete(participantId)
    }, 3000)

    userTypingTimers.value.set(participantId, timer)
  }
}

const handleUserStoppedTyping = (data: any) => {
  const participantId = data.participant_id || data.user_id

  // Clear timer and remove typing user
  const timer = userTypingTimers.value.get(participantId)
  if (timer) {
    clearTimeout(timer)
    userTypingTimers.value.delete(participantId)
  }

  typingUsers.value.delete(participantId)
}

// Typing detection - send typing events when user is actively editing
const sendTypingStart = () => {
  if (!websocket.value || websocket.value.readyState !== WebSocket.OPEN) return

  const message = {
    type: 'user_typing',
    timestamp: Date.now()
  }

  websocket.value.send(JSON.stringify(message))
}

const sendTypingStop = () => {
  if (!websocket.value || websocket.value.readyState !== WebSocket.OPEN) return

  const message = {
    type: 'user_stopped_typing',
    timestamp: Date.now()
  }

  websocket.value.send(JSON.stringify(message))
}

// Offline synchronization functions
const handleOnline = () => {
  isOnline.value = true
  console.log('Back online - attempting to sync changes')

  if (collaborativeMode.value && offlineChanges.value.length > 0) {
    // Try to reconnect if we're in collaborative mode
    enhancedConnectWebSocket()
  }
}

const handleOffline = () => {
  isOnline.value = false
  console.log('Gone offline - storing changes locally')

  connectionStatus.value = {
    status: 'offline',
    message: 'Offline - changes will sync when reconnected',
    iconClass: 'text-orange-400'
  }
  showConnectionStatus.value = true
}

const syncOfflineChanges = () => {
  if (!websocket.value || websocket.value.readyState !== WebSocket.OPEN) {
    return
  }

  console.log('Syncing offline changes:', offlineChanges.value.length)

  // Send all offline changes in order
  offlineChanges.value.forEach(change => {
    if (websocket.value) {
      websocket.value.send(JSON.stringify(change))
    }
  })

  // Clear offline changes after sending
  offlineChanges.value = []
  lastSyncedContent.value = localContent.value

  console.log('Offline changes synced successfully')
}

// Update content change handling to work offline
const handleContentChangeOffline = (content: string) => {
  if (!isOnline.value && collaborativeMode.value) {
    // Store changes offline
    const operation = createOperationFromDiff(lastContent.value, content)
    if (operation) {
      offlineChanges.value.push({
        type: 'operation',
        operation: operation,
        sequence_number: ++operationSequence.value,
        client_id: `client_${Date.now()}`,
        timestamp: Date.now()
      })

      // Still apply locally
      localContent.value = applyOperationToContent(localContent.value, operation)
      lastContent.value = localContent.value
      emit('update:modelValue', localContent.value)

      console.log('Change stored offline:', offlineChanges.value.length, 'changes pending')
    }
  } else {
    // Normal online operation
    handleContentChange(content)
  }
}

// Enhanced connection monitoring
const websocketOnOpen = () => {
  connectionStatus.value = {
    status: 'connected',
    message: 'Connected to collaborative session',
    iconClass: 'text-green-400'
  }

  // Sync offline changes when reconnected
  if (offlineChanges.value.length > 0) {
    syncOfflineChanges()
  }

  // Auto-hide status after 3 seconds
  setTimeout(() => {
    showConnectionStatus.value = false
  }, 3000)

  console.log('WebSocket connected successfully')
}

// Update WebSocket connection to use enhanced handlers
const updateWebSocketHandlers = () => {
  if (websocket.value) {
    websocket.value.onopen = websocketOnOpen
    websocket.value.onmessage = handleWebSocketMessage
    websocket.value.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason)

      connectionStatus.value = {
        status: isOnline.value ? 'disconnected' : 'offline',
        message: isOnline.value ? (event.code === 1000 ? 'Session ended' : 'Connection lost') :
                 'Offline - changes will sync when reconnected',
        iconClass: isOnline.value ? 'text-red-400' : 'text-orange-400'
      }

      showConnectionStatus.value = true

      // Clear online cursors when disconnected
      if (!isOnline.value) {
        otherUserCursors.value = []
      }

      // Attempt reconnection if it wasn't a deliberate close and we're online
      if (event.code !== 1000 && collaborativeMode.value && isOnline.value) {
        setTimeout(() => {
          if (collaborativeMode.value && isOnline.value) {
            console.log('Attempting to reconnect...')
            enhancedConnectWebSocket()
          }
        }, 3000)
      }
    }
    websocket.value.onerror = (error) => {
      console.error('WebSocket error:', error)
      connectionStatus.value = {
        status: 'error',
        message: isOnline.value ? 'Connection error' : 'Offline',
        iconClass: 'text-red-400'
      }
      showConnectionStatus.value = true
    }
  }
}

// Reconnect with exponential backoff
let reconnectAttempts = 0
const maxReconnectAttempts = 5
const baseReconnectDelay = 1000

const scheduleReconnect = () => {
  if (reconnectAttempts >= maxReconnectAttempts) {
    console.log('Max reconnection attempts reached')
    connectionStatus.value = {
      status: 'disconnected',
      message: 'Unable to reconnect. Please refresh the page.',
      iconClass: 'text-red-400'
    }
    return
  }

  const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts)
  reconnectAttempts++

  console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`)

  setTimeout(() => {
    if (collaborativeMode.value && isOnline.value) {
      enhancedConnectWebSocket()
    }
  }, delay)
}

// Lifecycle
watch(() => props.modelValue, (newContent) => {
  if (newContent !== localContent.value) {
    localContent.value = newContent
  }
})

onMounted(() => {
  // Add event listeners
  document.addEventListener('mousemove', updateCursorPosition)
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', updateCursorPosition)
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)

  // Clean up WebSocket connection
  if (websocket.value) {
    disconnectWebSocket()
  }
})

// Update the connectWebSocket function to use new handlers
const enhancedConnectWebSocket = () => {
  if (!props.articleId) {
    console.error('No article ID provided for collaborative editing')
    return
  }

  showConnectionStatus.value = true
  connectionStatus.value = {
    status: 'connecting',
    message: 'Connecting to collaborative session...',
    iconClass: 'text-yellow-400 animate-pulse'
  }

  try {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/articles/${props.articleId}/collaborate/`

    websocket.value = new WebSocket(wsUrl)
    updateWebSocketHandlers()

  } catch (error) {
    console.error('Failed to connect to WebSocket:', error)
    connectionStatus.value = {
      status: 'error',
      message: 'Failed to connect',
      iconClass: 'text-red-400'
    }
    showConnectionStatus.value = true
  }
}

// Enhanced content change handler
const enhancedHandleContentChange = (content: string) => {
  if (!isOnline.value && collaborativeMode.value) {
    // Store changes offline
    const operation = createOperationFromDiff(lastContent.value, content)
    if (operation) {
      offlineChanges.value.push({
        type: 'operation',
        operation: operation,
        sequence_number: ++operationSequence.value,
        client_id: `client_${Date.now()}`,
        timestamp: Date.now()
      })

      // Still apply locally
      localContent.value = applyOperationToContent(localContent.value, operation)
      lastContent.value = localContent.value
      emit('update:modelValue', localContent.value)

      console.log('Change stored offline:', offlineChanges.value.length, 'changes pending')
    }
  } else {
    // Normal online operation
    handleContentChange(content)
  }
}

// Export for testing
if (import.meta.env.DEV) {
  // @ts-ignore
  window.collabEditorDebug = {
    getOfflineChanges: () => offlineChanges.value,
    getPendingOperations: () => pendingOperations.value,
    getConnectionStatus: () => connectionStatus.value,
    forceDisconnect: disconnectWebSocket,
    forceReconnect: enhancedConnectWebSocket
  }
}
</script>

<style scoped>
.collaborative-editor {
  @apply flex flex-col h-full;
}

.editor-header {
  @apply bg-white border-b border-gray-200;
}

/* Custom styles for collaborative features */
.cursor-caret {
  @apply absolute w-0.5 bg-blue-500 rounded-sm transition-all duration-75;
}

.participant-avatar {
  @apply relative inline-block;
}

.participant-avatar .status-indicator {
  @apply absolute -bottom-0.5 -right-0.5 w-3 h-3 border-2 border-white rounded-full;
}

.participant-avatar .status-indicator.active {
  @apply bg-green-400;
}

.participant-avatar .status-indicator.away {
  @apply bg-yellow-400;
}

.participant-avatar .status-indicator.offline {
  @apply bg-gray-400;
}
</style>
