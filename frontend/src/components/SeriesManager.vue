<template>
  <div class="series-manager">
    <!-- Series List -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Content Series</h3>
        <button
          @click="showCreateModal = true"
          class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm"
        >
          Create Series
        </button>
      </div>

      <div v-if="series.length === 0 && !isLoading" class="text-center py-8">
        <p class="text-gray-500 mb-4">No series created yet</p>
        <button
          @click="showCreateModal = true"
          class="bg-gray-200 text-gray-700 px-4 py-2 rounded hover:bg-gray-300"
        >
          Create your first series
        </button>
      </div>

      <div v-else-if="isLoading" class="flex justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="item in series"
          :key="item.id"
          class="border rounded-lg p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between mb-2">
            <h4 class="font-medium text-gray-900">{{ item.title }}</h4>
            <button
              @click="showActionsMenu(item.id)"
              class="text-gray-400 hover:text-gray-600"
            >
              ⋮
            </button>
          </div>

          <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ item.description }}</p>

          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>{{ item.article_count }} articles</span>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>

          <!-- Actions Menu -->
          <div
            v-if="activeMenuId === item.id"
            class="absolute bg-white border rounded shadow-lg p-2 mt-1 z-10"
          >
            <button
              @click="editSeries(item)"
              class="block w-full text-left px-3 py-1 hover:bg-gray-100 rounded text-sm"
            >
              Edit
            </button>
            <button
              @click="deleteSeries(item.id)"
              class="block w-full text-left px-3 py-1 hover:bg-red-100 rounded text-sm text-red-600"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Series Modal -->
    <div
      v-if="showCreateModal || editingSeries"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="closeModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4" @click.stop>
        <h3 class="text-lg font-semibold mb-4">
          {{ editingSeries ? 'Edit Series' : 'Create New Series' }}
        </h3>

        <form @submit.prevent="submitSeriesForm">
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                v-model="seriesForm.title"
                type="text"
                required
                class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter series title"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                v-model="seriesForm.description"
                rows="3"
                class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Describe your series"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Cover Image (optional)
              </label>
              <input
                v-model="seriesForm.cover_image"
                type="text"
                class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Media ID or URL"
              />
            </div>
          </div>

          <div class="flex justify-end space-x-2 mt-6">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isCreatingSeries"
              class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
            >
              <span v-if="isCreatingSeries">Creating...</span>
              <span v-else>{{ editingSeries ? 'Update' : 'Create' }} Series</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Click outside to close menus -->
    <div
      v-if="activeMenuId"
      class="fixed inset-0 z-5"
      @click="activeMenuId = null"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useSeries, type Series } from '@/composables/useSeries'
import { useNotification } from '@kyvg/vue3-notification'

interface Props {
  onSeriesSelected?: (series: Series) => void
}

const props = defineProps<Props>()

const {
  series,
  isLoading,
  isCreatingSeries,
  fetchSeries,
  createSeries,
  updateSeries,
  deleteSeries
} = useSeries()

const { notify } = useNotification()

// State
const showCreateModal = ref(false)
const editingSeries = ref<Series | null>(null)
const activeMenuId = ref<string | null>(null)

const seriesForm = reactive({
  title: '',
  description: '',
  cover_image: ''
})

// Methods
const showActionsMenu = (seriesId: string) => {
  activeMenuId.value = activeMenuId.value === seriesId ? null : seriesId
}

const closeModal = () => {
  showCreateModal.value = false
  editingSeries.value = null
  resetForm()
}

const resetForm = () => {
  seriesForm.title = ''
  seriesForm.description = ''
  seriesForm.cover_image = ''
}

const submitSeriesForm = async () => {
  if (!seriesForm.title.trim()) return

  try {
    const updateData: any = {
      title: seriesForm.title,
      description: seriesForm.description
    }

    if (seriesForm.cover_image) {
      updateData.cover_image = seriesForm.cover_image
    }

    if (editingSeries.value) {
      await updateSeries(editingSeries.value.id, updateData)
      notify({
        title: 'Series updated',
        text: 'Series has been updated successfully',
        type: 'success'
      })
    } else {
      const newSeries = await createSeries(updateData)

      if (props.onSeriesSelected && newSeries) {
        props.onSeriesSelected(newSeries)
      }
    }

    closeModal()
  } catch (error) {
    // Error handled in composable
  }
}

const editSeries = (series: Series) => {
  editingSeries.value = series
  seriesForm.title = series.title
  seriesForm.description = series.description || ''
  seriesForm.cover_image = series.cover_image?.id || ''
  activeMenuId.value = null
}

const handleDelete = async (seriesId: string) => {
  if (confirm('Are you sure you want to delete this series? This action cannot be undone.')) {
    await deleteSeries(seriesId)
    notify({
      title: 'Series deleted',
      text: 'Series has been deleted successfully',
      type: 'success'
    })
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  fetchSeries()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
