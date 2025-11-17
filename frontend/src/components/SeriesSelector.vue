<template>
  <div class="series-selector">
    <div class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Content Series
      </label>
      <select
        v-model="selectedSeriesId"
        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        @change="handleSeriesChange"
      >
        <option value="">No series</option>
        <option
          v-for="series in series"
          :key="series.id"
          :value="series.id"
        >
          {{ series.title }}
        </option>
      </select>
    </div>

    <!-- Series Info -->
    <div v-if="selectedSeries" class="bg-blue-50 border border-blue-200 rounded p-3 mb-4">
      <h4 class="font-medium text-blue-900 mb-1">{{ selectedSeries.title }}</h4>
      <p class="text-sm text-blue-700 mb-2">{{ selectedSeries.description }}</p>
      <p class="text-xs text-blue-600">{{ selectedSeries.article_count }} articles in this series</p>
    </div>

    <!-- Series Order (if assigned to series) -->
    <div v-if="selectedSeriesId && selectedSeriesOrder !== undefined" class="mb-4">
      <label class="block text-sm font-medium text-gray-700 mb-2">
        Order in Series
      </label>
      <input
        v-model.number="selectedSeriesOrder"
        type="number"
        min="0"
        class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        @change="handleOrderChange"
      />
      <p class="text-xs text-gray-500 mt-1">
        The position of this article within the series (0 = first)
      </p>
    </div>

    <!-- Quick Series Creation -->
    <div class="border-t pt-4">
      <p class="text-sm text-gray-600 mb-2">Don't see your series?</p>
      <button
        @click="$emit('openSeriesManager')"
        class="text-blue-600 hover:text-blue-800 text-sm underline"
      >
        Manage Series →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useSeries, type Series } from '@/composables/useSeries'
import { useNotification } from '@kyvg/vue3-notification'

interface Props {
  modelValue?: string // series ID
  seriesOrder?: number
  articleId?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'update:seriesOrder', value: number): void
  (e: 'openSeriesManager'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  seriesOrder: 0
})

const emit = defineEmits<Emits>()

const { series, fetchSeries, assignArticleToSeries, removeArticleFromSeries } = useSeries()

// State
const selectedSeriesId = ref(props.modelValue)
const selectedSeriesOrder = ref(props.seriesOrder)

// Computed
const selectedSeries = computed(() => {
  return series.value.find(s => s.id === selectedSeriesId.value) || null
})

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  selectedSeriesId.value = newValue
})

watch(() => props.seriesOrder, (newValue) => {
  selectedSeriesOrder.value = newValue
})

// Methods
const handleSeriesChange = async () => {
  if (!props.articleId) {
    // Just emit the change for parent to handle
    emit('update:modelValue', selectedSeriesId.value)
    if (!selectedSeriesId.value) {
      emit('update:seriesOrder', 0)
    }
    return
  }

  try {
    if (!selectedSeriesId.value) {
      // Remove from series
      await removeArticleFromSeries(props.articleId)
      emit('update:modelValue', '')
      emit('update:seriesOrder', 0)
    } else {
      // Add to series with default order
      await assignArticleToSeries(props.articleId, selectedSeriesId.value)
      emit('update:modelValue', selectedSeriesId.value)
      // Order will be set by the backend
    }
  } catch (error) {
    // Revert selection on error
    selectedSeriesId.value = props.modelValue
  }
}

const handleOrderChange = async () => {
  if (!props.articleId || !selectedSeriesId.value) return

  try {
    await assignArticleToSeries(props.articleId, selectedSeriesId.value, selectedSeriesOrder.value)
    emit('update:seriesOrder', selectedSeriesOrder.value)
  } catch (error) {
    // Revert order on error
    selectedSeriesOrder.value = props.seriesOrder
  }
}

// Load series on mount
onMounted(() => {
  fetchSeries()
})
</script>

<style scoped>
</style>
