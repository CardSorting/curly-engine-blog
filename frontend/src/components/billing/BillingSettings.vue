<template>
  <!-- Billing Settings Component - Single Responsibility: Manage billing settings and preferences -->
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-xl font-semibold text-gray-900">Billing Settings</h2>
      <p class="text-gray-600">Manage your billing preferences and payment methods</p>
    </div>

    <!-- Payment Methods Section -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-medium text-gray-900">Payment Methods</h3>
        <button
          @click="showAddPayment = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Payment Method
        </button>
      </div>

      <!-- Payment Methods List -->
      <div v-if="paymentMethods.length > 0" class="space-y-4">
        <div
          v-for="method in paymentMethods"
          :key="method.id"
          :class="[
            'flex items-center justify-between p-4 border rounded-lg',
            method.type === 'card' ? 'border-gray-200' : 'border-gray-200'
          ]"
        >
          <!-- Payment Method Info -->
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <CreditCardIcon class="h-6 w-6 text-gray-400" />
            </div>
            <div class="ml-4">
              <div class="text-sm font-medium text-gray-900">
                {{ getPaymentMethodDisplay(method) }}
              </div>
              <div class="text-sm text-gray-500">
                {{ method.billing_details?.name || 'No name provided' }}
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="flex items-center space-x-2">
            <!-- Set as Default -->
            <button
              @click="setDefaultPaymentMethod(method.id)"
              class="text-sm text-blue-600 hover:text-blue-500"
            >
              Set Default
            </button>

            <!-- Remove -->
            <button
              @click="removePaymentMethod(method.id)"
              class="text-sm text-red-600 hover:text-red-500"
            >
              Remove
            </button>
          </div>
        </div>
      </div>

      <!-- No Payment Methods -->
      <div v-else class="text-center py-8">
        <CreditCardIcon class="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">No Payment Methods</h3>
        <p class="text-gray-600 mb-4">Add a payment method to manage your billing.</p>
        <button
          @click="showAddPayment = true"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
        >
          <PlusIcon class="h-4 w-4 mr-2" />
          Add Payment Method
        </button>
      </div>
    </div>

    <!-- Billing Address Section -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg font-medium text-gray-900">Billing Address</h3>
        <button
          @click="editingAddress = !editingAddress"
          :class="[
            'inline-flex items-center px-4 py-2 border text-sm font-medium rounded-md',
            editingAddress
              ? 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
              : 'border-transparent text-white bg-blue-600 hover:bg-blue-700'
          ]"
        >
          <PencilIcon class="h-4 w-4 mr-2" />
          {{ editingAddress ? 'Cancel' : 'Edit Address' }}
        </button>
      </div>

      <!-- Address Display -->
      <div v-if="!editingAddress" class="text-sm text-gray-600">
        <div v-if="billingAddress.name" class="font-medium text-gray-900 mb-2">{{ billingAddress.name }}</div>
        <div>{{ billingAddress.line1 }}</div>
        <div v-if="billingAddress.line2">{{ billingAddress.line2 }}</div>
        <div>{{ billingAddress.city }}, {{ billingAddress.state }} {{ billingAddress.postal_code }}</div>
        <div>{{ billingAddress.country }}</div>
        <div v-if="billingAddress.phone" class="mt-2">{{ billingAddress.phone }}</div>
      </div>

      <!-- Address Form -->
      <form v-else @submit.prevent="saveBillingAddress" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Full Name</label>
            <input
              v-model="addressForm.name"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Phone</label>
            <input
              v-model="addressForm.phone"
              type="tel"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Address Line 1</label>
          <input
            v-model="addressForm.line1"
            type="text"
            required
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Address Line 2</label>
          <input
            v-model="addressForm.line2"
            type="text"
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">City</label>
            <input
              v-model="addressForm.city"
              type="text"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">State/Province</label>
            <input
              v-model="addressForm.state"
              type="text"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">ZIP/Postal Code</label>
            <input
              v-model="addressForm.postal_code"
              type="text"
              required
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Country</label>
          <select
            v-model="addressForm.country"
            required
            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="US">United States</option>
            <option value="CA">Canada</option>
            <option value="GB">United Kingdom</option>
          </select>
        </div>

        <div class="flex items-center justify-end space-x-3">
          <button
            type="button"
            @click="editingAddress = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="savingAddress"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {{ savingAddress ? 'Saving...' : 'Save Address' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Billing Preferences Section -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 mb-6">Billing Preferences</h3>

      <div class="space-y-4">
        <!-- Email Notifications -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Email Notifications</h4>
            <p class="text-sm text-gray-500">Receive billing-related email notifications</p>
          </div>
          <input
            v-model="billingPreferences.emailNotifications"
            @change="updateBillingPreference('email_notifications', ($event.target as HTMLInputElement).checked)"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <!-- SMS Notifications -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">SMS Notifications</h4>
            <p class="text-sm text-gray-500">Receive billing-related SMS notifications</p>
          </div>
          <input
            v-model="billingPreferences.smsNotifications"
            @change="updateBillingPreference('sms_notifications', ($event.target as HTMLInputElement).checked)"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>

        <!-- Invoice Delivery -->
        <div class="flex items-center justify-between">
          <div>
            <h4 class="text-sm font-medium text-gray-900">Automatic Invoice Delivery</h4>
            <p class="text-sm text-gray-500">Automatically email invoices when they are generated</p>
          </div>
          <input
            v-model="billingPreferences.autoInvoiceDelivery"
            @change="updateBillingPreference('auto_invoice_delivery', ($event.target as HTMLInputElement).checked)"
            type="checkbox"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div v-if="loading" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
    </div>

    <!-- Error Display -->
    <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex">
        <ExclamationTriangleIcon class="h-5 w-5 text-red-400" />
        <div class="ml-3">
          <p class="text-sm text-red-800">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <!-- Add Payment Method Modal (placeholder for now) -->
    <div v-if="showAddPayment" class="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">Add Payment Method</h3>
          <button @click="showAddPayment = false" class="text-gray-400 hover:text-gray-600">
            <XMarkIcon class="h-6 w-6" />
          </button>
        </div>
        <p class="text-gray-600 mb-4">Payment method integration would be implemented here using Stripe Elements or similar.</p>
        <div class="flex justify-end">
          <button
            @click="showAddPayment = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SOLID Principles Applied:
 * - Single Responsibility: Billing settings management and preferences
 * - Open/Closed: Easy to extend with additional settings
 * - Interface Segregation: Clean prop/emit interface
 * - Dependency Inversion: Uses composables for business logic
 */
