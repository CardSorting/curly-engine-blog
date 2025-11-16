<template>
  <div class="relative h-64">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration,
} from 'chart.js'

Chart.register(CategoryScale, LinearScale, ArcElement, Title, Tooltip, Legend)

interface Props {
  data: Array<{ name: string; value: number; color: string }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const config: ChartConfiguration = {
    type: 'doughnut',
    data: {
      labels: props.data.map(d => d.name),
      datasets: [
        {
          data: props.data.map(d => d.value),
          backgroundColor: props.data.map(d => d.color),
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 15,
            usePointStyle: true,
          },
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.parsed
              const total = context.dataset.data.reduce((sum: number, val: any) => sum + val, 0)
              const percentage = ((value / total) * 100).toFixed(1)
              return `${label}: ${value} (${percentage}%)`
            },
          },
        },
      },
    },
  }

  if (chartInstance) {
    chartInstance.destroy()
  }
  chartInstance = new Chart(ctx, config)
}

watch(() => props.data, () => {
  nextTick(() => {
    createChart()
  })
}, { deep: true })

onMounted(() => {
  nextTick(() => {
    createChart()
  })
})
</script>
