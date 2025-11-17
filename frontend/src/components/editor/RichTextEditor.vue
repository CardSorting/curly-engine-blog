<template>
  <div class="rich-text-editor">
    <!-- Editor Toolbar -->
    <div class="editor-toolbar flex flex-wrap items-center gap-1 p-3 border-b border-gray-200 bg-gray-50">
      <!-- History Controls -->
      <div class="flex items-center border-r border-gray-300 pr-2 mr-2">
        <button
          @click="editor.commands.undo()"
          :disabled="!editor.can().undo()"
          class="toolbar-btn"
          title="Undo"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M3 10a7 7 0 1014 0 7 7 0 00-14 0zm10.707-1.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
          </svg>
        </button>
        <button
          @click="editor.commands.redo()"
          :disabled="!editor.can().redo()"
          class="toolbar-btn"
          title="Redo"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M17 10a7 7 0 11-14 0 7 7 0 0114 0zm-4.707-1.707a1 1 0 00-1.414 1.414L11.414 10 10 8.586a1 1 0 00-1.414-1.414l2 2a1 1 0 001.414 0l2-2z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>

      <!-- Formatting Controls -->
      <div class="flex items-center border-r border-gray-300 pr-2 mr-2">
        <button
          @click="editor.commands.toggleHeading({ level: 1 })"
          :class="{ 'active': editor.isActive('heading', { level: 1 }) }"
          class="toolbar-btn"
          title="Heading 1"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4v3h4v10h3V7h4V4H3z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.toggleHeading({ level: 2 })"
          :class="{ 'active': editor.isActive('heading', { level: 2 }) }"
          class="toolbar-btn"
          title="Heading 2"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 6v2h6v8h2V8h6V6H3z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.toggleBold()"
          :class="{ 'active': editor.isActive('bold') }"
          class="toolbar-btn"
          title="Bold"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M6 4v12h4.5c1.5 0 2.5-1 2.5-2.5S12 11 10.5 11H8V4H6zm2 5h2c.5 0 1 .5 1 1s-.5 1-1 1H8V9z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.toggleItalic()"
          :class="{ 'active': editor.isActive('italic') }"
          class="toolbar-btn"
          title="Italic"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M8 4h4l-2 8H6l2-8zm-1 10h4l-1 2H6l1-2z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.toggleUnderline()"
          :class="{ 'active': editor.isActive('underline') }"
          class="toolbar-btn"
          title="Underline"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5 3v6a3 3 0 006 0V3H8v6a1 1 0 01-2 0V3H5zm4 13a1 1 0 01-1 1H4a1 1 0 110-2h3a1 1 0 011-1h2a1 1 0 011-1h3a1 1 0 110 2h-3a1 1 0 01-1 1H9z"/>
          </svg>
        </button>
      </div>

      <!-- Lists and Alignment -->
      <div class="flex items-center border-r border-gray-300 pr-2 mr-2">
        <button
          @click="editor.commands.toggleBulletList()"
          :class="{ 'active': editor.isActive('bulletList') }"
          class="toolbar-btn"
          title="Bullet List"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 6h14v2H3V6zm0 4h14v2H3v-2zm0 4h14v2H3v-2z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.toggleOrderedList()"
          :class="{ 'active': editor.isActive('orderedList') }"
          class="toolbar-btn"
          title="Numbered List"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 6h14v2H3V6zm0 4h14v2H3v-2zm0 4h14v2H3v-2z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.setTextAlign('left')"
          :class="{ 'active': editor.isActive({ textAlign: 'left' }) }"
          class="toolbar-btn"
          title="Align Left"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 4h14v2H3V4zm0 4h10v2H3V8zm0 4h14v2H3v-2zm0 4h10v2H3v-2z"/>
          </svg>
        </button>
        <button
          @click="editor.commands.setTextAlign('center')"
          :class="{ 'active': editor.isActive({ textAlign: 'center' }) }"
          class="toolbar-btn"
          title="Align Center"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M5 4h10v2H5V4zm-1 4h12v2H4V8zm-1 4h14v2H3v-2zm1 4h12v2H4v-2z"/>
          </svg>
        </button>
      </div>

      <!-- Links and Media -->
      <div class="flex items-center border-r border-gray-300 pr-2 mr-2">
        <button
          @click="showLinkDialog = true"
          :class="{ 'active': editor.isActive('link') }"
          class="toolbar-btn"
          title="Insert Link"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clip-rule="evenodd"/>
          </svg>
        </button>
        <button
          @click="triggerImageInput"
          class="toolbar-btn"
          title="Insert Image"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"/>
          </svg>
        </button>
        <input
          ref="imageInput"
          type="file"
          accept="image/*"
          multiple
          class="hidden"
          @change="handleImageUpload"
        />
      </div>

      <!-- Tables -->
      <div class="flex items-center">
        <button
          @click="insertTable()"
          class="toolbar-btn"
          title="Insert Table"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M5 4a3 3 0 00-3 3v6a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H5zm-1 9v-1h5v2H5a1 1 0 01-1-1zm7 1v-2h3a1 1 0 010 2h-3zm0-3V9h3v2h-3zm-7-3V9h5v2H5a1 1 0 010-2zm0 4V9h5v2H5zm0-6V7h5v2H5a1 1 0 011-1z" clip-rule="evenodd"/>
          </svg>
        </button>
      </div>

      <!-- Content Analysis Tools -->
      <div class="flex items-center border-r border-gray-300 pr-2 mr-2">
        <button
          @click="showAnalysisPanel = !showAnalysisPanel"
          :class="{ 'bg-blue-100 text-blue-600': showAnalysisPanel }"
          class="toolbar-btn"
          title="Content Analysis"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </button>
        <button
          @click="analyzeContent('grammar')"
          :disabled="isAnalyzing"
          class="toolbar-btn"
          title="Check Grammar"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20" v-if="!isAnalyzing">
            <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
          </svg>
          <div class="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" v-else></div>
        </button>
        <button
          @click="analyzeContent('comprehensive')"
          :disabled="isAnalyzing"
          class="toolbar-btn"
          title="Full Analysis"
        >
          📊
        </button>
      </div>

      <!-- Character Count and Stats -->
      <div class="ml-auto text-sm text-gray-500 flex items-center space-x-4">
        <span v-if="readabilityScore > 0" :class="getReadabilityColorClass(readabilityScore)">
          {{ readabilityLevel }}
        </span>
        <span>{{ wordCount }} words</span>
        <span>{{ characterCount }}/{{ wordLimit ? wordLimit : '∞' }} chars</span>
      </div>
    </div>

    <!-- Editor Content Area -->
    <div
      class="editor-content border min-h-[300px] max-h-[600px] overflow-y-auto p-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      :class="{ 'prose prose-sm max-w-none': !editable }"
    >
      <EditorContent
        :editor="editor"
        class="focus:outline-none"
      />
    </div>

    <!-- Link Dialog -->
    <div v-if="showLinkDialog" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 w-96">
        <h3 class="text-lg font-semibold mb-4">Insert Link</h3>
        <input
          v-model="linkUrl"
          type="url"
          placeholder="https://example.com"
          class="w-full p-2 border border-gray-300 rounded mb-4"
          ref="linkInput"
        />
        <div class="flex justify-end space-x-2">
          <button
            @click="showLinkDialog = false"
            class="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="insertLink"
            class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Insert
          </button>
        </div>
      </div>
    </div>

    <!-- Image Drop Zone Indicator -->
    <div
      v-if="isDragOver"
      class="absolute inset-0 border-2 border-dashed border-blue-400 bg-blue-50 bg-opacity-80 flex items-center justify-center z-10"
    >
      <div class="text-center">
        <svg class="w-12 h-12 text-blue-500 mx-auto mb-2" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clip-rule="evenodd"/>
        </svg>
        <p class="text-blue-600 font-medium">Drop image here to insert</p>
      </div>
    </div>

    <!-- Auto-save indicator -->
    <div v-if="autoSaveEnabled && editor && editor.getText().length > 0" class="text-xs text-gray-400 mt-2">
      Auto-saved {{ lastSaved ? formatDate(lastSaved) : 'just now' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import CharacterCount from '@tiptap/extension-character-count'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableHeader from '@tiptap/extension-table-header'
import TableCell from '@tiptap/extension-table-cell'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import TextStyle from '@tiptap/extension-text-style'
import { useDebounceFn } from '@vueuse/core'
import { useMedia } from '@/composables/useApi'
import { useContentAnalysis } from '@/composables/useContentAnalysis'
import { useNotification } from '@kyvg/vue3-notification'

interface Props {
  modelValue: string
  placeholder?: string
  wordLimit?: number | undefined
  autoSave?: boolean
  editable?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'autoSave', content: string): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Start writing...',
  wordLimit: undefined,
  autoSave: true,
  editable: true
})

