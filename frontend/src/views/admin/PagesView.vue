<template>
  <AdminLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h1 class="text-2xl font-semibold text-gray-900">Pages</h1>
          <p class="mt-2 text-sm text-gray-700">Manage static pages like About, Contact, etc.</p>
        </div>
        <div class="mt-4 sm:ml-16 sm:mt-0 sm:flex-none">
          <Button @click="openCreateModal" class="flex items-center gap-2">
            <PlusIcon class="h-4 w-4" />
            Add Page
          </Button>
        </div>
      </div>

      <div v-if="loading" class="mt-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
      </div>

      <div v-else-if="pages.length === 0" class="mt-8 text-center">
        <NewspaperIcon class="mx-auto h-12 w-12 text-gray-400" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">No pages</h3>
        <p class="mt-1 text-sm text-gray-500">Get started by creating a new page.</p>
        <div class="mt-6">
          <Button @click="openCreateModal" class="flex items-center gap-2">
            <PlusIcon class="h-4 w-4" />
            Add Page
          </Button>
        </div>
      </div>

      <div v-else class="mt-8">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">
                  Title
                </th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  URL
                </th>
                <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="page in pages" :key="page.id">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                  {{ page.title }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  /{{ page.slug }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  <span
                    :class="[
                      'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                      page.is_published
                        ? 'bg-green-100 text-green-800'
                        : 'bg-yellow-100 text-yellow-800'
                    ]"
                  >
                    {{ page.is_published ? 'Published' : 'Draft' }}
                  </span>
                </td>
                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                  <Button
                    @click="openEditModal(page)"
                    variant="ghost"
                    size="sm"
                    class="p-1 mr-2"
                  >
                    <PencilIcon class="h-4 w-4" />
                  </Button>
                  <Button
                    @click="openDeleteModal(page)"
                    variant="ghost"
                    size="sm"
                    class="p-1 text-red-600 hover:text-red-700"
                  >
                    <TrashIcon class="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <Modal
      v-if="showCreateModal"
      @close="showCreateModal = false"
      title="Create Page"
      size="lg"
    >
      <form @submit.prevent="handleCreate" class="space-y-4">
        <Input
          v-model="form.title"
          label="Title"
          placeholder="Enter page title"
          required
          @input="generateSlug"
        />
        <Input
          v-model="form.slug"
          label="URL Slug"
          placeholder="page-url-slug"
          required
        />
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Content</label>
          <MarkdownEditor
            v-model="form.content"
            placeholder="Write your page content in markdown..."
          />
        </div>
        <Input
          v-model="form.meta_description"
          label="Meta Description"
          placeholder="SEO meta description"
        />
        <div class="flex items-center">
          <input
            v-model="form.is_published"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label class="ml-2 block text-sm text-gray-700">Publish immediately</label>
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
            Create Page
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Edit Modal -->
    <Modal
      v-if="showEditModal"
      @close="showEditModal = false"
      title="Edit Page"
      size="lg"
    >
      <form @submit.prevent="handleUpdate" class="space-y-4">
        <Input
          v-model="form.title"
          label="Title"
          placeholder="Enter page title"
          required
          @input="generateSlug"
        />
        <Input
          v-model="form.slug"
          label="URL Slug"
          placeholder="page-url-slug"
          required
        />
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Content</label>
          <MarkdownEditor
            v-model="form.content"
            placeholder="Write your page content in markdown..."
          />
        </div>
        <Input
          v-model="form.meta_description"
          label="Meta Description"
          placeholder="SEO meta description"
        />
        <div class="flex items-center">
          <input
            v-model="form.is_published"
            type="checkbox"
            class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <label class="ml-2 block text-sm text-gray-700">Publish immediately</label>
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
            Update Page
          </Button>
        </div>
      </form>
    </Modal>

    <!-- Delete Modal -->
    <Modal
      v-if="showDeleteModal"
      @close="showDeleteModal = false"
      title="Delete Page"
    >
      <div class="space-y-4">
        <p class="text-sm text-gray-600">
          Are you sure you want to delete the page "<strong>{{ selectedPage?.title }}</strong>"?
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
            Delete Page
          </Button>
        </div>
      </div>
    </Modal>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/layouts/AdminLayout.vue'
import { NewspaperIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { ref, onMounted } from 'vue'
import { usePages } from '@/composables/useApi'
import { type Page } from '@/types/api'
import Button from '@/components/ui/Button.vue'
import Input from '@/components/ui/Input.vue'
import Modal from '../../components/ui/Modal.vue'
import MarkdownEditor from '@/components/editor/MarkdownEditor.vue'
import { useNotification } from '@kyvg/vue3-notification'

const { fetchPages, createPage, updatePage, deletePage } = usePages()
const { notify } = useNotification()

const pages = ref<Page[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const selectedPage = ref<Page | null>(null)

const form = ref({
  title: '',
  slug: '',
  content: '',
  meta_description: '',
  is_published: false
})

onMounted(async () => {
  await loadPages()
})

const loadPages = async () => {
  try {
    const response = await fetchPages()
    // Fix: Ensure we always assign an array of pages
    pages.value = response?.results || []
  } catch (error) {
    console.error('Failed to load pages:', error)
  } finally {
    loading.value = false
  }
}

const generateSlug = () => {
  form.value.slug = form.value.title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '')
}

const openCreateModal = () => {
  form.value = {
    title: '',
    slug: '',
    content: '',
    meta_description: '',
    is_published: false
  }
  showCreateModal.value = true
}

const openEditModal = (page: Page) => {
  selectedPage.value = page
  form.value = {
    title: page.title,
    slug: page.slug,
    content: page.content || '',
    meta_description: page.meta_description || '',
    is_published: page.is_published || false
  }
  showEditModal.value = true
}

const openDeleteModal = (page: Page) => {
  selectedPage.value = page
  showDeleteModal.value = true
}

const handleCreate = async () => {
  try {
    const response = await createPage(form.value)
    if (response) {
      notify({
        title: 'Success',
        text: 'Page created successfully!',
        type: 'success'
      })
      showCreateModal.value = false
      await loadPages()
    }
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to create page',
      type: 'error'
    })
  }
}

const handleUpdate = async () => {
  if (!selectedPage.value) return
  
  try {
    const response = await updatePage(selectedPage.value.slug, form.value)
    if (response) {
      notify({
        title: 'Success',
        text: 'Page updated successfully!',
        type: 'success'
      })
      showEditModal.value = false
      await loadPages()
    }
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to update page',
      type: 'error'
    })
  }
}

const handleDelete = async () => {
  if (!selectedPage.value) return
  
  try {
    await deletePage(selectedPage.value.slug)
    notify({
      title: 'Success',
      text: 'Page deleted successfully!',
      type: 'success'
    })
    showDeleteModal.value = false
    await loadPages()
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to delete page',
      type: 'error'
    })
  }
}
</script>
