<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="py-6">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900">Media Library</h1>
              <p class="mt-1 text-sm text-gray-500">Upload and manage your media files</p>
            </div>
            <div class="flex items-center space-x-3">
              <Button @click="openUploadModal" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700">
                <CloudArrowUpIcon class="w-5 h-5 mr-2" />
                Upload Files
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Filters -->
      <div class="bg-white shadow rounded-lg mb-6">
        <div class="px-4 py-5 sm:p-6">
          <div class="flex flex-wrap gap-4 items-center">
            <!-- File Type Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">File Type</label>
              <select
                v-model="typeFilter"
                @change="loadMedia"
                class="block w-full pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
              >
                <option value="">All Types</option>
                <option value="image">Images</option>
                <option value="video">Videos</option>
                <option value="document">Documents</option>
              </select>
            </div>

            <!-- Search -->
            <div class="flex-1 min-w-64">
              <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                v-model="searchQuery"
                @input="debouncedSearch"
                type="text"
                placeholder="Search files..."
                class="block w-full px-3 py-2 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              />
            </div>

            <div class="flex items-end">
              <Button @click="refreshMedia" variant="outline" size="sm">
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading media files...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600">{{ error }}</p>
        <Button @click="loadMedia" class="mt-4">
          Try Again
        </Button>
      </div>

      <!-- Media Grid -->
      <div v-else-if="mediaFiles.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div
          v-for="file in mediaFiles"
          :key="file.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
        >
          <!-- Image Thumbnail -->
          <div v-if="isImage(file.file)" class="aspect-square bg-gray-100 relative group">
            <img
              :src="file.file"
              :alt="file.alt_text || file.file_name"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100">
              <div class="flex space-x-2">
                <Button
                  @click="copyUrl(file)"
                  variant="secondary"
                  size="sm"
                  class="bg-white/20 hover:bg-white/30 text-white border-0"
                >
                  <ClipboardIcon class="w-4 h-4" />
                </Button>
                <Button
                  @click="deleteFile(file)"
                  variant="danger"
                  size="sm"
                  class="bg-red-600/20 hover:bg-red-600/30 text-red-300 border-0"
                >
                  <TrashIcon class="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          <!-- File Icon for Non-Images -->
          <div v-else class="aspect-square bg-gray-100 flex items-center justify-center">
            <DocumentIcon class="w-12 h-12 text-gray-400" />
          </div>

          <!-- File Info -->
          <div class="p-3">
            <p class="text-sm font-medium text-gray-900 truncate" :title="file.file_name">
              {{ file.file_name }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              {{ formatFileSize(file.file_size) }} • {{ formatDate(file.uploaded_at) }}
            </p>
            <Button
              @click="copyUrl(file)"
              variant="outline"
              size="sm"
              class="w-full mt-2 text-xs"
            >
              Copy URL
            </Button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 bg-white rounded-lg shadow">
        <PhotoIcon class="mx-auto h-16 w-16 text-gray-300" />
        <h3 class="mt-2 text-lg font-medium text-gray-900">No media files</h3>
        <p class="mt-1 text-gray-600">Upload your first media files to get started.</p>
        <div class="mt-6">
          <Button @click="openUploadModal">
            Upload Files
          </Button>
        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeUploadModal">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Upload Media Files</h3>

          <div class="space-y-4">
            <!-- Drag & Drop Area -->
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
              @dragover.prevent
              @drop="handleDrop"
            >
              <CloudArrowUpIcon class="mx-auto h-12 w-12 text-gray-400" />
              <p class="mt-2 text-sm text-gray-600">
                Drag & drop files here, or
                <label class="text-blue-600 hover:text-blue-500 cursor-pointer">
                  browse files
                  <input
                    ref="fileInput"
                    type="file"
                    multiple
                    accept="image/*,video/*,audio/*,.pdf,.doc,.docx"
                    class="hidden"
                    @change="handleFileSelect"
                  />
                </label>
              </p>
              <p class="mt-1 text-xs text-gray-500">Images, videos, documents up to 10MB each</p>
            </div>

            <!-- Upload Progress -->
            <div v-if="uploadProgress > 0" class="space-y-2">
              <div class="flex justify-between text-sm">
                <span>Uploading...</span>
                <span>{{ uploadProgress }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div
                  class="bg-blue-600 h-2 rounded-full transition-all"
                  :style="{ width: uploadProgress + '%' }"
                ></div>
              </div>
            </div>

            <!-- Selected Files -->
            <div v-if="selectedFiles.length" class="space-y-2">
              <h4 class="text-sm font-medium">Selected Files:</h4>
              <div class="max-h-32 overflow-y-auto space-y-1">
                <div v-for="(file, index) in selectedFiles" :key="index" class="flex items-center justify-between text-sm bg-gray-50 p-2 rounded">
                  <span class="truncate">{{ file.name }}</span>
                  <span class="text-gray-500 ml-2">{{ formatFileSize(file.size) }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex space-x-3 mt-6">
            <Button @click="uploadFiles" :disabled="!selectedFiles.length || uploading" :loading="uploading">
              Upload
            </Button>
            <Button @click="closeUploadModal" variant="outline">
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  CloudArrowUpIcon,
  PhotoIcon,
  DocumentIcon,
  ClipboardIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import { useMedia } from '@/composables/useApi'
import { type Media } from '@/types/api'
import Button from '@/components/ui/Button.vue'

const { fetchMedia, uploadMedia, deleteMedia } = useMedia()

const mediaFiles = ref<Media[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const typeFilter = ref('')
const searchQuery = ref('')
let searchTimeout: number | null = null

const showUploadModal = ref(false)
const selectedFiles = ref<File[]>([])
const uploadProgress = ref(0)
const uploading = ref(false)

const fileInput = ref<HTMLInputElement>()

onMounted(async () => {
  await loadMedia()
})

const loadMedia = async () => {
  loading.value = true
  error.value = null

  try {
    const params: any = {}
    if (typeFilter.value) params.type = typeFilter.value
    if (searchQuery.value) params.search = searchQuery.value

    const response = await fetchMedia(params)
    if (response && response.results) {
      mediaFiles.value = response.results
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load media'
  } finally {
    loading.value = false
  }
}

const openUploadModal = () => {
  showUploadModal.value = true
  selectedFiles.value = []
  uploadProgress.value = 0
}

const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  uploadProgress.value = 0
}

const handleDrop = (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (files) {
    handleFiles(Array.from(files))
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

const handleFiles = (files: File[]) => {
  // Filter out files larger than 10MB
  const validFiles = files.filter(file => file.size <= 10 * 1024 * 1024)
  selectedFiles.value.push(...validFiles)
}

const uploadFiles = async () => {
  if (!selectedFiles.value.length) return

  uploading.value = true
  uploadProgress.value = 0

  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name)

      await uploadMedia(formData)
      uploadProgress.value += 100 / selectedFiles.value.length
    }

    await loadMedia()
    closeUploadModal()
  } catch (err: any) {
    error.value = err.message || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

const copyUrl = async (file: Media) => {
  try {
    await navigator.clipboard.writeText(file.file)
    // Could show success notification here
  } catch (err) {
    console.error('Failed to copy URL:', err)
  }
}

const deleteFile = async (file: Media) => {
  if (!confirm('Are you sure you want to delete this file?')) return

  try {
    await deleteMedia(file.id)
    mediaFiles.value = mediaFiles.value.filter(f => f.id !== file.id)
  } catch (err: any) {
    console.error('Failed to delete file:', err)
  }
}

const debouncedSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    loadMedia()
  }, 300)
}

const refreshMedia = () => {
  loadMedia()
}

const isImage = (url: string): boolean => {
  return /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(url)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (dateString: string | null): string => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}
</script>