const emit = defineEmits<Emits>()

// Reactive state
const editor = ref()
const characterCount = ref(0)
const lastSaved = ref<Date | null>(null)
const isDragOver = ref(false)
const showLinkDialog = ref(false)
const linkUrl = ref('')
const imageInput = ref<HTMLInputElement>()
const linkInput = ref<HTMLInputElement>()

const autoSaveEnabled = computed(() => props.autoSave)
const { uploadMedia } = useMedia()
const {
  analyzeText,
  realTimeCheck,
  analysisResults,
  isAnalyzing,
  writingSuggestions,
  readabilityRating,
  issueCountBySeverity
} = useContentAnalysis()
const { notify } = useNotification()

// Content analysis state
const showAnalysisPanel = ref(false)
const wordCount = ref(0)
const readabilityScore = computed(() => readabilityRating.value.score || 0)
const readabilityLevel = computed(() => readabilityRating.value.level || 'Unknown')

// Content analysis functions
const analyzeContent = async (type: 'grammar' | 'readability' | 'seo' | 'comprehensive') => {
  if (!editor.value) return

  const text = editor.value.getText()
  if (!text.trim()) {
    notify({
      title: 'No content',
      text: 'Please enter some content to analyze',
      type: 'warning'
    })
    return
  }

  await analyzeText(text, type)
  wordCount.value = text.split(/\s+/).filter((word: string) => word.length > 0).length
}

