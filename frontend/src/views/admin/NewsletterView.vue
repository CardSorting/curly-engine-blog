<template>
  <AdminLayout>
    <div class="px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <h1 class="text-2xl font-semibold text-gray-900">Newsletter Management</h1>
          <p class="mt-2 text-sm text-gray-700">Create and manage your newsletter campaigns and subscribers.</p>
        </div>
        <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <Button @click="showCreateModal = true" variant="primary">
            <PlusIcon class="h-4 w-4 mr-2" />
            New Campaign
          </Button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="mt-8 grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <UsersIcon class="h-8 w-8 text-blue-500" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Total Subscribers</h3>
                <p class="text-2xl font-bold text-gray-900">{{ stats.totalSubscribers.toLocaleString() }}</p>
                <p class="text-sm text-green-600">+{{ stats.newSubscribers }} this month</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <PaperAirplaneIcon class="h-8 w-8 text-green-500" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Campaigns Sent</h3>
                <p class="text-2xl font-bold text-gray-900">{{ stats.campaignsSent }}</p>
                <p class="text-sm text-gray-500">Last 30 days</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <CursorArrowRaysIcon class="h-8 w-8 text-purple-500" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Open Rate</h3>
                <p class="text-2xl font-bold text-gray-900">{{ stats.openRate }}%</p>
                <p class="text-sm text-green-600">+{{ stats.openRateChange }}% vs avg</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white overflow-hidden shadow rounded-lg">
          <div class="p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <HandThumbUpIcon class="h-8 w-8 text-yellow-500" />
              </div>
              <div class="ml-4">
                <h3 class="text-lg font-medium text-gray-900">Click Rate</h3>
                <p class="text-2xl font-bold text-gray-900">{{ stats.clickRate }}%</p>
                <p class="text-sm text-green-600">+{{ stats.clickRateChange }}% vs avg</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Campaigns Section -->
      <div class="mt-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-medium text-gray-900">Recent Campaigns</h2>
          <div class="flex space-x-2">
            <select v-model="campaignFilter" class="rounded-md border-gray-300 shadow-sm text-sm">
              <option value="all">All Campaigns</option>
              <option value="sent">Sent</option>
              <option value="draft">Drafts</option>
              <option value="scheduled">Scheduled</option>
            </select>
          </div>
        </div>

        <div class="bg-white shadow overflow-hidden sm:rounded-md">
          <!-- Empty State for Campaigns -->
          <div v-if="filteredCampaigns.length === 0" class="text-center py-12">
            <PaperAirplaneIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No campaigns found</h3>
            <p class="mt-1 text-sm text-gray-500">
              Get started by creating your first newsletter campaign.
            </p>
          </div>

          <!-- Campaigns List -->
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="campaign in filteredCampaigns"
              :key="campaign.id"
              class="px-6 py-4 hover:bg-gray-50"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <h3 class="text-sm font-medium text-gray-900">{{ campaign.subject }}</h3>
                    <span
                      :class="[
                        'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                        getCampaignStatusClass(campaign.status)
                      ]"
                    >
                      {{ campaign.status }}
                    </span>
                  </div>
                  <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <span>{{ campaign.sent_at ? new Date(campaign.sent_at).toLocaleDateString() : 'Not sent' }}</span>
                    <span>{{ campaign.recipients }} recipients</span>
                    <span v-if="campaign.open_rate">{{ campaign.open_rate }}% opened</span>
                    <span v-if="campaign.click_rate">{{ campaign.click_rate }}% clicked</span>
                  </div>
                </div>
                <div class="ml-4 flex-shrink-0 flex space-x-2">
                  <Button @click="viewCampaign(campaign)" variant="outline" size="sm">
                    View
                  </Button>
                  <Button
                    v-if="campaign.status === 'draft'"
                    @click="editCampaign(campaign)"
                    variant="outline"
                    size="sm"
                  >
                    Edit
                  </Button>
                  <Button
                    v-if="campaign.status === 'draft'"
                    @click="sendCampaign(campaign)"
                    variant="primary"
                    size="sm"
                  >
                    Send
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subscribers Section -->
      <div class="mt-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-medium text-gray-900">Recent Subscribers</h2>
          <div class="flex space-x-2">
            <Button @click="showImportModal = true" variant="outline" size="sm">
              <ArrowDownTrayIcon class="h-4 w-4 mr-2" />
              Import
            </Button>
            <Button @click="exportSubscribers" variant="outline" size="sm">
              <ArrowUpTrayIcon class="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        <div class="bg-white shadow overflow-hidden sm:rounded-md">
          <!-- Empty State for Subscribers -->
          <div v-if="subscribers.length === 0" class="text-center py-12">
            <UsersIcon class="mx-auto h-12 w-12 text-gray-400" />
            <h3 class="mt-2 text-sm font-medium text-gray-900">No subscribers yet</h3>
            <p class="mt-1 text-sm text-gray-500">
              Start building your newsletter list by importing subscribers or collecting sign-ups.
            </p>
          </div>

          <!-- Subscribers List -->
          <div v-else class="divide-y divide-gray-200">
            <div
              v-for="subscriber in subscribers"
              :key="subscriber.id"
              class="px-6 py-4 hover:bg-gray-50"
            >
              <div class="flex items-center justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-3">
                    <h3 class="text-sm font-medium text-gray-900">{{ subscriber.email }}</h3>
                    <span
                      :class="[
                        'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                        subscriber.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      ]"
                    >
                      {{ subscriber.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                  <div class="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                    <span>Subscribed {{ new Date(subscriber.subscribed_at).toLocaleDateString() }}</span>
                    <span v-if="subscriber.first_name">{{ subscriber.first_name }} {{ subscriber.last_name }}</span>
                  </div>
                </div>
                <div class="ml-4 flex-shrink-0 flex space-x-2">
                  <Button
                    @click="toggleSubscriberStatus(subscriber)"
                    :variant="subscriber.is_active ? 'danger' : 'primary'"
                    size="sm"
                  >
                    {{ subscriber.is_active ? 'Deactivate' : 'Activate' }}
                  </Button>
                  <Button @click="removeSubscriber(subscriber)" variant="danger" size="sm">
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Campaign Modal -->
      <Modal
        :show="showCreateModal"
        @close="showCreateModal = false"
        title="Create New Campaign"
        size="lg"
      >
        <form @submit.prevent="createCampaign">
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700">Campaign Name</label>
              <input
                v-model="newCampaign.name"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Subject Line</label>
              <input
                v-model="newCampaign.subject"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Content</label>
              <textarea
                v-model="newCampaign.content"
                rows="8"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Write your newsletter content here..."
                required
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Send Options</label>
              <div class="mt-2 space-y-2">
                <label class="inline-flex items-center">
                  <input
                    v-model="newCampaign.sendOption"
                    type="radio"
                    value="now"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Send immediately</span>
                </label>
                <label class="inline-flex items-center ml-6">
                  <input
                    v-model="newCampaign.sendOption"
                    type="radio"
                    value="schedule"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Schedule for later</span>
                </label>
                <label class="inline-flex items-center ml-6">
                  <input
                    v-model="newCampaign.sendOption"
                    type="radio"
                    value="draft"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Save as draft</span>
                </label>
              </div>
            </div>

            <div v-if="newCampaign.sendOption === 'schedule'">
              <label class="block text-sm font-medium text-gray-700">Schedule Date & Time</label>
              <input
                v-model="newCampaign.scheduledAt"
                type="datetime-local"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <Button type="button" @click="showCreateModal = false" variant="outline">
              Cancel
            </Button>
            <Button type="submit" :loading="creatingCampaign">
              Create Campaign
            </Button>
          </div>
        </form>
      </Modal>

      <!-- Edit Campaign Modal -->
      <Modal
        :show="!!editingCampaign"
        @close="closeEditModal"
        title="Edit Campaign"
        size="lg"
      >
        <form v-if="editingCampaign" @submit.prevent="updateCampaign">
          <div class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-gray-700">Campaign Name</label>
              <input
                v-model="editingCampaign.name"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Subject Line</label>
              <input
                v-model="editingCampaign.subject"
                type="text"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                required
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">Content</label>
              <textarea
                v-model="editingCampaign.content"
                rows="8"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                placeholder="Write your newsletter content here..."
                required
              ></textarea>
            </div>

            <div v-if="editingCampaign.status === 'draft'">
              <label class="block text-sm font-medium text-gray-700">Send Options</label>
              <div class="mt-2 space-y-2">
                <label class="inline-flex items-center">
                  <input
                    v-model="editSendOption"
                    type="radio"
                    value="draft"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Keep as draft</span>
                </label>
                <label class="inline-flex items-center ml-6">
                  <input
                    v-model="editSendOption"
                    type="radio"
                    value="now"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Send immediately</span>
                </label>
                <label class="inline-flex items-center ml-6" v-if="editSendOption !== 'now'">
                  <input
                    v-model="editSendOption"
                    type="radio"
                    value="schedule"
                    class="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  <span class="ml-2">Schedule for later</span>
                </label>
              </div>
            </div>

            <div v-if="editSendOption === 'schedule'">
              <label class="block text-sm font-medium text-gray-700">Schedule Date & Time</label>
              <input
                v-model="editScheduledAt"
                type="datetime-local"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <Button type="button" @click="closeEditModal" variant="outline">
              Cancel
            </Button>
            <Button type="submit" :loading="updatingCampaign">
              Update Campaign
            </Button>
          </div>
        </form>
      </Modal>

      <!-- View Campaign Modal -->
      <Modal
        :show="!!selectedCampaign"
        @close="selectedCampaign = null"
        :title="selectedCampaign?.subject || 'Campaign Details'"
        size="lg"
      >
        <div v-if="selectedCampaign" class="space-y-6">
          <div class="border-b border-gray-200 pb-4">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-medium text-gray-900">{{ selectedCampaign.subject }}</h3>
              <span
                :class="[
                  'inline-flex rounded-full px-2 text-xs font-semibold leading-5',
                  getCampaignStatusClass(selectedCampaign.status)
                ]"
              >
                {{ selectedCampaign.status }}
              </span>
            </div>
            <p class="mt-2 text-sm text-gray-600">Created {{ new Date(selectedCampaign.created_at).toLocaleDateString() }}</p>
          </div>

          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">Content</h4>
            <div class="bg-gray-50 rounded-lg p-4 whitespace-pre-wrap text-sm text-gray-900 max-h-40 overflow-y-auto">
              {{ selectedCampaign.content }}
            </div>
          </div>

          <div>
            <h4 class="text-sm font-medium text-gray-700 mb-2">Campaign Statistics</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-sm text-gray-500">Recipients:</span>
                <span class="ml-2 font-medium">{{ selectedCampaign.recipients }}</span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Status:</span>
                <span class="ml-2 font-medium">{{ selectedCampaign.status }}</span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Sent:</span>
                <span class="ml-2 font-medium">
                  {{ selectedCampaign.sent_at ? new Date(selectedCampaign.sent_at).toLocaleDateString() : 'Not sent' }}
                </span>
              </div>
              <div v-if="selectedCampaign.scheduled_at">
                <span class="text-sm text-gray-500">Scheduled:</span>
                <span class="ml-2 font-medium">{{ new Date(selectedCampaign.scheduled_at).toLocaleDateString() }}</span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Open Rate:</span>
                <span class="ml-2 font-medium">{{ selectedCampaign.open_rate || 0 }}%</span>
              </div>
              <div>
                <span class="text-sm text-gray-500">Click Rate:</span>
                <span class="ml-2 font-medium">{{ selectedCampaign.click_rate || 0 }}%</span>
              </div>
            </div>
          </div>
        </div>
      </Modal>

      <!-- Import Subscribers Modal -->
      <Modal
        :show="showImportModal"
        @close="showImportModal = false"
        title="Import Subscribers"
      >
        <div class="space-y-4">
          <p class="text-sm text-gray-600">
            Upload a CSV file with email addresses. The file should have a single column with email addresses.
          </p>
          
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <ArrowDownTrayIcon class="mx-auto h-12 w-12 text-gray-400" />
            <div class="mt-4">
              <label for="file-upload" class="cursor-pointer">
                <span class="mt-2 block text-sm font-medium text-gray-900">
                  Click to upload or drag and drop
                </span>
                <input id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileUpload" accept=".csv" />
              </label>
              <p class="mt-1 text-xs text-gray-500">CSV files only</p>
            </div>
          </div>

          <div v-if="importFile" class="text-sm text-gray-600">
            Selected file: {{ importFile.name }}
          </div>

          <div class="flex justify-end space-x-3">
            <Button @click="showImportModal = false" variant="outline">
              Cancel
            </Button>
            <Button @click="importSubscribers" :loading="importing" :disabled="!importFile">
              Import
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import Button from '@/components/ui/Button.vue'
import Modal from '@/components/ui/Modal.vue'
import { useNewsletter, useNewsletterCampaigns } from '@/composables/useApi'
import { notify } from '@kyvg/vue3-notification'
import type { Subscriber } from '@/types/api'

// Define NewsletterCampaign type since it's not in the main types file
interface NewsletterCampaign {
  id: string
  name: string
  subject: string
  content: string
  status: 'draft' | 'sent' | 'scheduled'
  sent_at: string | null
  scheduled_at: string | null
  recipients: number
  open_rate: number | null
  click_rate: number | null
  created_at: string
  updated_at: string
}
import {
  PlusIcon,
  UsersIcon,
  PaperAirplaneIcon,
  CursorArrowRaysIcon,
  HandThumbUpIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
} from '@heroicons/vue/24/outline'

const { getSubscribers, getSubscriberStats, importSubscribers: apiImportSubscribers, exportSubscribers: apiExportSubscribers, updateSubscriber, deleteSubscriber } = useNewsletter()
const { getCampaigns, getCampaign, createCampaign: apiCreateCampaign, updateCampaign: apiUpdateCampaign, deleteCampaign, sendCampaign: apiSendCampaign, scheduleCampaign } = useNewsletterCampaigns()

// Stats
const stats = ref({
  totalSubscribers: 0,
  newSubscribers: 0,
  campaignsSent: 0,
  openRate: 0,
  openRateChange: 0,
  clickRate: 0,
  clickRateChange: 0,
})

// Campaigns
const campaigns = ref<NewsletterCampaign[]>([])

const campaignFilter = ref('all')
const filteredCampaigns = computed(() => {
  if (campaignFilter.value === 'all') return campaigns.value
  return campaigns.value.filter(c => c.status === campaignFilter.value)
})

// Subscribers
const subscribers = ref<Subscriber[]>([])

// Modals
const showCreateModal = ref(false)
const showImportModal = ref(false)
const creatingCampaign = ref(false)
const importing = ref(false)
const updatingCampaign = ref(false)
const importFile = ref<File | null>(null)
const selectedCampaign = ref<NewsletterCampaign | null>(null)
const editingCampaign = ref<NewsletterCampaign | null>(null)
const editSendOption = ref('draft')
const editScheduledAt = ref('')

// New Campaign Form
const newCampaign = ref({
  name: '',
  subject: '',
  content: '',
  sendOption: 'draft',
  scheduledAt: '',
})

const getCampaignStatusClass = (status: string) => {
  switch (status) {
    case 'sent':
      return 'bg-green-100 text-green-800'
    case 'draft':
      return 'bg-yellow-100 text-yellow-800'
    case 'scheduled':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const createCampaign = async () => {
  creatingCampaign.value = true
  try {
    const campaignData = {
      name: newCampaign.value.name,
      subject: newCampaign.value.subject,
      content: newCampaign.value.content,
    }

    // Create the campaign via API
    const createdCampaign = await apiCreateCampaign(campaignData) as NewsletterCampaign

    // Handle send options
    if (newCampaign.value.sendOption === 'now') {
      await apiSendCampaign(createdCampaign.id)
    } else if (newCampaign.value.sendOption === 'schedule' && newCampaign.value.scheduledAt) {
      await scheduleCampaign(createdCampaign.id, newCampaign.value.scheduledAt)
    }

    // Reload campaigns list
    await loadInitialData()

    notify({
      title: 'Success',
      text: `Campaign "${newCampaign.value.name}" created successfully!`,
      type: 'success',
    })

    showCreateModal.value = false
    resetCampaignForm()
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to create campaign',
      type: 'error',
    })
  } finally {
    creatingCampaign.value = false
  }
}

const resetCampaignForm = () => {
  newCampaign.value = {
    name: '',
    subject: '',
    content: '',
    sendOption: 'draft',
    scheduledAt: '',
  }
}

const viewCampaign = (campaign: NewsletterCampaign) => {
  selectedCampaign.value = campaign
}

const editCampaign = (campaign: NewsletterCampaign) => {
  editingCampaign.value = { ...campaign }
  editSendOption.value = campaign.status === 'draft' ? 'draft' : 'draft'
  editScheduledAt.value = campaign.scheduled_at || ''
}

const closeEditModal = () => {
  editingCampaign.value = null
  editSendOption.value = 'draft'
  editScheduledAt.value = ''
}

const updateCampaign = async () => {
  if (!editingCampaign.value) return

  updatingCampaign.value = true
  try {
    const campaignData = {
      name: editingCampaign.value.name,
      subject: editingCampaign.value.subject,
      content: editingCampaign.value.content,
    }

    // Update the campaign via API
    await apiUpdateCampaign(editingCampaign.value.id, campaignData)

    // Handle send options
    if (editSendOption.value === 'now') {
      await apiSendCampaign(editingCampaign.value.id)
    } else if (editSendOption.value === 'schedule' && editScheduledAt.value) {
      await scheduleCampaign(editingCampaign.value.id, editScheduledAt.value)
    }

    // Reload campaigns list
    await loadInitialData()

    notify({
      title: 'Success',
      text: `Campaign "${editingCampaign.value.name}" updated successfully!`,
      type: 'success',
    })

    closeEditModal()
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to update campaign',
      type: 'error',
    })
  } finally {
    updatingCampaign.value = false
  }
}

