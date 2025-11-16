<template>
  <!-- Invoice History Component - Single Responsibility: Display invoice list and download functionality -->
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-semibold text-gray-900">Invoice History</h2>
        <p class="text-gray-600">View and download your billing invoices</p>
      </div>
      <button
        @click="refreshInvoices"
        :disabled="loading"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
      >
        <ArrowPathIcon
          v-if="!loading"
          class="h-4 w-4 mr-2"
        />
        <ArrowPathIcon
          v-else
          class="h-4 w-4 mr-2 animate-spin"
        />
        Refresh
      </button>
    </div>

    <!-- Invoice List -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- Loading State -->
      <div v-if="loading && invoices.length === 0" class="p-8 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading invoices...</p>
      </div>

      <!-- No Invoices State -->
      <div v-else-if="!loading && invoices.length === 0" class="p-8 text-center">
        <DocumentTextIcon class="h-12 w-12 text-gray-400 mx-auto" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">No invoices yet</h3>
        <p class="text-gray-600">Your invoices will appear here after your first billing cycle.</p>
      </div>

      <!-- Invoice Table -->
      <table v-else class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Invoice
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Amount
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th scope="col" class="relative px-6 py-3">
              <span class="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="invoice in invoices"
            :key="invoice.id"
            class="hover:bg-gray-50"
          >
            <!-- Invoice Number -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="text-sm font-medium text-gray-900">
                  {{ invoice.number || `INV-${invoice.id.slice(-8).toUpperCase()}` }}
                </div>
              </div>
            </td>

            <!-- Amount -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">
                ${{ (invoice.amount / 100).toFixed(2) }}
              </div>
              <div class="text-sm text-gray-500 uppercase">
                {{ invoice.currency }}
              </div>
            </td>

            <!-- Status -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                  invoice.status === 'open' ? 'bg-blue-100 text-blue-800' :
                  invoice.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  invoice.status === 'void' ? 'bg-red-100 text-red-800' :
                  'bg-orange-100 text-orange-800'
                ]"
              >
                {{ invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1) }}
              </span>
            </td>

            <!-- Date -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-900">
                {{ formatDate(invoice.created) }}
              </div>
              <div v-if="invoice.due_date" class="text-sm text-gray-500">
                Due {{ formatDate(invoice.due_date) }}
              </div>
            </td>

            <!-- Actions -->
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <div class="flex items-center space-x-2">
                <button
                  v-if="invoice.hosted_invoice_url"
                  @click="openInvoice(invoice.hosted_invoice_url)"
                  class="text-blue-600 hover:text-blue-900 p-1"
                  title="View Invoice"
                >
                  <EyeIcon class="h-4 w-4" />
                </button>
                <button
                  v-if="invoice.invoice_pdf"
                  @click="downloadInvoice(invoice)"
                  :disabled="downloadingInvoice === invoice.id"
                  class="text-green-600 hover:text-green-900 p-1 disabled:opacity-50"
                  title="Download PDF"
                >
                  <ArrowDownTrayIcon
                    v-if="downloadingInvoice !== invoice.id"
                    class="h-4 w-4"
                  />
                  <ArrowPathIcon
                    v-else
                    class="h-4 w-4 animate-spin"
                  />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Load More Button -->
    <div v-if="hasMoreInvoices && !loading" class="flex justify-center">
      <button
        @click="loadMoreInvoices"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
      >
        Load More Invoices
      </button>
    </div>

    <!-- Error State -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Invoice history display and management
 * - Open/Closed: Easy to extend with additional invoice actions
 * - Interface Segregation: Clean prop/emit interface
 * - Dependency Inversion: Uses composables for business logic
 */
import { ref, computed, onMounted, defineProps, defineEmits } from 'vue'
import {
  DocumentTextIcon,
  ArrowPathIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import { useBillingData } from '@/composables/useBillingData'
import type { Invoice } from '@/types/api'

// Props define the contract
interface Props {
  initialLimit?: number
  showLoadMore?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  initialLimit: 10,
  showLoadMore: true
})

// Emits define external communication interface
const emit = defineEmits<{
  'invoice-opened': [invoice: Invoice]
  'invoice-downloaded': [invoice: Invoice]
}>()

// Composable for business logic
const { invoices, invoicesLoading, loadInvoices, refreshInvoices } = useBillingData()

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)
const downloadingInvoice = ref<string | null>(null)
const currentLimit = ref(props.initialLimit)

// Computed properties
const hasMoreInvoices = computed(() => invoices.value.length >= currentLimit.value)

// Methods
const loadMoreInvoices = async () => {
  currentLimit.value += props.initialLimit
  loading.value = true
  error.value = null

  try {
    await loadInvoices(currentLimit.value)
  } catch (err: any) {
    error.value = err?.message || 'Failed to load more invoices'
  } finally {
    loading.value = false
  }
}

const refreshInvoicesLocal = async () => {
  loading.value = true
  error.value = null

  try {
    await refreshInvoices()
    currentLimit.value = Math.max(currentLimit.value, invoices.value.length)
  } catch (err: any) {
    error.value = err?.message || 'Failed to refresh invoices'
  } finally {
    loading.value = false
  }
}

const formatDate = (timestamp: number): string => {
  return new Date(timestamp * 1000).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const openInvoice = (url: string) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const downloadInvoice = async (invoice: Invoice) => {
  if (!invoice.invoice_pdf || downloadingInvoice.value === invoice.id) return

  downloadingInvoice.value = invoice.id

  try {
    // Create a temporary link element for download
    const link = document.createElement('a')
    link.href = invoice.invoice_pdf
    link.download = `invoice-${invoice.number || invoice.id}.pdf`
    link.target = '_blank'

    // Trigger download
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Emit download event
    emit('invoice-downloaded', invoice)
  } catch (err: any) {
    error.value = 'Failed to download invoice'
    console.error('Error downloading invoice:', err)
  } finally {
    downloadingInvoice.value = null
  }
}

// Initialize component
onMounted(() => {
  loadInvoices(props.initialLimit)
})
</script>