const getReadabilityColorClass = (score: number): string => {
  if (score >= 80) return 'text-green-600'
  else if (score >= 60) return 'text-yellow-600'
  else if (score >= 30) return 'text-orange-600'
  else return 'text-red-600'
}

// Create editor instance
const createEditor = () => {
  editor.value = new Editor({
    content: props.modelValue,
    editable: props.editable,
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: props.placeholder
      }),
      CharacterCount,
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-blue-600 hover:text-blue-800 underline cursor-pointer'
        }
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full h-auto rounded-lg shadow-sm'
        }
      }),
      Table.configure({}),
      TableRow,
      TableHeader.configure({
        HTMLAttributes: {
          class: 'bg-gray-50 font-medium'
        }
      }),
      TableCell,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
        defaultAlignment: 'left'
      }),
      Underline,
      TextStyle
    ],
    onUpdate: ({ editor: updatedEditor }: any) => {
      const html = updatedEditor.getHTML()
      characterCount.value = updatedEditor.storage.characterCount.characters()
      emit('update:modelValue', html)

      // Auto-save
      if (autoSaveEnabled.value) {
        debouncedAutoSave(html)
      }
    },
    onCreate: ({ editor: createdEditor }: any) => {
      characterCount.value = createdEditor.storage.characterCount.characters()
    }
  })
}

// Debounced auto-save
const debouncedAutoSave = useDebounceFn((content: string) => {
  emit('autoSave', content)
  lastSaved.value = new Date()
}, 2000)

// Insert table
const insertTable = () => {
  editor.value.commands.insertTable({
    rows: 3,
    cols: 3,
    withHeaderRow: true
  })
}

// Link dialog functions
const insertLink = () => {
  if (linkUrl.value) {
    editor.value.commands.setLink({ href: linkUrl.value })
    showLinkDialog.value = false
    linkUrl.value = ''
  }
}

// Image functions
const triggerImageInput = () => {
  imageInput.value?.click()
}

const handleImageUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (!files) return

  for (const file of Array.from(files)) {
    if (file.type.startsWith('image/')) {
      try {
        const formData = new FormData()
        formData.append('file', file)

        const response = await uploadMedia(formData)
        if (response && response.file) {
          // Insert image into editor
          editor.value.commands.setImage({
            src: response.file.file,
            alt: response.file.file_name || 'Uploaded image'
          })

          notify({
            title: 'Success',
            text: 'Image uploaded and inserted',
            type: 'success'
          })
        }
      } catch (error) {
        notify({
          title: 'Upload Failed',
          text: 'Failed to upload image',
          type: 'error'
        })
      }
    }
  }

  // Clear input
  if (target) target.value = ''
}

