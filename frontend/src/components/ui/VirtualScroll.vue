<template>
  <div
    ref="container"
    class="virtual-scroll-container"
    :style="{ height: containerHeight }"
    @scroll="handleScroll"
  >
    <div
      class="virtual-scroll-content"
      :style="{ height: totalHeight }"
    >
      <div
        v-for="(item, index) in visibleItems"
        :key="getItemKey(item, visibleStartIndex + index)"
        class="virtual-scroll-item"
        :style="{ transform: `translateY(${visibleStartIndex * itemHeight}px)` }"
      >
        <slot :item="item" :index="visibleStartIndex + index" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
  containerHeight?: string
  bufferSize?: number
  getKey?: (item: any) => string | number
}

const props = withDefaults(defineProps<Props>(), {
  containerHeight: '400px',
  bufferSize: 5,
  getKey: (item: any) => item.id || item
})

const container = ref<HTMLElement>()
const scrollTop = ref(0)

// Calculated values
const totalItems = computed(() => props.items.length)
const totalHeight = computed(() => totalItems.value * props.itemHeight)

// Visible range calculation
const visibleStartIndex = computed(() => {
  const start = Math.floor(scrollTop.value / props.itemHeight) - props.bufferSize
  return Math.max(0, start)
})

const visibleEndIndex = computed(() => {
  const containerHeight = container.value?.clientHeight || 400
  const end = Math.ceil((scrollTop.value + containerHeight) / props.itemHeight) + props.bufferSize
  return Math.min(totalItems.value - 1, end)
})

const visibleItems = computed(() => {
  return props.items.slice(visibleStartIndex.value, visibleEndIndex.value + 1)
})

// Methods
const handleScroll = (event: Event) => {
  const target = event.target as HTMLElement
  scrollTop.value = target.scrollTop
}

const getItemKey = (item: any, index: number) => {
  try {
    return props.getKey(item)
  } catch {
    return index
  }
}

// Scroll to specific item
const scrollToItem = (index: number) => {
  if (!container.value) return
  const targetScrollTop = index * props.itemHeight
  container.value.scrollTo({ top: targetScrollTop, behavior: 'smooth' })
}

// Scroll to specific position
const scrollToPosition = (position: number) => {
  if (!container.value) return
  container.value.scrollTo({ top: position, behavior: 'smooth' })
}

// Expose methods for parent components
defineExpose({
  scrollToItem,
  scrollToPosition,
  getItemKey
})
</script>

<style scoped>
.virtual-scroll-container {
  overflow: auto;
}

.virtual-scroll-content {
  position: relative;
}

.virtual-scroll-item {
  position: absolute;
  left: 0;
  right: 0;
  will-change: transform;
}
</style>
