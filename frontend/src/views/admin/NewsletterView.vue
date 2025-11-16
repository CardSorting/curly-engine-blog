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
          <div class="divide-y divide-gray-200">
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
          <div class="divide-y divide-gray-200">
            <div
              v-for="subscriber in recentSubscribers"
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
                    <span>Subscribed {{ new Date(subscriber.created_at).toLocaleDateString() }}</span>
                    <span v-if="subscriber.name">{{ subscriber.name }}</span>
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
import {
  PlusIcon,
  UsersIcon,
  PaperAirplaneIcon,
  CursorArrowRaysIcon,
  HandThumbUpIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
} from '@heroicons/vue/24/outline'

const { subscribe } = useNewsletter()

// Stats
const stats = ref({
  totalSubscribers: 1250,
  newSubscribers: 45,
  campaignsSent: 8,
  openRate: 32.5,
  openRateChange: 2.3,
  clickRate: 4.2,
  clickRateChange: 0.8,
})

// Campaigns
const campaigns = ref([
  {
    id: '1',
    name: 'Weekly Digest',
    subject: 'This Week in Tech: Latest Updates',
    status: 'sent',
    sent_at: '2024-01-15T10:00:00Z',
    recipients: 1250,
    open_rate: 35.2,
    click_rate: 4.8,
  },
  {
    id: '2',
    name: 'Product Launch',
    subject: 'Introducing Our New Features!',
    status: 'draft',
    sent_at: null,
    recipients: 0,
    open_rate: 0,
    click_rate: 0,
  },
  {
    id: '3',
    name: 'Monthly Newsletter',
    subject: 'January 2024 Newsletter',
    status: 'scheduled',
    sent_at: '2024-01-20T09:00:00Z',
    recipients: 1250,
    open_rate: 0,
    click_rate: 0,
  },
])

const campaignFilter = ref('all')
const filteredCampaigns = computed(() => {
  if (campaignFilter.value === 'all') return campaigns.value
  return campaigns.value.filter(c => c.status === campaignFilter.value)
})

// Subscribers
const recentSubscribers = ref([
  {
    id: '1',
    email: 'john@example.com',
    name: 'John Doe',
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    email: 'jane@example.com',
    name: 'Jane Smith',
    is_active: true,
    created_at: '2024-01-14T15:30:00Z',
  },
  {
    id: '3',
    email: 'inactive@example.com',
    name: null,
    is_active: false,
    created_at: '2024-01-10T08:00:00Z',
  },
])

// Modals
const showCreateModal = ref(false)
const showImportModal = ref(false)
const creatingCampaign = ref(false)
const importing = ref(false)
const importFile = ref<File | null>(null)

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
    // Mock API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    const campaign = {
      id: Date.now().toString(),
      name: newCampaign.value.name,
      subject: newCampaign.value.subject,
      status: newCampaign.value.sendOption === 'draft' ? 'draft' : 'sent',
      sent_at: newCampaign.value.sendOption === 'now' ? new Date().toISOString() : null,
      recipients: newCampaign.value.sendOption === 'draft' ? 0 : stats.value.totalSubscribers,
      open_rate: 0,
      click_rate: 0,
    }
    
    campaigns.value.unshift(campaign)
    
    notify({
      title: 'Success',
      text: `Campaign "${campaign.name}" created successfully!`,
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

const viewCampaign = (campaign: any) => {
  console.log('View campaign:', campaign)
}

const editCampaign = (campaign: any) => {
  console.log('Edit campaign:', campaign)
}

const sendCampaign = async (campaign: any) => {
  try {
    campaign.status = 'sent'
    campaign.sent_at = new Date().toISOString()
    campaign.recipients = stats.value.totalSubscribers
    
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

const toggleSubscriberStatus = async (subscriber: any) => {
  try {
    subscriber.is_active = !subscriber.is_active
    notify({
      title: 'Success',
      text: `Subscriber ${subscriber.is_active ? 'activated' : 'deactivated'}`,
      type: 'success',
    })
  } catch (error) {
    notify({
      title: 'Error',
      text: 'Failed to update subscriber',
      type: 'error',
    })
  }
}

const removeSubscriber = async (subscriber: any) => {
  if (!confirm(`Are you sure you want to remove ${subscriber.email}?`)) return
  
  try {
    const index = recentSubscribers.value.findIndex(s => s.id === subscriber.id)
    if (index > -1) {
      recentSubscribers.value.splice(index, 1)
      stats.value.totalSubscribers--
    }
    
    notify({
      title: 'Success',
      text: 'Subscriber removed',
      type: 'success',
    })
  } catch (error) {
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
    // Mock import process
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Simulate importing 10 new subscribers
    const newCount = 10
    stats.value.totalSubscribers += newCount
    stats.value.newSubscribers += newCount
    
    notify({
      title: 'Success',
      text: `Successfully imported ${newCount} subscribers`,
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

const exportSubscribers = () => {
  const data = recentSubscribers.value.map(sub => ({
    email: sub.email,
    name: sub.name || '',
    status: sub.is_active ? 'Active' : 'Inactive',
    created_at: sub.created_at,
  }))
  
  if (data.length === 0) {
    console.warn('No subscribers to export')
    return
  }
  
  const csv = [
    Object.keys(data[0] || {}).join(','),
    ...data.map(row => Object.values(row).map(v => `"${v}"`).join(','))
  ].join('\n')
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `subscribers-${new Date().toISOString().split('T')[0]}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  // Load initial data
})
</script>