// Drag and drop for images
const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.types.includes('Files')) {
    isDragOver.value = true
  }
}

const handleDragLeave = () => {
  isDragOver.value = false
}

const handleDrop = async (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false

  const files = event.dataTransfer?.files
  if (!files) return

  for (const file of Array.from(files)) {
    if (file.type.startsWith('image/')) {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await uploadMedia(formData)
        if (response && response.file) {
          editor.value.commands.setImage({
            src: response.file.file,
            alt: response.file.file_name || 'Uploaded image'
          })

          notify({
            title: 'Success',
            text: 'Image uploaded and inserted',
            type: 'success'
          })
        }
      } catch (error) {
        notify({
          title: 'Upload Failed',
          text: 'Failed to upload image',
          type: 'error'
        })
      }
    }
  }
}

// Format date helper
const formatDate = (date: Date) => {
  return date.toLocaleTimeString()
}

// Watch for external content changes
watch(() => props.modelValue, (newContent) => {
  if (editor.value && newContent !== editor.value.getHTML()) {
    editor.value.commands.setContent(newContent)
  }
})

// Lifecycle
onMounted(() => {
  createEditor()
})

onUnmounted(() => {
  if (editor.value) {
    editor.value.destroy()
  }
})
</script>

<style scoped>
.toolbar-btn {
  @apply p-2 mx-1 rounded text-gray-600 hover:text-gray-900 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed;
}

.toolbar-btn.active {
  @apply bg-blue-100 text-blue-600;
}

.editor-content {
  @apply prose prose-sm max-w-none;
}

.editor-content :deep(.ProseMirror) {
  @apply outline-none min-h-[300px];
}

.editor-content :deep(.ProseMirror h1) {
  @apply text-2xl font-bold mb-4 mt-6;
}

.editor-content :deep(.ProseMirror h2) {
  @apply text-xl font-semibold mb-3 mt-5;
}

.editor-content :deep(.ProseMirror h3) {
  @apply text-lg font-medium mb-2 mt-4;
}

.editor-content :deep(.ProseMirror p) {
  @apply mb-4 leading-relaxed;
}

.editor-content :deep(.ProseMirror ul, .ProseMirror ol) {
  @apply mb-4 pl-6;
}

.editor-content :deep(.ProseMirror li) {
  @apply mb-1;
}

.editor-content :deep(.ProseMirror blockquote) {
  @apply border-l-4 border-gray-300 pl-4 italic text-gray-600 my-4 bg-gray-50 py-2;
}

.editor-content :deep(.ProseMirror code) {
  @apply bg-gray-100 px-2 py-1 rounded text-sm font-mono;
}

.editor-content :deep(.ProseMirror pre) {
  @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-4;
}

.editor-content :deep(.ProseMirror pre code) {
  @apply bg-transparent p-0 text-gray-100;
}

.editor-content :deep(.ProseMirror table) {
  @apply w-full border-collapse my-4 border border-gray-300;
}

.editor-content :deep(.ProseMirror th, .ProseMirror td) {
  @apply border border-gray-300 px-3 py-2;
}

.editor-content :deep(.ProseMirror th) {
  @apply bg-gray-50 font-medium;
}

.editor-content :deep(.ProseMirror hr) {
  @apply border-gray-300 my-8;
}

.editor-content :deep(.ProseMirror img) {
  @apply max-w-full h-auto rounded-lg shadow-sm my-4 cursor-pointer;
}

.editor-content :deep(.ProseMirror a) {
  @apply text-blue-600 hover:text-blue-800 underline cursor-pointer;
}

/* Table resizing styles */
.editor-content :deep(.ProseMirror table .selectedCell) {
  @apply bg-blue-50;
}

/* Drag and drop cursor */
.editor-content.dragover {
  cursor: copy;
}

/* Toolbar responsive */
@media (max-width: 768px) {
  .editor-toolbar {
    flex-wrap: wrap;
  }
}
</style>
