<template>
  <div class="markdown-editor" @dragover.prevent @drop.prevent="handleDrop">
    <!-- Editor Toolbar -->
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center space-x-2">
        <button
          @click="insertMarkdown('**', '**')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Bold"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6 4v12h4.5c1.5 0 2.5-1 2.5-2.5S12 11 10.5 11H8V4H6zm2 5h2c.5 0 1 .5 1 1s-.5 1-1 1H8V9z"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('*', '*')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Italic"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8 4h4l-2 8H6l2-8zm-1 10h4l-1 2H6l1-2z"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('## ', '')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Heading"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4h3v12H3V4zm5 0h3v3H8V4zm5 0h3v12h-3V4zm-5 5h3v7H8V9z"/>
          </svg>
        </button>
        <div class="w-px h-4 bg-gray-300"></div>
        <button
          @click="insertMarkdown('- ', '')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="List"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 6h14v2H3V6zm0 4h14v2H3v-2zm0 4h14v2H3v-2z"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('[', '](url)')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Link"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('![', '](url)')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Image"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"/>
          </svg>
        </button>
        <div class="w-px h-4 bg-gray-300"></div>
        <button
          @click="insertMarkdown('```\n', '\n```')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Code Block"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('`', '`')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Inline Code"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6.5 3L4 9l2.5 6H8L5.5 9 8 3H6.5zm7 0L11 9l2.5 6h1.5L12.5 9 15 3h-1.5z"/>
          </svg>
        </button>
        <button
          @click="insertMarkdown('> ', '')"
          class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
          title="Quote"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="togglePreview"
          class="px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
        >
          {{ showPreview ? 'Edit' : 'Preview' }}
        </button>
      </div>
    </div>

    <!-- Editor Container -->
    <div class="border rounded-lg overflow-hidden">
      <!-- Split View -->
      <div v-if="!showPreview" class="grid grid-cols-1 lg:grid-cols-2">
        <!-- Text Editor -->
        <div class="border-r">
          <textarea
            ref="textareaRef"
            v-model="content"
            @input="updateContent"
            @keydown="handleKeydown"
            class="w-full h-96 p-4 font-mono text-sm resize-none focus:outline-none"
            placeholder="Write your markdown here..."
          ></textarea>
        </div>
        <!-- Preview -->
        <div class="bg-gray-50">
          <div 
            class="h-96 p-4 overflow-auto prose prose-sm max-w-none"
            v-html="previewContent"
          ></div>
        </div>
      </div>

      <!-- Full Preview -->
      <div v-else class="bg-gray-50">
        <div 
          class="h-96 p-4 overflow-auto prose prose-sm max-w-none"
          v-html="previewContent"
        ></div>
      </div>

      <!-- Full Editor -->
      <div v-if="showPreview === false" class="border-t">
        <textarea
          v-model="content"
          @input="updateContent"
          @keydown="handleKeydown"
          class="w-full h-96 p-4 font-mono text-sm resize-none focus:outline-none"
          placeholder="Write your markdown here..."
        ></textarea>
      </div>
    </div>

    <!-- Character Count -->
    <div class="mt-2 text-sm text-gray-500">
      {{ content.length }} characters
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'
import { useMedia } from '@/composables/useApi'
import { useNotification } from '@kyvg/vue3-notification'

interface Props {
  modelValue: string
  placeholder?: string
  height?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Write your markdown here...',
  height: '24rem'
})

const emit = defineEmits<Emits>()

const content = ref(props.modelValue)
const showPreview = ref<boolean | null>(null) // null for split view
const textareaRef = ref<HTMLTextAreaElement>()

// Configure marked options
marked.setOptions({
  breaks: true,
  gfm: true
})

const previewContent = computed(() => {
  if (!content.value) return ''
  try {
    return marked(content.value)
  } catch (error) {
    console.error('Markdown parsing error:', error)
    return content.value
  }
})

const updateContent = () => {
  emit('update:modelValue', content.value)
}

const insertMarkdown = (before: string, after: string) => {
  const textarea = textareaRef.value
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = content.value.substring(start, end)
  
  const newText = before + selectedText + after
  content.value = content.value.substring(0, start) + newText + content.value.substring(end)
  
  nextTick(() => {
    textarea.selectionStart = start + before.length
    textarea.selectionEnd = start + before.length + selectedText.length
    textarea.focus()
  })
  
  updateContent()
}

const handleKeydown = (event: KeyboardEvent) => {
  // Handle tab key for indentation
  if (event.key === 'Tab') {
    event.preventDefault()
    insertMarkdown('  ', '')
  }
  
  // Handle cmd+b for bold
  if (event.metaKey && event.key === 'b') {
    event.preventDefault()
    insertMarkdown('**', '**')
  }
  
  // Handle cmd+i for italic
  if (event.metaKey && event.key === 'i') {
    event.preventDefault()
    insertMarkdown('*', '*')
  }
}

const togglePreview = () => {
  if (showPreview.value === null) {
    showPreview.value = true
  } else if (showPreview.value) {
    showPreview.value = false
  } else {
    showPreview.value = null
  }
}

// Watch for external changes
const { uploadMedia } = useMedia()
const { notify } = useNotification()

const handleDrop = async (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (!files || files.length === 0) return
  
  const file = files[0]
  if (!file || !file.type.startsWith('image/')) {
    notify({
      title: 'Error',
      text: 'Please drop an image file',
      type: 'error'
    })
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await uploadMedia(formData)
    if (response && response.file) {
      const markdown = `![${response.file.name}](${response.file.url})`
      const textarea = textareaRef.value
      if (textarea) {
        const start = textarea.selectionStart
        content.value = content.value.substring(0, start) + markdown + content.value.substring(start)
        nextTick(() => {
          textarea.selectionStart = textarea.selectionEnd = start + markdown.length
          textarea.focus()
        })
      }
      notify({
        title: 'Success',
        text: 'Image uploaded successfully',
        type: 'success'
      })
    }
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to upload image',
      type: 'error'
    })
  }
}

watch(() => props.modelValue, (newValue) => {
  if (newValue !== content.value) {
    content.value = newValue
  }
})
</script>

<style scoped>
.markdown-editor {
  @apply w-full;
}

.prose {
  @apply text-gray-700;
}

.prose h1 {
  @apply text-2xl font-bold text-gray-900 mb-4;
}

.prose h2 {
  @apply text-xl font-semibold text-gray-900 mb-3;
}

.prose h3 {
  @apply text-lg font-medium text-gray-900 mb-2;
}

.prose p {
  @apply mb-4;
}

.prose ul, .prose ol {
  @apply mb-4 pl-6;
}

.prose li {
  @apply mb-1;
}

.prose blockquote {
  @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-4;
}

.prose code {
  @apply bg-gray-100 px-1 py-0.5 rounded text-sm font-mono;
}

.prose pre {
  @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4;
}

.prose pre code {
  @apply bg-transparent p-0;
}

.prose img {
  @apply max-w-full h-auto rounded-lg shadow-sm;
}

.prose a {
  @apply text-blue-600 hover:text-blue-800 underline;
}

.prose hr {
  @apply border-gray-300 my-6;
}

.prose table {
  @apply w-full border-collapse mb-4;
}

.prose th, .prose td {
  @apply border border-gray-300 px-3 py-2;
}

.prose th {
  @apply bg-gray-50 font-medium;
}
</style>
