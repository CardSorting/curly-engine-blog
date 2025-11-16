<template>
  <AdminLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h1 class="text-2xl font-semibold text-gray-900">Topics</h1>
          <p class="mt-2 text-sm text-gray-700">Manage blog topics and categories</p>
        </div>
        <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <Button @click="openCreateModal" class="flex items-center gap-2">
            <PlusIcon class="h-4 w-4" />
            Add Topic
          </Button>
        </div>
      </div>

      <div v-if="loading" class="mt-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>

      <div v-else-if="topics.length === 0" class="mt-8 text-center">
        <TagIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No topics</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new topic.</p>
        <div class="mt-6">
          <Button @click="openCreateModal" class="flex items-center gap-2">
            <PlusIcon class="h-4 w-4" />
            Add Topic
          </Button>
        </div>
      </div>

      <div v-else class="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="topic in topics"
          :key="topic.id"
          class="relative rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <div
                  class="h-3 w-3 rounded-full"
                  :style="{ backgroundColor: topic.color || '#3B82F6' }"
                ></div>
                <h3 class="text-lg font-medium text-gray-900">{{ topic.name }}</h3>
              </div>
              <p class="mt-1 text-sm text-gray-500">/{{ topic.slug }}</p>
              <p v-if="topic.description" class="mt-2 text-sm text-gray-600">{{ topic.description }}</p>
            </div>
            <div class="flex gap-1">
              <Button
                @click="openEditModal(topic)"
                variant="ghost"
                size="sm"
                class="p-1"
              >
                <PencilIcon class="h-4 w-4" />
              </Button>
              <Button
                @click="openDeleteModal(topic)"
                variant="ghost"
                size="sm"
                class="p-1 text-red-600 hover:text-red-700"
              >
                <TrashIcon class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <Modal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      title="Create Topic"
    >
      <form @submit.prevent="handleCreate" class="space-y-4">
        <Input
          v-model="form.name"
          label="Name"
          placeholder="Enter topic name"
          required
          @input="generateSlug"
        />
        <Input
          v-model="form.slug"
          label="URL Slug"
          placeholder="topic-url-slug"
          required
        />
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Optional description"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
          <input
            v-model="form.color"
            type="color"
            class="h-10 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div class="flex justify-end gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            @click="showCreateModal = false"
          >
            Cancel
          </Button>
          <Button type="submit">
            Create Topic
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Edit Modal -->
    <Modal
      v-if="showEditModal"
      @close="showEditModal = false"
      title="Edit Topic"
    >
      <form @submit.prevent="handleUpdate" class="space-y-4">
        <Input
          v-model="form.name"
          label="Name"
          placeholder="Enter topic name"
          required
          @input="generateSlug"
        />
        <Input
          v-model="form.slug"
          label="URL Slug"
          placeholder="topic-url-slug"
          required
        />
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="Optional description"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Color</label>
          <input
            v-model="form.color"
            type="color"
            class="h-10 w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
        <div class="flex justify-end gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            @click="showEditModal = false"
          >
            Cancel
          </Button>
          <Button type="submit">
            Update Topic
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Delete Modal -->
    <Modal
      v-if="showDeleteModal"
      @close="showDeleteModal = false"
      title="Delete Topic"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          Are you sure you want to delete the topic "<strong>{{ selectedTopic?.name }}</strong>"?
          This action cannot be undone.
        </p>
        <div class="flex justify-end gap-2 pt-4">
          <Button
            type="button"
            variant="outline"
            @click="showDeleteModal = false"
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="danger"
            @click="handleDelete"
          >
            Delete Topic
          </Button>
        </div>
      </div>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
import { TagIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { ref, onMounted } from 'vue'
import { useTopics } from '@/composables/useApi'
import { type Topic } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import { useNotification } from '@kyvg/vue3-notification'

const { fetchTopics, createTopic, updateTopic, deleteTopic } = useTopics()
const { notify } = useNotification()

const topics = ref<Topic[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedTopic = ref<Topic | null>(null)

const form = ref({
  name: '',
  slug: '',
  description: '',
  color: '#3B82F6'
})

onMounted(async () => {
  await loadTopics()
})

const loadTopics = async () => {
  try {
    const response = await fetchTopics()
    // Fix: Ensure we always assign an array of topics
    topics.value = response?.results || []
  } catch (error) {
    console.error('Failed to load topics:', error)
  } finally {
    loading.value = false
  }
}

const generateSlug = () => {
  form.value.slug = form.value.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

const openCreateModal = () => {
  form.value = {
    name: '',
    slug: '',
    description: '',
    color: '#3B82F6'
  }
  showCreateModal.value = true
}

const openEditModal = (topic: Topic) => {
  selectedTopic.value = topic
  form.value = {
    name: topic.name,
    slug: topic.slug,
    description: topic.description || '',
    color: topic.color || '#3B82F6'
  }
  showEditModal.value = true
}

const openDeleteModal = (topic: Topic) => {
  selectedTopic.value = topic
  showDeleteModal.value = true
}

const handleCreate = async () => {
  try {
    const response = await createTopic(form.value)
    if (response) {
      notify({
        title: 'Success',
        text: 'Topic created successfully!',
        type: 'success'
      })
      showCreateModal.value = false
      await loadTopics()
    }
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to create topic',
      type: 'error'
    })
  }
}

const handleUpdate = async () => {
  if (!selectedTopic.value) return
  
  try {
    const response = await updateTopic(selectedTopic.value.slug, form.value)
    if (response) {
      notify({
        title: 'Success',
        text: 'Topic updated successfully!',
        type: 'success'
      })
      showEditModal.value = false
      await loadTopics()
    }
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to update topic',
      type: 'error'
    })
  }
}

const handleDelete = async () => {
  if (!selectedTopic.value) return
  
  try {
    await deleteTopic(selectedTopic.value.slug)
    notify({
      title: 'Success',
      text: 'Topic deleted successfully!',
      type: 'success'
    })
    showDeleteModal.value = false
    await loadTopics()
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to delete topic',
      type: 'error'
    })
  }
}
</script>
