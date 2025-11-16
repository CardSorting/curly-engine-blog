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
  BarElement,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration,
} from 'chart.js'

Chart.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface Props {
  data: Array<{ name: string; value: number }>
}

const props = defineProps<Props>()
const chartCanvas = ref<HTMLCanvasElement>()
let chartInstance: Chart | null = null

const createChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return

  const config: ChartConfiguration = {
    type: 'bar',
    data: {
      labels: props.data.map(d => d.name),
      datasets: [
        {
          label: 'Articles',
          data: props.data.map(d => d.value),
          backgroundColor: 'rgba(99, 102, 241, 0.8)',
          borderColor: 'rgb(99, 102, 241)',
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              return `Articles: ${context.parsed.y}`
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
        },
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1,
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