const sendCampaign = async (campaign: NewsletterCampaign) => {
  try {
    await apiSendCampaign(campaign.id)

    // Reload campaigns list to get updated data
    await loadInitialData()

    notify({
      title: 'Success',
      text: 'Campaign sent successfully!',
      type: 'success',
    })
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to send campaign',
      type: 'error',
    })
  }
}

const toggleSubscriberStatus = async (subscriber: Subscriber) => {
  const originalStatus = subscriber.is_active

  try {
    // Optimistically update the UI
    subscriber.is_active = !subscriber.is_active

    // Update subscriber status via API
    await updateSubscriber(subscriber.id, { is_active: subscriber.is_active })

    notify({
      title: 'Success',
      text: `Subscriber ${subscriber.is_active ? 'activated' : 'deactivated'}`,
      type: 'success',
    })
  } catch (error) {
    // Revert optimistic update on error
    subscriber.is_active = originalStatus

    notify({
      title: 'Error',
      text: 'Failed to update subscriber status',
      type: 'error',
    })
  }
}

const removeSubscriber = async (subscriber: Subscriber) => {
  if (!confirm(`Are you sure you want to remove ${subscriber.email}?`)) return

  const originalIndex = subscribers.value.findIndex(s => s.id === subscriber.id)
  if (originalIndex === -1) return

  // Store reference for potential restore
  const removedSubscriber = subscribers.value[originalIndex] as Subscriber

  // Optimistically remove from UI
  subscribers.value.splice(originalIndex, 1)
  stats.value.totalSubscribers = Math.max(0, stats.value.totalSubscribers - 1)

  try {
    // Delete subscriber via API
    await deleteSubscriber(subscriber.id)

    notify({
      title: 'Success',
      text: 'Subscriber removed',
      type: 'success',
    })
  } catch (error) {
    // Restore subscriber on error
    subscribers.value.splice(originalIndex, 0, removedSubscriber)
    stats.value.totalSubscribers++

    notify({
      title: 'Error',
      text: 'Failed to remove subscriber',
      type: 'error',
    })
  }
}