import { ref, onMounted, defineProps, defineEmits } from 'vue'
import {
  CreditCardIcon,
  PlusIcon,
  PencilIcon,
  ExclamationTriangleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import { useBillingData } from '@/composables/useBillingData'
import type { PaymentMethod } from '@/types/api'

// Props define the contract
interface Props {
  accountId?: string
}

const props = withDefaults(defineProps<Props>(), {
  accountId: ''
})

// Emits define external communication interface
const emit = defineEmits<{
  'settings-updated': [settings: any]
  'payment-method-added': [method: PaymentMethod]
  'payment-method-removed': [methodId: string]
}>()

// Composables for business logic
const { paymentMethods, loadPaymentMethods } = useBillingData()

// Reactive state
const loading = ref(false)
const error = ref<string | null>(null)

const editingAddress = ref(false)
const savingAddress = ref(false)
const showAddPayment = ref(false)

// Billing address data
const billingAddress = ref({
  name: '',
  line1: '',
  line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'US',
  phone: ''
})

const addressForm = ref({
  name: '',
  line1: '',
  line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'US',
  phone: ''
})

// Billing preferences
const billingPreferences = ref({
  emailNotifications: true,
  smsNotifications: false,
  autoInvoiceDelivery: true
})

// Methods
const getPaymentMethodDisplay = (method: PaymentMethod): string => {
  if (method.type !== 'card') return 'Unknown Payment Method'

  const card = method.card!
  const brand = card.brand.charAt(0).toUpperCase() + card.brand.slice(1)
  return `${brand} ending in ${card.last4}`
}

const setDefaultPaymentMethod = async (methodId: string) => {
  // TODO: Implement set default payment method
  console.log('Setting default payment method:', methodId)
  // This would typically call an API endpoint
}

const removePaymentMethod = async (methodId: string) => {
  if (!confirm('Are you sure you want to remove this payment method?')) return

  loading.value = true
  error.value = null

  try {
    // TODO: Implement remove payment method API call
    console.log('Removing payment method:', methodId)
    emit('payment-method-removed', methodId)

    // Refresh payment methods
    await loadPaymentMethods()
  } catch (err: any) {
    error.value = err?.message || 'Failed to remove payment method'
  } finally {
    loading.value = false
  }
}

const saveBillingAddress = async () => {
  savingAddress.value = true
  error.value = null

  try {
    // TODO: Implement save billing address API call
    console.log('Saving billing address:', addressForm.value)

    // Update local billing address object
    Object.assign(billingAddress.value, addressForm.value)

    editingAddress.value = false
    emit('settings-updated', { address: billingAddress.value })
  } catch (err: any) {
    error.value = err?.message || 'Failed to save billing address'
  } finally {
    savingAddress.value = false
  }
}

const updateBillingPreference = async (key: string, value: boolean) => {
  try {
    // TODO: Implement update billing preference API call
    console.log('Updating billing preference:', key, value)

    // Update local preferences
    if (key === 'email_notifications') billingPreferences.value.emailNotifications = value
    else if (key === 'sms_notifications') billingPreferences.value.smsNotifications = value
    else if (key === 'auto_invoice_delivery') billingPreferences.value.autoInvoiceDelivery = value

    emit('settings-updated', { preferences: billingPreferences.value })
  } catch (err: any) {
    error.value = err?.message || 'Failed to update preference'
  }
}

// Initialize component
onMounted(() => {
  loadPaymentMethods()

  // TODO: Load billing address and preferences from API
  // For now, using placeholder data
  billingAddress.value = {
    name: 'John Doe',
    line1: '123 Main St',
    line2: '',
    city: 'Anytown',
    state: 'CA',
    postal_code: '12345',
    country: 'US',
    phone: '+1 (555) 123-4567'
  }

  addressForm.value = { ...billingAddress.value }
})
</script>