const handleFileUpload = (event: Event) => {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (file && file.type === 'text/csv') {
    importFile.value = file
  } else {
    notify({
      title: 'Error',
      text: 'Please select a valid CSV file',
      type: 'error',
    })
  }
}

const importSubscribers = async () => {
  if (!importFile.value) return

  importing.value = true
  try {
    const result = await apiImportSubscribers(importFile.value)

    // Reload subscribers and stats
    await loadInitialData()

    // Extract imported count from response if available
    const importedCount = (result as any)?.imported_count || 0

    notify({
      title: 'Success',
      text: importedCount > 0
        ? `Successfully imported ${importedCount} subscribers`
        : 'Subscribers imported successfully',
      type: 'success',
    })

    showImportModal.value = false
    importFile.value = null
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to import subscribers',
      type: 'error',
    })
  } finally {
    importing.value = false
  }
}

const exportSubscribers = async () => {
  try {
    const response = await apiExportSubscribers()

    // Create download link for the blob response
    const blob = response as Blob
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `subscribers-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)

    notify({
      title: 'Success',
      text: 'Subscribers exported successfully',
      type: 'success',
    })
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to export subscribers',
      type: 'error',
    })
  }
}

onMounted(async () => {
  await loadInitialData()
})

const loadInitialData = async () => {
  try {
    const loadingStates = []

    // Load campaigns with error handling
    loadingStates.push(
      getCampaigns().then((campaignsResponse) => {
        if (campaignsResponse && Array.isArray(campaignsResponse)) {
          campaigns.value = campaignsResponse as NewsletterCampaign[]
        }
      }).catch((error) => {
        console.error('Failed to load campaigns:', error)
      })
    )

    // Load subscribers with error handling
    loadingStates.push(
      getSubscribers({ page_size: 20 }).then((subscribersResponse) => {
        if (subscribersResponse && typeof subscribersResponse === 'object' && 'results' in subscribersResponse) {
          subscribers.value = subscribersResponse.results as Subscriber[]
        }
      }).catch((error) => {
        console.error('Failed to load subscribers:', error)
      })
    )

    // Load subscriber stats with error handling
    loadingStates.push(
      getSubscriberStats().then((statsResponse) => {
        if (statsResponse && typeof statsResponse === 'object') {
          const data = statsResponse as any
          stats.value.totalSubscribers = data.total_subscribers || 0
          stats.value.newSubscribers = data.new_subscribers_this_month || 0
          // Calculate or load other stats from analytics if available
          stats.value.campaignsSent = data.campaigns_sent_last_30_days || 0
          stats.value.openRate = data.average_open_rate?.toFixed(1) || 0
          stats.value.clickRate = data.average_click_rate?.toFixed(1) || 0
          stats.value.openRateChange = data.open_rate_change || 0
          stats.value.clickRateChange = data.click_rate_change || 0
        }
      }).catch((error) => {
        console.error('Failed to load subscriber stats:', error)
        // Reset stats to show no data rather than keeping placeholder values
        stats.value = {
          totalSubscribers: 0,
          newSubscribers: 0,
          campaignsSent: 0,
          openRate: 0,
          openRateChange: 0,
          clickRate: 0,
          clickRateChange: 0,
        }
      })
    )

    // Wait for all loading operations to complete
    await Promise.allSettled(loadingStates)

  } catch (error) {
    console.error('Critical error loading newsletter data:', error)
    // Ensure we don't show misleading placeholder data
    campaigns.value = []
    subscribers.value = []
    notify({
      title: 'Error',
      text: 'Failed to load newsletter data. Please refresh the page.',
      type: 'error',
    })
  }
}
</script>
